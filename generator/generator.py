import os
import random
import json
import asyncio
import multiprocessing
from asgiref.sync import sync_to_async
from math import prod
from typing import List
from PIL import Image
from backend.settings import MEDIA_ROOT
from generator.models import Collection
from generator.serializers import CollectionMetaSerializer


class Generator():

    @staticmethod
    def generate_meta(loop: int, collection: dict, attributes: List[dict]) -> None:
        collection |= {
            'name': f'{collection["name"]}#{loop}',
            'image_url': f'{loop}.jpg',
            'image_count': f'{loop}/{collection["image_count"]}',
            'attributes': attributes
        }

        with  open( os.path.join('output/', f'{loop}.json'), 'w') as file: 
            json.dump(collection, file, indent=4)

    @staticmethod
    def generate_token(loop: int, combination: dict) -> List[dict]:
        output = Image.open(os.path.join(MEDIA_ROOT, list(combination.values())[0]))
        attributes = []

        for layer, attribute in list(combination.items())[1:]:
            paste_attribute = Image.open(os.path.join(MEDIA_ROOT, attribute)).convert('RGBA')
            output.paste(paste_attribute, (0,0), paste_attribute)
            attributes.append({'trait_type': layer, 'value': attribute})
        
        output.convert('RGB').save(os.path.join('output/', f'{loop}.jpg'), 'JPEG', optimize=True)

        return attributes
        
    @classmethod
    def generate_tokens(cls, combinations: List[dict], collection: dict) -> dict:
        for loop, combination in enumerate(combinations, 1):
            attribute_list = cls.generate_token(loop, combination)
            cls.generate_meta(loop, collection, attribute_list)

        return {'success': True, 'message': 'Generation completed'}

    @classmethod
    def generate_combinations(cls, traits: dict, id: int) -> dict:
        collection_dict = CollectionMetaSerializer(Collection.objects.get(pk=id)).data
        attributes_count = [len(value) for value in traits.values()]
        completed_combinations = []

        if collection_dict['image_count'] > prod(attributes_count):
            return {'success': False, 'message': 'Expected number of generations, less than possible'}
        
        while True:
            combination = {}

            for layer, attributes in traits.items():
                image_list, chance_list = zip(*[(k,v) for attribute in attributes for k,v in attribute.items()])
                image = random.choices(image_list, chance_list)
                combination[layer] = image[0]
                
            if combination not in completed_combinations:
                completed_combinations.append(combination)
            
            if len(completed_combinations) == collection_dict['image_count']:
                break

        return cls.generate_tokens(completed_combinations, collection_dict)


# TODO: !завести ассинхроноость и многопоточность
# TODO: внедрить pinata API
# TODO: добавить поле ключем от pinata API в бд, и брать его для внедрения