# Create your models here.
from django.db import models

class Product(models.Model):
    image = models.ImageField(upload_to='MEDIA_ROOT/')
    title = models.CharField(max_length=200, default=None)
    url = models.CharField(max_length=300, default=None)#, on_delete=models.CASCADE)
    price = models.CharField(max_length=10, default=None)
    desired_price = models.CharField(max_length=10, default=None)
    mail_has_been_sent = models.BooleanField(default=False)

    @staticmethod
    def print_instance_attributes():
        attributes = []
        for attribute in Product.__dict__.keys():
            if (not attribute.startswith('_')) and (attribute != 'id'):
                attributes.append(attribute)
        return attributes

    def __str__(self):
        return self.title