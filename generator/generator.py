import os
import random
import json
import asyncio
import aiofiles
from math import prod
from typing import List
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

from backend.settings import MEDIA_ROOT
from .models import Collection
from .serializers import CollectionMetaSerializer


class Generator():

    @staticmethod
    async def generate_meta(iter: int, collection: dict, attributes: List[dict]) -> None:
        collection |= {
            'name': f'{collection["name"]}#{iter}',
            'image_url': f'{iter}.jpg',
            'image_count': f'{iter}/{collection["image_count"]}',
            'attributes': attributes
        }

        async with aiofiles.open( os.path.join('output/', f'{iter}.json'), 'w') as file: 
            await json.dump(collection, file, indent=4)

    @staticmethod
    def paste_image(first_layer: Image, new_layer: Image) -> Image:
        first_layer.paste(new_layer, (0,0), new_layer)
        return first_layer

    @classmethod
    def generate_token(cls, iter: int, combination: dict) -> List[dict]:
        first_layer = Image.open(os.path.join(MEDIA_ROOT, list(combination.values())[0]))
        attributes = []

        for layer, attribute in list(combination.items())[1:]:
            result = cls.paste_image(first_layer, Image.open(os.path.join(MEDIA_ROOT, attribute)).convert('RGBA'))
            attributes.append({'trait_type': layer, 'value': attribute})

        result.convert('RGB').save(os.path.join('output/', f'{iter}.jpg'), 'JPEG', optimize=True)

        return attributes
        
    @classmethod
    async def generate_tokens(cls, loop, combinations: List[dict], collection: dict) -> dict:
        with ThreadPoolExecutor(max_workers=os.cpu_count()*4) as executor:
            for iter, combination in enumerate(combinations, 1):
                # attribute_list = executor.submit(cls.generate_token, iter, combination)
                # executor.submit(cls.generate_meta, iter, collection, attribute_list.result())

                attribute_list = await loop.run_in_executor(executor, cls.generate_token, iter, combination)
                await loop.run_in_executor(executor, cls.generate_meta, iter, collection, attribute_list)

            return {'success': True, 'message': 'Generation completed'}

    @classmethod
    def generate_combinations(cls, traits: dict, id: int) -> dict:
        collection = CollectionMetaSerializer(Collection.objects.get(pk=id)).data
        attributes_count = [len(value) for value in traits.values()]
        completed_combinations = []

        if collection['image_count'] > prod(attributes_count):
            return {'success': False, 'message': 'Expected number of generations, less than possible'}

        #  if u need generation by chance

        # while True:
        #     combination = {}

        #     for layer, attributes in traits.items():
        #         image_list, chance_list = zip(*[(k,v) for attribute in attributes for k,v in attribute.items()])
        #         image = random.choices(image_list, chance_list)
        #         combination[layer] = image[0]
                
        #     if combination not in completed_combinations:
        #         completed_combinations.append(combination)
            
        #     if len(completed_combinations) == collection['image_count']:
        #         break

        #  if u need generation in percentage terms

        for _ in range(collection['image_count']):
            combination = {}
            
            for layer, attributes in traits.items():
                attributes = [k for attr in attributes for k,v in attr.items() for _ in range(int(v*collection['image_count']/100))]

                for attribute in random.sample(attributes, collection['image_count']):
                    combination |= {layer: attribute}

            completed_combinations.append(combination)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(cls.generate_tokens(loop, completed_combinations, collection))
        loop.close()

        return result


# TODO: внедрить pinata API
# TODO: добавить поле ключем от pinata API в бд, и брать его для внедрения