import requests
from bs4 import BeautifulSoup
import re


#Variables globales:
url_racine = "http://books.toscrape.com"
#url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
url_category_to_scrap = "http://books.toscrape.com/catalogue/category/books/mystery_3/page-1.html"
url = [] #liste qui va contenir url de chaque livre

with open ("scraping_result.csv","w") as my_file:
    my_file.write ("product_page_url;universal_product_code;title;price_including_tax;price_excluding_tax;number_available;product_description;category;review_rating;image_url" + "\n")

#Verifier que l'URL est accessible
"""
if response.ok:
    print ("Le lien " + url + " est accessible")
    print ("Le scrapping des informations est en cours..")
else:
    print("L'url: " + url + " n'est pas accessible")
    exit(1)
"""


def extract_info(book_url):
    response = requests.get(book_url)
    soup = BeautifulSoup(response.text ,features="html.parser")
    all_info = soup.find("table" , {"class" : "table table-striped"}).findAll("td")

    upc = all_info[0].text
    #product_type = all_info[1].text
    price_excluding_tax = all_info[2].text[2:] #Faut-il garder symbole livres ?
    price_including_tax = all_info[3].text[2:]
    #tax = all_info[4].text
    number_available = re.findall("\d+",all_info[5].text) #Le format semble être toujour le même, donc cet extraction doit fonctionner
    review_rating = all_info[6].text  #Number of reviews or stars? 


    title_info = soup.find("div" , {"class" : "col-sm-6 product_main"}).find("h1")
    title = title_info.text

    #Cette descritpion ne contient pas d'attribut
    product_description_info = soup.find("article", {"class" : "product_page"}).find("p", {"class" : None})
    product_description = product_description_info.text

    #L'url de la category est unique et contient une part variable specifique à chaque category
    category_info = soup.find("a",{"href" : re.compile("\.\./category/books/[A-Za-z0-9_]+/index\.html")})
    category = category_info.text


    image_url_info = soup.find("img")
    image_url = url_racine + image_url_info["src"].replace("../..","")

    #Ecriture dans un fichier 
    
    with open ("scraping_result.csv","a", encoding="utf-8") as my_file:
        my_file.write (book_url + ";" + upc + ";" + title + ";" + price_including_tax + ";" + price_excluding_tax + ";" + number_available[0] + ";" + product_description + ";" + category + ";" + review_rating + ";" + image_url + "\n")



def category_information(url_category):
    response = requests.get(url_category)


    soup = BeautifulSoup(response.text ,features="html.parser")

    one_category_url = soup.findAll("div" , {"class" : "image_container"})
    for html_a in one_category_url:
        a = html_a.find("a")
        global url
        url.append(url_racine + a["href"].replace("../../..","/catalogue"))

    #On utilise une fonction recursive pour traiter l'url suivant s'il existe
    find_next_page = soup.find("li",{"class" : "next"})

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





category_information(url_category_to_scrap)

for i in url:
    extract_info(i)
