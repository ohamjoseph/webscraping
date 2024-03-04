"""||-->>>>>>>>>>>>>>>>>IMPORT<<<<<<<<<<<<<<<<<<<<<<<<--||"""
import sys
import re
from pathlib import Path

from loguru import logger
import requests
from bs4 import BeautifulSoup as bs

"""||-->>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<--||"""

FILEPATH = Path(__name__).parent / 'airbnb.html'

logger.remove()
logger.add(f'airbnb-scraping/airbnb.log',
           level="WARNING",
           rotation='500kb')

logger.add(sys.stderr, level='WARNING')

def fetch_content(url:str, from_disk=False )-> str:

    if from_disk and FILEPATH.exists():
        return _restore_page_content()
    
    try:
        logger.info(f'Making request to {url}')
        response = requests.get(url, headers = {'User-agent': 'your bot 0.1'})
        response.raise_for_status()
        html_content = response.text
        _store_page_content(content=html_content)

        return html_content

    except requests.RequestException as e:
        logger.error(f"Could not fetch content from {url} du to {str(e)}")
        raise e

def average_price(html:str)->int:

    prices = []

    soup = bs(html,'html.parser')
    divs = soup.find_all('div',{'data-testid':'card-container'})

    for div in divs:
        price_node = div.find('span', class_='_1y74zjx') or div.find('span', class_='_tyxjp1')

        if not price_node:
            logger.warning(f"Couldn't find price in div {div}")
            continue
        price = re.sub(r"\D","", price_node.text)
    
        if price.isdigit():
            logger.info(f'Price found : {price}')
            prices.append(int(price))
        else:
            logger.warning(f'Price {price} is not a digit')

    return round(sum(prices)/len(prices)) if len(prices) else 0



def _store_page_content(content:str)->bool:

    logger.info("Store content in local disk")
    with open(FILEPATH,"w") as f:
        f.write(content)

    return FILEPATH.exists()

def _restore_page_content()->str:

    logger.info(f'Restore page content in local disk')

    with open(FILEPATH,'r') as f:
        return f.read()

if __name__=='__main__':
    url = sys.argv[-1]
    #url = 'https://www.airbnb.fr/s/Ouagadougou--Centre--Burkina-Faso/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2024-03-01&monthly_length=2&monthly_end_date=2024-06-01&price_filter_input_type=0&channel=EXPLORE&search_type=autocomplete_click&price_filter_num_nights=61&date_picker_type=monthly_stay&source=structured_search_input_header&query=Ouagadougou%2C%20Centre&place_id=ChIJzUSqzuyVLg4Rizt0nHlnn3k'
    html = fetch_content(url=url, from_disk=True)
    print(average_price(html=html))
