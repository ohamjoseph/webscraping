import sys
from typing import List
import re
from urllib.parse import urljoin

from selectolax.parser import HTMLParser
import requests
from loguru import logger

URL= "https://books.toscrape.com/"

logger.remove()
logger.add(f'books.log',
           level='WARNING',
           rotation='500kb')
logger.add(sys.stderr, level="INFO") 

def get_all_books_urls(url:str)->List[str]:
    """
       Récuperer toutes les URLs des livres sur touts les pages à partir d'une url

    Args:
        url (str): URL de depart

    Returns:
        List[str]: Liste de toutes les URLs de toutes les pages
    """
    
    all_urls = []
    
    while True:
    
        logger.info(f"Scraping de la page {url}")
        try:
            with requests.Session() as session:
                response = session.get(url)
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la resquete HTTP sur la page {url} : {e}")
            continue

        tree = HTMLParser(response.text)
        urls = get_all_books_urls_on_page(url,tree=tree)
        all_urls.extend(urls)
         
        url = get_next_pages_url(url,tree=tree)
        if not url:
            break
        
    return all_urls

def get_next_pages_url(url:str, tree: HTMLParser)->str | None:
    """Recuperer l'url de page suivante a partir du HTML

    Args:
        tree (HTMLParser): Objet HTML de la page actuel
        url (str) : url actuelle

    Returns:
        str: URL de la page suivante
    """
    
    next_page_node = tree.css_first("li.next > a")
    if next_page_node and "href" in next_page_node.attributes:
        return urljoin(url, next_page_node.attributes["href"])
    
    logger.info("Il n'y a pas de bouton next sur cette page")
    return None

def get_all_books_urls_on_page(url:str,tree:HTMLParser)->List[str]:
    """Recuperer toutes les URLs des livres present sur une page

    Args:
        tree (HTMLParser): Objet HTML de la page

    Returns:
        List[str]: Liste des urls des livres de la pages
    """
    
    books_links_nodes = tree.css("h3 > a")
    if len(books_links_nodes)<=0:
        logger.error("Aucune lien de livre n'a été trouvé")
        return[]
    else:
        return [urljoin(url,link.attributes["href"]) for link in books_links_nodes if "href" in link.attributes]


def get_book_total_price(url:str, session:requests.Session=None)->float:
    """Recuperer le prix total d'un livre depuis sont url

    Args:
        url (str): l'URL du livre

    Returns:
        float: prix total du livre
    """
    
    logger.info(f"Recueration du prix de la page : {url}")
    
    try:
        if session:
            response = session.get(url)
        else:
            response = requests.get(url)
            
        response.raise_for_status()

        tree = HTMLParser(response.text)

        price = get_book_price(tree=tree)*get_book_stock(tree=tree)
        logger.info(f"Prix : {price} à la page {url}")
        return price
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de la requête HTTP : {e}")
        return 0.0
    

def get_book_price(tree:HTMLParser)->float:
    """Extraire le prix du livre de le code HTML

    Args:
        tree (HTMLParser): Le code HTML

    Returns:
        float: le prix di livre
    """
    price_node = tree.css_first("p.price_color")
    if price_node:
        price_string = price_node.text()
    else:
        logger.error(f"Aucun noeud contenant le prix n'a été trouvé.")
        return 0.0
    
    try:
        price = re.findall(r"[0-9.]+",price_string)[0]
    except IndexError as e:
        logger.error(f"Aucun nombre n'a été trouvé : {e}")
        return 0.0
    else:
        return float(price)
       

def get_book_stock(tree:HTMLParser)->int:
    """Recupérer le stock d'un livre depuis le code HTML

    Args:
        tree (HTMLParser): Le code HTML

    Returns:
        int: le stock
    """
    stock_node = tree.css_first("p.instock.availability")
    if stock_node:
        stock_string = stock_node.text()
    else:
        logger.error(f"Aucun noeud contenant le stock disponible n'a été trouvé.")
        return 0.0
    
    try:
        price = re.findall(r"[0-9]+",stock_string)[0]
    except IndexError as e:
        logger.error(f"Aucun nombre n'a été trouvé : {e}")
        return 0.0
    else:
        return int(price)
    

def main():
    all_books_urls=get_all_books_urls(URL)
    total_price=[]

    with requests.Session() as session:

        for book_url in all_books_urls:
            price = get_book_total_price(book_url, session=session)
            total_price.append(price)

    return sum(total_price)

if __name__=='__main__':
    print(main())