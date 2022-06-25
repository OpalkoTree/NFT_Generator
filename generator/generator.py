import os
import random
import json
import requests
import asyncio
import aiofiles
from io import BytesIO
from math import prod
from typing import List
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

from backend.settings import MEDIA_ROOT
from .models import Collection
from .serializers import CollectionMetaSerializer


class Generator():

    @staticmethod
    def pinata_upload(file_name: str, file: BytesIO) -> dict:
        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"

        payload = {
            'pinataOptions': json.dumps({ 'cidVersion': 1 }),
            'pinataMetadata': json.dumps({ 'name': file_name })
            }

        files = [('file', (file_name, file.getvalue(), 'application/octet-stream'))]

        headers = {
            'pinata_api_key': Generator.api_key,
            'pinata_secret_api_key': Generator.secret_api_key
            }

        response = requests.request('POST', url, headers=headers, data=payload, files=files)

        return json.loads(response.text)

    @classmethod
    def generate_meta(cls, iter: int, collection: dict, attributes: List[dict], cid: dict) -> None:
        collection |= {
            'name': f'{ collection["name"] }#{ iter }',
            'image_url': f'https://gateway.pinata.cloud/ipfs/{ cid["IpfsHash"] }',
            'image_count': f'{ iter }/{ collection["image_count"] }',
            'attributes': attributes
            }

        tempFile = BytesIO()
        tempFile.write(json.dumps(collection, indent=4).encode('utf-8'))
        cls.pinata_upload(f'{ iter }.json', tempFile)
        tempFile.close()

    @staticmethod
    def paste_image(first_layer: Image, new_layer: Image) -> Image:
        first_layer.paste(new_layer, (0,0), new_layer)
        return first_layer

    @classmethod
    def generate_token(cls, iter: int, combination: dict) -> tuple:
        first_layer = Image.new(mode='RGBA', size=(1500,1500))
        tempFile = BytesIO()
        attributes = []

        for layer, attribute in list(combination.items()):
            new_layer = Image.open(os.path.join(MEDIA_ROOT, attribute)).convert('RGBA')
            result = cls.paste_image(first_layer, new_layer)
            attributes.append({ 'trait_type': layer, 'value': attribute })

        result.convert('RGB').save(tempFile, 'JPEG', optimize=True)
        cid = cls.pinata_upload(f'{ iter }.jpg', tempFile)
        tempFile.close()

        return cid, attributes
        
    @classmethod
    async def generate_tokens(cls, loop, combinations: List[dict], collection: dict) -> dict:
        with ThreadPoolExecutor(max_workers=os.cpu_count()*4) as executor:
            for iter, combination in enumerate(combinations, 1):
                cid, attribute_list = await loop.run_in_executor(executor, cls.generate_token, iter, combination)
                await loop.run_in_executor(executor, cls.generate_meta, iter, collection, attribute_list, cid)

            return { 'success': True, 'message': 'Generation completed' }

    @classmethod
    def generate_combinations(cls, traits: dict, kwargs: dict) -> dict:
        cls.api_key, cls.secret_api_key = kwargs['api_key'], kwargs['secret_api_key']
        collection = CollectionMetaSerializer(Collection.objects.get(pk=kwargs['id'])).data
        attributes_count = prod([len(value) for value in traits.values()])
        completed_combinations = []

        if collection['image_count'] > attributes_count:
            return { 'success': False, 'message': 'Expected number of generations, less than possible' }

        while True:
            combination = {}

            for layer, attributes in traits.items():
                ## if u need generation by chance
                image_list, chance_list = zip(*[(k,v) for attribute in attributes for k,v in attribute.items()])
                combination |= { layer: random.choices(image_list, chance_list)[0] }

                ##  if u need generation in percentage terms
                # attributes = sum([[k]*int(v*collection['image_count']/100) for attr in attributes for k,v in attr.items()], [])

                # for attribute in random.sample(attributes, collection['image_count']):
                    # combination |= { layer: attribute }
                
            if combination not in completed_combinations:
                completed_combinations.append(combination)
            
            if len(completed_combinations) == collection['image_count']:
                break

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(cls.generate_tokens(loop, completed_combinations, collection))
        loop.close()

        return result

# TODO: сделать рефактор