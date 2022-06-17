import os
import random
import json
from math import prod
from typing import List
from PIL import Image
from backend.settings import MEDIA_ROOT
from generator.models import Collection
from generator.serializers import CollectionSerializer


class Generator():

    @staticmethod
    def generate_token(loop: int, combination: dict, collection: dict) -> None:
        attributes_dict = {}
        output = Image.open(os.path.join(MEDIA_ROOT, list(combination.values())[0]))

        for layer, attribute in list(combination.items())[1:]:
            paste_attribute = Image.open(os.path.join(MEDIA_ROOT, attribute)).convert('RGBA')
            output.paste(paste_attribute, (0,0), paste_attribute)
            attributes_dict[layer] = attribute

        collection['attributes'] = attributes_dict
        output.convert('RGB').save(f'{loop}.jpg', 'JPEG', optimize=True)

        with open(f'{loop}.json', 'w') as file: 
            json.dump(collection, file, indent=4)


    @classmethod
    def generate_tokens(cls, combinations: List[dict], collection: dict) -> dict:
        for loop, combination in enumerate(combinations):
            cls.generate_token(loop, combination, collection)

        return {'success': True, 'message': f'Generations completed'}

    @classmethod
    def generate_combinations(cls, traits: dict, id: int) -> dict:
        collection = CollectionSerializer(Collection.objects.get(pk=id)).data
        attributes_count = [len(value) for value in traits.values()]
        completed_combinations = []

        if collection['image_count'] > prod(attributes_count):
            return {'success': False, 'message': f'Expected number of generations, less than possible'}
        
        while True:
            combination = {}

            for layer, attributes in traits.items():
                image_list, chance_list = zip(*[(k,v) for attribute in attributes for k,v in attribute.items()])
                image = random.choices(image_list, chance_list)
                combination[layer] = image[0]
                
            if combination not in completed_combinations:
                completed_combinations.append(combination)
            
            if len(completed_combinations) == collection['image_count']:
                break

        return cls.generate_tokens(completed_combinations, collection)

# TODO: завести ассинхроноость и многопоточность