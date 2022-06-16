from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator


class Blockchain(models.Model):
    blockchain_name = models.CharField(max_length=128)

    def __str__(self):
        return self.blockchain_name


class Collection(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    collection_name = models.CharField(max_length=128)
    collection_family = models.CharField(max_length=128)
    description = models.TextField(max_length=500)
    name_format = models.CharField(max_length=128)
    image_count = models.IntegerField(
        default=1, validators=[
            MinValueValidator(1), MaxValueValidator(10)
        ]
        )
    royalty = models.FloatField(
        default=0.1, validators=[
            MinValueValidator(0.1), MaxValueValidator(10.0)
        ]
    )
    royalty_address = models.CharField(max_length=128)
    blockchain = models.ForeignKey(Blockchain, on_delete=models.CASCADE)
    is_generated = models.BooleanField(default=False)

    def __str__(self):
        return self.collection_name


class Attribute(models.Model):
    image = models.FileField()
    chance = models.IntegerField(
        default=0, validators=[
            MinValueValidator(0), MaxValueValidator(100)
        ]
    )

    def __str__(self):
        return self.image.name


class Layer(models.Model): 
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    layer_name = models.CharField(max_length=128)
    attributes = models.ManyToManyField(Attribute)

    def __str__(self):
        return self.layer_name
