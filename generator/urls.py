from django.contrib import admin
from django.urls import path
from rest_framework import routers
from .views import CollectionViewSet, AttributeViewSet, LayerViewSet, generate_nft


app_name = 'generator'

urlpatterns = [
    path('collection/', CollectionViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('collection/<int:pk>/', CollectionViewSet.as_view({'patch': 'update', 'delete': 'destroy'})),

    path('collection/attribute/', AttributeViewSet.as_view({'post': 'create'})),
    path('collection/attribute/<int:pk>/', AttributeViewSet.as_view({'delete': 'destroy'})),

    path('collection/layer/', LayerViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('collection/layer/<int:pk>/', LayerViewSet.as_view({'patch': 'update', 'delete': 'destroy'})),

    path('collection/generate/', generate_nft),
]

# https://dizballanze.com/ru/django-rest-framework-delete-put-patch-actions-on-list/
