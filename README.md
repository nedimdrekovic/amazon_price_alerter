# Amazon Price Alerter (in Progress)

The amazon price alerter allows the user to create a list of products and send a email if the product's current price is below a user-defined desired price.

# 💻 Tech Stack:
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) 
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![Scrapy](https://img.shields.io/badge/Scrapy-green?style=for-the-badge&logo=Scrapy)
![JavaScript](https://img.shields.io/badge/JavaScript-yellow?style=for-the-badge&logo=JavaScript)
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)


## Installations
1. Clone the repository:
   ```bash
   git clone https://github.com/nedimdrekovic/amazon_price_alerter.git

2. Install a virtual environment to work on and activate it (recommended):
   ```bash
   python3 -m venv <venv_name>
   source <venv_name>/bin/activate

3. Install the libraries/packages/modules required to run the project:
   ```bash
   pip install -r requirements.txt

4. Run database migrations (run after every change in models.py):
   ```bash
   python3 manage.py makemigrations
   python3 manage.py migrate
   
5. Start the developmemt server to run the project (optional: port):
   ```bash
   python3 manage.py runserver <port>

6. Open web browser and type:
   ```bash
   http://127.0.0.1:8000/
   or
   http://127.0.0.1:<port>/    (depending on the port)

## Features (new features coming soon)
1. ```Url and Price```: type url + desired_price

2. ```Adding Product```: press the button ```Add```

     2.1. Check if inputs are valid.
     ```
       valid url: existing amazon url that hasn't been added to the list yet
       valid price: price needs to be a number (german standard)
     ```      
     Examples:
     ```
     1.3 --> valid
     1,3 --> changed to 1.3 --> valid
     100.557 --> rounded down to 100.55
     9999.56,34 --> invalid
     9999,56.34 --> invalid
     ```
   
3. ```Deleting Product```: deletes product from list by pressing the button ```Delete``` on the product's field.



## ToDo's:
- better UI for listing products
- feature for notifying user when product is available
- add loading symbol during scraping process
