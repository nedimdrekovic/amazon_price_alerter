# Register your models here.
from django.contrib import admin as ad
from products.models import Product
from django.contrib import messages
from django.shortcuts import redirect
import os

#import django
#django.setup()

# model hinzufuegen damit es auf der admin-seite sichtbar ist
#admin.site.unregister(Product)
#ad.site.register(Product)

@ad.register(Product)
class ProductAdmin(ad.ModelAdmin):
    def start_scraping(self, request):
        print("Request method:", request.method)
        if request.method == 'GET':
            os.system("python manage.py crawl")
            self.message_user(self, request,
                              'Crawler initialized successfully',
                              level=messages.SUCCESS)
            print("Crawl Python aufruf!")
        return redirect('../')