import random
import json
from PIL import Image
from math import prod


MEDIA_URL = './media/'

class Generator():

    def generate(meta:dict, traits:list, quantity:int) -> dict:
        attributes_count = [len(value) for value in traits.values()]
        weighted_layers = []
        attributes_list = []
        completed_list = []

        for _ in range(quantity):
            attributes_dict = {}
            completed = []

            for layer, attributes in traits.items():
                completed = {}

                image_list, chance_list = zip(*[(k,v) for attribute in attributes for k,v in attribute.items()])
                image = random.choices(image_list, chance_list)[0]
                weighted_layers.append(Image.open(MEDIA_URL + image).convert('RGBA'))
                completed[layer] = image
                completed_list.append(completed)

            if quantity > prod(attributes_count):
                return {'success': False, 'message': f'Expected number of generations, less than possible'}
            
            if completed not in attributes_list:
                output = weighted_layers[0]

                for trait in range(1, weighted_layers.__len__()):
                    output.paste(weighted_layers[trait], (0,0), weighted_layers[trait])

                output.save(f'{len(attributes_list)}.png', 'PNG')
                attributes_dict['attributes'] = completed_list

                meta['attributes'] = completed_list
                json.dump(meta, open(f'{len(attributes_list)}.json', 'w'), indent = 4)
            
            attributes_list.append(attributes_dict)

        return {'success': True, 'message': f'Successfully generated {quantity} NFTs'}

'''
завести ассинхроноость и многопоточность
'''
