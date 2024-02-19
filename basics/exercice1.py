import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint
import re

UERL = "https://books.toscrape.com/"

def rating()->list[int]:
    ids = []
    try: #try connexion 
        response = requests.get(UERL)
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
            id = re.findall(r'_\d{1,}', link)[0][1:]
        except IndexError as indx:
            print(f"Cet article ne possede pas de ID : {indx}")
            raise IndexError from indx
        else:
            ids.append(int(id))
        
    return ids
        

    #titles =[el for el in soup.find_all('a', title=True)]
    #pprint(f'titles: {titles}')

def main(seuil):
    with requests.Session() as session:
        response = session.get(UERL)

        soup = bs(response.text, 'html.parser')


        #get all categorises with her link
        #aside = soup.find('div', class_='side_categories')

        #catergorises_link = [[c.text.strip(), c.get("href")] for c in aside.find_all('a')[1:]]
        aside = soup.select("div.side_categories a")[1:]
        catergorises_link = [[c.text.strip(), c.get("href")] for c in aside]
        #pprint(catergorises_link)

        # catergories with books number
        for cl in catergorises_link:
            bl = session.get(url+cl[1])
            cl_soup = bs(bl.text,'html.parser')
            num = cl_soup.find('form', method='get').find('strong').text
            if int(num)<=seuil:
                print(f"La categories {cl[0]} n'a pas suffisament de livres ({num})")
            



if __name__=='__main__':
    #main(seuil=2)
    print(rating())
