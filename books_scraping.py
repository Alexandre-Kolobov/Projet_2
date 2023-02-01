import requests
from bs4 import BeautifulSoup
import re
import csv
import os
import shutil


# Global variables:
url_racine = "http://books.toscrape.com"
url_category = []  # List for urls of each category
url = []  # List for url of each book
liste_dict_categ = []  # List to save dictionnaries with all book information
folder_cvs = "scraping_result/"

# Remove old files and folder and create a new empty folder:
if os.path.exists(folder_cvs) is True:
    shutil.rmtree(folder_cvs)
os.mkdir(folder_cvs)


def list_categories():  # To get URL of each category
    response = requests.get(url_racine)

    # Check that URL is ok:
    if response.ok:
        print("The link: " + url_racine + " is ok")
        print("Start scraping..")
    else:
        print("The link: " + url_racine + " is not accessible")
        exit(1)

    # Put the URL of each category in the list
    soup = BeautifulSoup(response.text, features="html.parser")
    all_categories_navlist = soup.find("ul", {"class": "nav nav-list"})
    all_categories = all_categories_navlist.find("ul").findAll("a")

    for category_a in all_categories:
        global url_category
        url_category.append(url_racine + "/" + category_a["href"])


def category_information(url_category):  # To get URL of each book
    response = requests.get(url_category)
    soup = BeautifulSoup(response.text, features="html.parser")

    one_category_url = soup.findAll("div", {"class": "image_container"})
    for html_a in one_category_url:
        a = html_a.find("a")
        global url
        url.append(url_racine + a["href"].replace("../../..", "/catalogue"))

    # Use of recursive to check possibility of next page
    find_next_page = soup.find("li", {"class": "next"})

    if str(find_next_page) != "None":
        find_next_page_a = find_next_page.find("a")
        find_next_page_href = find_next_page_a.attrs["href"]
        url_category_splitted = url_category.split("/")
        url_category_splitted[7] = find_next_page_href
        url_next_page = ""
        for index in url_category_splitted:
            url_next_page = url_next_page + index + "/"

        url_next_page = url_next_page[:-1]

        category_information(url_next_page)


def extract_info(book_url):
    response = requests.get(book_url)
    soup = BeautifulSoup(response.text, features="html.parser")
    all_info_tstriped = soup.find("table", {"class": "table table-striped"})
    all_info = all_info_tstriped.findAll("td")

    upc = all_info[0].text
    # product_type = all_info[1].text
    price_excluding_tax = all_info[2].text[2:]  # To remove the currency symbol
    price_including_tax = all_info[3].text[2:]  # To remove the currency symbol
    # tax = all_info[4].text
    # d+ means number in range 0-9 (one or more times):
    number_available = re.findall("\\d+", all_info[5].text)
    review_rating = all_info[6].text

    title_info_div = soup.find("div", {"class": "col-sm-6 product_main"})
    title_info = title_info_div.find("h1")
    title = title_info.text

    # This description doesn't have class, we can use None
    item_info_article = soup.find("article", {"class": "product_page"})
    item_info_p = item_info_article.find("p", {"class": None})

    if str(item_info_p) == "None":
        product_description = "Pas de description"
    else:
        product_description = item_info_p.text

    # URL of each category is only one element different from others
    category_info = soup.find("a", {"href": re.compile("\\.\\./category/books/"
                              "[A-Za-z0-9_ -]+/index\\.html")})
    category = category_info.text

    image_url_info = soup.find("img")
    image_url = url_racine + image_url_info["src"].replace("../..", "")

    # Add all book's information in a dictionnary
    dict_info = {"product_page_url": book_url, "universal_product_code": upc,
                 "title": title, "price_including_tax": price_including_tax,
                 "price_excluding_tax": price_excluding_tax,
                 "number_available": number_available[0],
                 "product_description": product_description,
                 "category": category,
                 "review_rating": review_rating,
                 "image_url": image_url}

    # Add dictionnary in a list
    liste_dict_categ.append(dict_info)


# Create and append a file per category with book's informations
def write_file(list_with_dicts):
    for i in list_with_dicts:
        file_name = (folder_cvs + i["category"] + ".csv")
        if os.path.isfile(folder_cvs + i["category"] + ".csv") is False:
            with open(file_name, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, i.keys(), delimiter=";")
                writer.writeheader()
                writer.writerow(i)
        else:
            with open(file_name, "a", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, i.keys(), delimiter=";")
                writer.writerow(i)


print("Listing categories")
list_categories()

print("Getting books URL")
for category in url_category:
    category_information(category)

print("Getting books informations")
for i in url:
    extract_info(i)

print("Making files")
write_file(liste_dict_categ)
