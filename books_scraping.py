import requests
from bs4 import BeautifulSoup
import re
import csv
import os
import shutil

#Variables globales:
url_racine = "http://books.toscrape.com"
#url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
url_category_to_scrap = "http://books.toscrape.com/catalogue/category/books/mystery_3/page-1.html"
url_category = [] #liste qui va contenir url de chaque category
url = [] #liste qui va contenir url de chaque livre
liste_dict_categ = [] #liste qui va contenir les dictionnaires avec des info de chaque livre par categorie

#Remove old files with folder and create a new empty folder
if os.path.exists("scraping_result/") == True:
    shutil.rmtree("scraping_result/")

os.mkdir("scraping_result/")


#Verifier que l'URL est accessible
"""
if response.ok:
    print ("Le lien " + url + " est accessible")
    print ("Le scrapping des informations est en cours..")
else:
    print("L'url: " + url + " n'est pas accessible")
    exit(1)
"""

def list_categories():
    response = requests.get(url_racine)
    soup = BeautifulSoup(response.text ,features="html.parser")
    all_categories = soup.find("ul" , {"class" : "nav nav-list"}).find("ul").findAll("a")

    for category_a in all_categories:
        global url_category
        url_category.append(url_racine + "/" + category_a["href"])

 


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
    if str(product_description_info) == "None":
        product_description = "Pas de description"
    else:
        product_description = product_description_info.text

    #L'url de la category est unique et contient une part variable specifique à chaque category
    category_info = soup.find("a",{"href" : re.compile("\.\./category/books/[A-Za-z0-9_ -]+/index\.html")})
    category = category_info.text
    # A optimiser 


    image_url_info = soup.find("img")
    image_url = url_racine + image_url_info["src"].replace("../..","") #image_url_info["src"] - You can access a tag’s attributes by treating the tag like a dictionary


    #Ecriture dans un fichier 
    #
    """
    with open ("scraping_result.csv","a", encoding="utf-8") as my_file:
        my_file.write ("product_page_url;universal_product_code;title;price_including_tax;price_excluding_tax;number_available;product_description;category;review_rating;image_url" + "\n")
        my_file.write (book_url + ";" + upc + ";" + title + ";" + price_including_tax + ";" + price_excluding_tax + ";" + number_available[0] + ";" + product_description + ";" + category + ";" + review_rating + ";" + image_url + "\n")
    """
    #Passer par dictionnaire + une fonction qui fait le liste des dictionnaires
   
    dict_info = {"product_page_url":book_url,"universal_product_code":upc,"title":title,"price_including_tax":price_including_tax, \
        "price_excluding_tax":price_excluding_tax,"number_available":number_available[0],"product_description":product_description, \
        "category":category,"review_rating":review_rating,"image_url":image_url}
    
    liste_dict_categ.append(dict_info)
    



def write_file(list_with_dicts):
    for i in list_with_dicts:
        print (i["category"])
        if os.path.isfile("scraping_result/" + i["category"] + ".csv") == False:
            with open ("scraping_result/"+ i["category"] + ".csv","w",newline="",encoding="utf-8") as my_file:
                writer = csv.DictWriter(my_file, i.keys(),delimiter=";")
                writer.writeheader()
                writer.writerow(i)
        else:
            with open ("scraping_result/"+ i["category"] + ".csv","a",newline="",encoding="utf-8") as my_file:
                writer = csv.DictWriter(my_file, i.keys(),delimiter=";")
                writer.writerow(i)


list_categories()

for category in url_category:
    category_information(category)
#category_information("http://books.toscrape.com/catalogue/category/books/music_14/index.html")

for i in url:
    extract_info(i)
    #data = extract_info(i)
    #liste_categ.append(data)
    #dev fonction pour ecrire un fichier en one shot 

write_file(liste_dict_categ)



"""
with open ("scraping_result/" + category_a.text + ".csv","w") as my_file:
    my_file.write ("product_page_url;universal_product_code;title;price_including_tax;price_excluding_tax;number_available;product_description;category;review_rating;image_url" + "\n")
    now = datetime.now()
 
print("now =", now)

# dd/mm/YY H:M:S
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
print("date and time =", dt_string)
"""