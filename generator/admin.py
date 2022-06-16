from django.contrib import admin
from .models import Blockchain, Collection, Attribute, Layer


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):

    model = Collection
    list_display = ['collection_name', 'image_count', 'blockchain', 'is_generated']
    list_filter = ['image_count', 'blockchain', 'is_generated']
    search_fields = ('creator', 'collection_name', 'collection_family', 'name_format')


admin.site.register(Blockchain)
admin.site.register(Attribute)
admin.site.register(Layer)
