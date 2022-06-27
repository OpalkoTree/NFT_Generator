import os
import random
import json
import requests
import asyncio
import aiofiles
from io import BytesIO
from math import prod, ceil
from typing import List
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

from backend.settings import MEDIA_ROOT
from .models import Collection
from .serializers import CollectionMetaSerializer
from .dataclass import Token

from sys import getsizeof

class Generator():

    @staticmethod
    def pinata_upload(pin_name: str, tokens: List[tuple]) -> dict:
        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"

        payload = {
            'pinataOptions': json.dumps({ 'cidVersion': 1, 'wrapWithDirectory': True }),
            'pinataMetadata': json.dumps({ 'name': pin_name })
            }

        if not tokens[0].is_generated:
            files = [('file', (f'images/{ token.name.split("#")[1] }.jpg', token.image)) for token in tokens]
        else:
            files = [('file', (f'jsons/{ token.name.split("#")[1] }.json', token.to_json())) for token in tokens]

        headers = {
            'pinata_api_key': Generator.api_key,
            'pinata_secret_api_key': Generator.secret_api_key
            }

        response = requests.request('POST', url, headers=headers, data=payload, files=files)

        return json.loads(response.text)

    @staticmethod
    def paste_image(first_layer: Image, new_layer: Image) -> Image:
        first_layer.paste(new_layer, (0,0), new_layer)
        return first_layer

    @classmethod
    def generate_token(cls, iter: int, combination: dict, collection: dict) -> tuple:
        first_layer = Image.new(mode='RGBA', size=(1500,1500))
        attributes = []

        for layer, attribute in list(combination.items()):
            new_layer = Image.open(os.path.join(MEDIA_ROOT, attribute)).convert('RGBA')
            result = cls.paste_image(first_layer, new_layer)
            attributes.append({ 'trait_type': layer, 'value': attribute })

        with BytesIO() as tempFile:
            result.convert('RGB').save(tempFile, 'JPEG', optimize=True)

            collection = collection | {
                'name': f'{ collection["name"] }#{ iter }',
                'image': tempFile.getvalue(),
                'series': f'{ iter }/{ collection["series"] }',
                'attributes': attributes,
            }

        return Token(**collection)
        
    @classmethod
    async def generate_tokens(cls, loop, combinations: List[dict], collection: dict) -> dict:
        with ThreadPoolExecutor(max_workers=os.cpu_count()*4) as executor:
            tokens_array = []

            for iter, combination in enumerate(combinations, 1):
                tokens_array.append(await loop.run_in_executor(executor, cls.generate_token, iter, combination, collection))

            img_cid = cls.pinata_upload(f'{collection["collection_name"]}_img', tokens_array)

            [token.replace_image(img_cid) for token in tokens_array]

            meta_cid = cls.pinata_upload(f'{collection["collection_name"]}_json', tokens_array)

        return { 'success': True, 'message': 'Generation completed', 'images': img_cid, 'meta': meta_cid }

    @classmethod
    def generate_combinations(cls, traits: dict, kwargs: dict) -> dict:
        cls.api_key, cls.secret_api_key = kwargs['api_key'], kwargs['secret_api_key']
        collection = CollectionMetaSerializer(Collection.objects.get(pk=kwargs['id'])).data
        attributes_count = prod([len(value) for value in traits.values()])
        completed_combinations = []

        if collection['series'] > attributes_count:
            return { 'success': False, 'message': 'Expected number of generations, less than possible' }
        
        while True:
            combination = {}

            for layer, attributes in traits.items():
                ## if u need generation by chance
                # image_list, chance_list = zip(*[(k,v) for attribute in attributes for k,v in attribute.items()])
                # combination |= { layer: random.choices(image_list, chance_list)[0] }

                ##  if u need generation in percentage terms
                attributes = sum([[k]*ceil(v*collection['series']/100) for attr in attributes for k,v in attr.items()], [])

                for attribute in random.sample(attributes, collection['series']):
                    combination |= { layer: attribute }

            if combination not in completed_combinations:
                completed_combinations.append(combination)
            
            if len(completed_combinations) == collection['series']:
                break

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(cls.generate_tokens(loop, completed_combinations, dict(collection)))
        loop.close()

        return result

# TODO: сделать рефактор