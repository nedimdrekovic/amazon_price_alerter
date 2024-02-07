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


<<<<<<< HEAD

=======
>>>>>>> origin/master
def scrape_image(soup):
    # children = soup.find('div', {'id': "img-canvas"})
    new_product_image = "NA"
    children = soup.find_all("div", {"id": "imgTagWrapperId"})
    if children == None:
        new_product_image = "https://www.salonlfc.com/wp-content/uploads/2018/01/image-not-found-scaled.png"
    else:
        # children = children.findChildren('img')
        # new_product_image = children[-1].find("div", {"img", "src"})
        pass

    # children = children.find('img', recursive=False)
    if children:
        if type(children) == list:
            new_product_image = children[-1].find("img")['src']
        else:
            new_product_image = children[-1].find("img")['src']
    else:  # other method
        children = soup.find_all("div", {"class": "imgTagWrapper"})
        """  tag = soup.find(id="imgTagWrapperId")
        if tag is not None:
            children = tag.find("img", recursive=False)
            for child in children:
                if child.has_attr('src'):
                    new_product_image = child['src']"""
        # "https://www.salonlfc.com/wp-content/uploads/2018/01/image-not-found-scaled.png"
    return new_product_image


def scrape_title(soup):
    # am besten schon vorher in Liste einfuegen, damit nicht immer in Webseite
    # gesucht werden muss und Ladezeiten somit nicht unnoetig lang sind
    try:
        new_product_title = soup.find("span", attrs={"id": 'productTitle'}).string.strip()
        # Erscheinungsdatum: id=productSubtitle
        # product_title = product_title.string.strip().replace(',', ''
        print("-" * 50)
    except AttributeError:
        new_product_title = "NA"
    return new_product_title


def scrape_price(soup):
    # alle Daten aus Datenbank in Tabelle einfügen, bis auf Preis.
    # Preis jedes Mal bei Aufruf aus Amazon-Webseite ausfiltern und vergleichen ob
    # sich Wert veraendert hat
    try:
        new_product_price_v0 = soup.find("span", attrs={'class': 'a-color-price'})
        new_product_price_v1 = soup.find("span", attrs={'class': 'a-offscreen'})
        new_product_price_v2 = soup.find("span", attrs={'class': 'aok-offscreen'})
        new_product_price_v3 = soup.find("span", attrs={'id': "price"})  # .text  # aktueller Preis
        # new_product_price_v4 = soup.find("span", attrs={'class': "a-price-whole"})  # aktueller Preis
        new_product_price_v5 = soup.find("span", attrs={'aria-hidden': "true"})  # aktueller Preis

        # checking multiple methods to
        new_product_price_list = [new_product_price_v0,
                                  new_product_price_v1,
                                  new_product_price_v2,
                                  new_product_price_v3,
                                  # new_product_price_v4,
                                  new_product_price_v5]
        price_is_found = [True if price_found is not None else False for price_found in new_product_price_list]
        if any(price_is_found):  # if price is found / product is available
            # iterate over different methods that find the price tag for the product
            prices = []
            for i, price_found in enumerate(price_is_found):
                if price_found:
                    price = new_product_price_list[i].text.replace(" ", "")
                    prices.append(price)

            # set price for the first solution that's been found and skip every other solution
            new_product_price = ""
            for price in prices:
                if "nicht verfügbar" in price:
                    new_product_price = "Derzeit nicht verfügbar."
                if "€" in price:  # get first found solution
                    new_product_price = price
                    break
        else:  # if there is no price found
            new_product_price = "NA"

        """
            new_product_price = soup.find("span", attrs={'class': "a-price-whole"})  # aktueller Preis
            price_tags = new_product_price.find_next_siblings()  # get next tags which includes n digits of price
            new_product_price = new_product_price.text
            for tag in price_tags:
                new_product_price += "" + tag.text"""

        new_product_price = new_product_price.replace(",", ".")
        new_product_price = new_product_price.split("€")[0]
        if new_product_price not in ["", "NA"]:
            new_product_price = float(new_product_price)  # converting string to number

    except AttributeError:
        new_product_price = "NA"
    except ValueError:
        print("Kein Preis für das Produkt gefunden.")
        new_product_price = "NA"
    return new_product_price


def scrape_product_data(soup):
    # scrape data for each property carefully to find data in most cases
    new_product_image = scrape_image(soup)
    new_product_title = scrape_title(soup)
    new_product_price = scrape_price(soup)

    return new_product_image, new_product_title, new_product_price


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


def crawl():
    crawler = CrawlerProcess(get_project_settings())
    crawler.crawl(ProductSpider)
    crawler.start(stop_after_crawl=False)


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

<<<<<<< HEAD
    """# quick checking if scraping went successfully by simply checking if product has any empty value for the attributes
    for product in list(Product.objects.all().values()):
        for product_property, product_value in product.items():
            if product_value == "":
                print("product has not been scraped successfully.", product_property, "couldn't be found.")"""

    for product in Product.objects.all().values():
        if float(product['price']) <= float(product['desired_price']):
            if not product['mail_has_been_sent']:
                print("Send mail.")
                # send_email(product['url'], product['price'], product['desired_price'])
                Product.objects.filter(url=product['url']).update(mail_has_been_sent=True)

=======
>>>>>>> origin/master
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
