import os
import random
import json
from PIL import Image
from math import prod
from backend.settings import MEDIA_ROOT

class Generator():

    @staticmethod
    def generate_tokens(combinations: list) -> dict:
        for loop, combination in enumerate(combinations):
            output = Image.new(
                'RGBA',
                Image.open(os.path.join(MEDIA_ROOT, list(combination.values())[0])).size
            )

            for layer, attribute in combination.items():
                attribute = Image.open(os.path.join(MEDIA_ROOT, attribute)).convert('RGBA')
                output.paste(attribute, (0,0), attribute)

            output.save(f'{loop}.png', 'PNG')

        return {'success': True, 'message': f'Generations completed'}

    @classmethod
    def generate_combinations(cls, traits:list, quantity:int) -> dict:
        attributes_count = [len(value) for value in traits.values()]
        completed_combinations = []

        if quantity > prod(attributes_count):
            return {'success': False, 'message': f'Expected number of generations, less than possible'}
        
        while True:
            combination = {}

            for layer, attributes in traits.items():
                image_list, chance_list = zip(*[(k,v) for attribute in attributes for k,v in attribute.items()])
                image = random.choices(image_list, chance_list)
                combination[layer] = image[0]
                
            if combination not in completed_combinations:
                completed_combinations.append(combination)
            
            if len(completed_combinations) == quantity:
                break

        return cls.generate_tokens(completed_combinations)

# TODO: завести ассинхроноость и многопоточность