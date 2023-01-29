import requests
from bs4 import BeautifulSoup

#Verifier que l'URL est accessible
url = "http://books.toscrape.com/"
response = requests.get(url)

#print (response)


if response.ok:
    print ("Le lien " + url + " est accessible")
    print ("Le scrapping des inforamtions est en cours..")
else:
    print("L'url: " + url + " n'est pas accessible")
    exit(1)


