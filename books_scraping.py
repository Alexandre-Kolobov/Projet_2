import re
import csv
import os
import shutil
import requests
from bs4 import BeautifulSoup
import wget


# Global variables:
URL_RACINE = "http://books.toscrape.com"
FOLDER_CVS = "scraping_result/"
FOLDER_IMG = "scraping_result/img/"
url_category = []  # List for urls of each category
url = []  # List for url of each book
liste_dict_categ = []  # List to save dictionnaries with all book information
chars_to_replace = ['<', '>', ':', '/', '\\', '|', '?', '*', "\""]


def remove_folder(folder):
    """Remove folder and it's files and create a new empty folder.

    Arguments:
    folder -- the path of folder
    """
    if os.path.exists(folder) is True:
        shutil.rmtree(folder)
    os.mkdir(folder)


def list_categories():
    """To get URL of each category"""
    response = requests.get(URL_RACINE)

    # Check that URL is ok:
    if response.ok:
        print("The link: " + URL_RACINE + " is ok")
        print("Start scraping..")
    else:
        print("The link: " + URL_RACINE + " is not accessible")
        exit(1)

    # Put the URL of each category in the list
    soup = BeautifulSoup(response.text, features="html.parser")
    all_categories_navlist = soup.find("ul", {"class": "nav nav-list"})
    all_categories = all_categories_navlist.find("ul").findAll("a")

    for category_a in all_categories:
        global url_category
        url_category.append(URL_RACINE + "/" + category_a["href"])


def category_information(url_category):
    """To get URL of each book by parsing URL of each category

    Arguments:
    url_category -- URL of one category
    """
    response = requests.get(url_category)
    if response.ok is False:
        print("URL is KO:" + url_category)
        exit(1)

    soup = BeautifulSoup(response.text, features="html.parser")

    one_category_url = soup.findAll("div", {"class": "image_container"})
    for html_a in one_category_url:
        a = html_a.find("a")
        global url
        url.append(URL_RACINE + a["href"].replace("../../..", "/catalogue"))

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
    """To get book information and save in a dictionnary

    Arguments
    book_url -- URL of one book
    """
    response = requests.get(book_url)
    if response.ok is False:
        print("URL is KO:" + book_url)
        exit(1)

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
    image_url = URL_RACINE + image_url_info["src"].replace("../..", "")

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


def write_file(list_with_dicts):
    """From a list with dictionnaries create a file and append it

    Arguments:
    list_with_dicts -- list with dictionnaries that contains books informations
    """
    for i in list_with_dicts:
        file_name = (replace_chars(" ", "_", i["category"]) + ".csv")
        file = (FOLDER_CVS + file_name)
        if os.path.isfile(file) is False:
            with open(file, "w", newline="", encoding="utf-8") as wfile:
                writer = csv.DictWriter(wfile, i.keys(), delimiter=";")
                writer.writeheader()
                writer.writerow(i)
        else:
            with open(file, "a", newline="", encoding="utf-8") as wfile:
                writer = csv.DictWriter(wfile, i.keys(), delimiter=";")
                writer.writerow(i)


def download_img(list_with_dicts):
    """Download images from URL in a dictionnary

    Argumetns:
    list_with_dicts -- list with dictionnaries that contains image's URL
    """
    for i in list_with_dicts:
        print(i["category"] + "###" + i["title"] + "\n")
        file_name = replace_chars(chars_to_replace, "", i["title"])
        file = (FOLDER_IMG + file_name + ".jpg")
        wget.download(i["image_url"], out=file)
        print("\n")


def replace_chars(chars, replacement, text):
    """Replace file name caracteres and limit max length

    Arguments:
    chars -- Characters to be replaced
    replacement -- By what characters will be replaced
    text - Text where characters will be replaced
    """
    for char in chars:
        if char in text:
            text = text.replace(char, replacement)
    return text[:100]


print("Removing old files")
remove_folder(FOLDER_CVS)
remove_folder(FOLDER_IMG)

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

print("Downloading book's images")
download_img(liste_dict_categ)
