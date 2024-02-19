import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint
import re

URL = "https://books.toscrape.com/"

def rating()->list[int]:
    '''
        Displays the ID list of books on the home page
        with a star rating of one.
    '''
    ids = []
    try: #try connexion 
        response = requests.get(URL)
        response.raise_for_status()
    except requests.exceptions.RequestException as ex:
        print(f"Il y'a un problème de connexion au site {ex}")
        raise requests.exceptions.RequestException from ex
    
    # get response and all books with one rate
    soup = bs(response.text,'html.parser')
    books_with_one =  soup.select('p.star-rating.One')

    for book in books_with_one:
        try:
            link = book.find_next('h3').find('a')["href"]
        except TypeError as type:
            print(f'[err] impossible de trouver la balise <a> dans cet article : {type}')
            raise KeyError from type
        except AttributeError as attr:
            print(f'[err] impossible de trouver la balise <h3> dans cet article : {attr}')
            raise AttributeError from attr
        except KeyError as key:
            print(f"[err] impossible de trouver le lien de detail de l'article : {key}")
            raise KeyError from key
        
        try:
            id = re.findall(r'_\d+', link)[0][1:]
        except IndexError as indx:
            print(f"Cet article ne possede pas de ID : {indx}")
            raise IndexError from indx
        else:
            ids.append(int(id))
        
    return ids

if __name__=='__main__':
    print(rating())