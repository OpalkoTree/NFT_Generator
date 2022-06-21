from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes

from .models import Collection, Attribute, Layer
from .serializers import CollectionSerializer, AttributeSerializer, LayerSerializer

from .generator import Generator

@api_view(['POST'])
@permission_classes((AllowAny,))
def generate_nft(request):
    import time
    start = time.time()

    if not request.data.get('id'):
        return JsonResponse({'success': False, 'message': 'id required'}, status=200, safe=False)

    layers = Layer.objects.filter(collection__id=request.data['id'])
    layers_list = {layer.layer_name:[{i.image.name:i.chance} for i in layer.attributes.all()] for layer in layers}

    generation = Generator.generate_combinations(layers_list, request.data['id'], request.data['api_key'])

    print(round((time.time() - start), 3))

    return JsonResponse(generation, status=200, safe=False)


class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = [AllowAny]

    def list(self, request):
        collections_query = self.queryset.filter(creator=request.user)
        serializer = self.serializer_class(collections_query, many=True)

        return JsonResponse({'success': True, 'data': serializer.data}, status=200)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return JsonResponse({'success': True, 'data': serializer.data}, status=200)

    def update(self, request, **kwargs):
        collection = self.get_object()
        serializer = self.serializer_class(collection, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return JsonResponse({'success': True, 'data': serializer.data}, status=200)

    def destroy(self, **kwargs):
        collection = self.get_object()
        collection.delete()

        return JsonResponse({'success': True, 'message': 'Has been deleted'}, status=200)


class AttributeViewSet(viewsets.ModelViewSet):
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer
    permission_classes = [AllowAny]
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        total_dict = serializer.save()

        return JsonResponse({'success': True, 'data': total_dict}, status=200)

    def destroy(self, **kwargs):
        attribute = self.get_object()
        attribute.delete()

        return JsonResponse({'success': True, 'message': 'Has been deleted'}, status=200)


class LayerViewSet(viewsets.ModelViewSet):
    queryset = Layer.objects.all()
    serializer_class = LayerSerializer
    permission_classes = [AllowAny]

    def list(self, request):
        layer_query = self.queryset.filter(collection=request.data['collection'])
        serializer = self.serializer_class(layer_query, many=True)

        return JsonResponse({'success': True, 'data': serializer.data}, status=200)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return JsonResponse({'success': True, 'data': serializer.data}, status=200)

    def update(self, request, **kwargs):
        layer = self.get_object()
        serializer = self.serializer_class(layer, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return JsonResponse({'success': True, 'data': serializer.data}, status=200)

    def destroy(self, **kwargs):
        layer = self.get_object()
        layer.delete()

        return JsonResponse({'success': True, 'message': 'Has been deleted'}, status=200)
