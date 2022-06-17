import json
from requests import JSONDecodeError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Collection, Attribute, Layer


class CollectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Collection
        fields = '__all__'

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        ret['creator'] = instance.creator.username
        ret['blockchain'] = instance.blockchain.blockchain_name

        return ret


class CollectionMetaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Collection
        fields = ['name', 'image_count', 'collection_name', 'description', 'blockchain']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['blockchain'] = instance.blockchain.blockchain_name

        return ret


class AttributeSerializer(serializers.ModelSerializer):
    image = serializers.ListField()
    chance = serializers.ListField()

    class Meta:
        model = Attribute
        fields = '__all__'

    def validate_chance(self, value):
        try:
            return json.loads(value[0])
        except JSONDecodeError:
            return value

    def validate(self, value):
        if len(value['image']) == len(value['chance']):
            return value
        else:
            raise ValidationError('The number of images does not match the number of chances')

    def create(self, validated_data):
        total_data = {}

        for image, chance in zip(validated_data['image'], validated_data['chance']):
            total_data |= {image.name: chance}
            self.Meta.model.objects.create(image=image, chance=chance)

        return total_data


class LayerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Layer
        fields = '__all__'
        depth = 1

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        ret['collection'] = instance.collection.name

        return ret
