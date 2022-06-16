from django.http import JsonResponse
from rest_framework import serializers
from .models import Collection, Attribute, Layer


class CollectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Collection
        fields = "__all__"

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        ret['creator'] = instance.creator.username
        ret['blockchain'] = instance.blockchain.blockchain_name

        return ret


class AttributeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Attribute
        fields = "__all__"


class LayerSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Layer
        fields = "__all__"
        depth = 1

    def to_representation(self, instance):
        ret = super().to_representation(instance)

        ret['collection'] = instance.collection.collection_name

        return ret
