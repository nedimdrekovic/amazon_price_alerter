import json
import smtplib
import ssl
from email.message import EmailMessage
from urllib.parse import unquote

import django
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from scraper.scraper.spiders.product_spider import CrawlerScript
from scraper.scraper.spiders.product_spider import ProductSpider
from .models import Product

django.setup()



# Create your views here.
# in der View wird die Logik der Anwendung geschrieben
# so werden informationen aus dem Model abgefragt
# und an ein template weitergegeben

HEADERS = ({
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 44.0.2403.157 Safari / 537.36',
    'Accept': 'text/html',
})
cookies = dict(language='de')

# Define email sender and receiver
email_sender = 'maxmustermann@gmail.com'
email_password = '1234567890'  # via google mail
email_receiver = 'erikamustermann@gmail.com'


def send_email(url, price, desired_price):
    # Set the subject and body of the email
    subject = 'Check out my new video!'
    body = "Der Preis deines Artikels ist nun unter deinem Wunschpreis!" + \
           "\nDein Wunschpreis war " + str(desired_price) + \
           "€.\nDer aktuelle Preis liegt bei " + str(price) + \
           "€. (" + url + ")"

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(body)

    # Add SSL (layer of security)
    context = ssl.create_default_context()

    # Log in and send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())


@csrf_exempt
def delete_prod(request):
    """
    Handles the deleting process of each product

    :param request: containts data about the current request
    :return: Jsonresponse that returns the generated response for the status update
    """
    if request.method == 'POST':
        url = request.POST.get('current_product_link')
        Product.objects.filter(url=url).delete()
        return JsonResponse({'status': 'deleted'})


def show_webpage(request):
    """ Renders template which presents the actual website to the user."""
    return render(request, 'products/product_list.html')


@csrf_exempt
def product_list(request):
    """
    Updates product data after each get request.

    :param request: contains data about the current request
    :return: Jsonresponse that returns the generated response
    """
    print("Aktualisieren!!")
    status = ""
    configure_logging()

    # Starte den Crawl-Prozess
    spider = ProductSpider(data=[list(Product.objects.all().values()), 'update'])
    crawler = CrawlerScript(spider)
    crawler.start()
    crawler.join()

    """# quick checking if scraping went successfully by simply checking if product has any empty value for the attributes
        for product in list(Product.objects.all().values()):
            for product_property, product_value in product.items():
                if product_value == "":
                    print("product has not been scraped successfully.", product_property, "couldn't be found.")"""

    for product in Product.objects.all().values():
        if not product['mail_has_been_sent']:
            # send_email(product['url'], product['price'], product['desired_price'])
            Product.objects.filter(url=product['url']).update(mail_has_been_sent=True)
        Product.objects.filter(url=product['url']).update(price=product['price'])

    products = list(Product.objects.all().values())
    return JsonResponse({'products': products, 'status': status})


def max_price_is_valid(max_price):
    """
    Checks if there is validation error in passed parameter for the desired price.

    :param max_price: desired_price for the product as a string
    :return: True if the desired price is a valid value.
    """
    try:
        val = float(max_price)
    except ValueError:
        return False
    return True


def url_is_valid(url):
    """
    Checks if the list of products already contains the passed url.

    :param url: the passed url.
    :return: True if url is not already in the list and can be added
    """
    existing_urls = list(
        Product.objects.all().values_list('url', flat=True))  # flat=True for returning QuerySets instead of 1-tuples
    return unquote(url) not in existing_urls


@csrf_exempt
def add_prod(request):
    """
    Handles the adding of a product to the list after submitting the 'add' button.

    :param request: containts data about the current request
    :return: Jsonresponse containing information either about the created product data or a report for its non-creation
    """
    if request.method == 'POST':
        url = request.POST.get('amzn_url')
        max_price = request.POST.get('desired_price')
        max_price = max_price.replace('€', '')  # remove euro symbol in case it is added
        max_price = max_price.replace('.', '')  # remove points in case price is >= 1000
        max_price = max_price.replace(',', '.')  # replace comma with point to represent positions after decimal point

        if url_is_valid(url):
            try:
                if max_price_is_valid(max_price):
                    # get here only if all conditions for creating an object are met
                    # Starte den Crawl-Prozess für den Spider mit der angegebenen Start-URL

                    # scrape product
                    spider = ProductSpider(data=[[{'url': url, 'desired_price': max_price}], 'create'])
                    crawler = CrawlerScript(spider)
                    crawler.start()
                    crawler.join()

                    new_product = Product.objects.filter(url=unquote(url))
                    if not new_product:
                        # if product is not found in database
                        return JsonResponse({'status': 'not_existing'})
                    new_product = new_product[0]  # get actual product

                    new_product_data = {
                        'image': json.dumps(str(new_product.image)),
                        'title': new_product.title,
                        'url': url,
                        'price': new_product.price,
                        'desired_price': new_product.desired_price,
                        'status': "new_product_created"
                    }

                    # update product list once after adding the product
                    return JsonResponse(new_product_data)
                else:
                    return JsonResponse({'status': 'empty_input_field'})
            except ValueError:
                return JsonResponse({'status': 'only_numbers'})
            except Exception as e:
                print("Error -->", e)
        else:
            return JsonResponse({'status': 'is_already_in_list'})
    return show_webpage(request)
