import os
import json
import sys

import requests
from datetime import datetime
from pathlib import Path
from selectolax.parser import HTMLParser
from loguru import  logger
from dotenv import load_dotenv

load_dotenv()

logger.remove()
logger.add(sys.stderr, level="DEBUG")
logger.add("amazon.log", level="WARNING", rotation="1 MB")

PRICE_FILEPATH = Path('.') / "price.json"

def write_price_to_file(price:int):

    logger.debug("Ajout de nouveau prix")

    if PRICE_FILEPATH.exists():
        with open(PRICE_FILEPATH, 'r') as f:
            data = json.load(f)
    else:
        data = []
    data.append({
        "price": price,
        "timestamp": datetime.now().isoformat()
    })

    with open(PRICE_FILEPATH,'w') as f:
        json.dump(data, f, indent=4)
def get_price_difference(current_price:int)->int:
    logger.debug("Calcule de la difference de prix")

    if PRICE_FILEPATH.exists():
        with open(PRICE_FILEPATH,"r") as f:
            data = json.load(f)

            previous_price = data[-1]['price']
    else:
        previous_price = current_price
    try:
        return round((previous_price-current_price)/previous_price *100)
    except ZeroDivisionError as e:
        logger.error(f"La valeur precedente à la valeur 0 : {e}")
        raise e

def send_alert(message):
    logger.info(f"Envoi d'une alerte avec le message: {message}")
    try:
        response = requests.post("https://api.pushover.net/1/messages.json",
                      data={
                            "token": os.environ["PUSHOVER_TOKEN"],
                            "user": os.environ["PUSHOVER_USER"],
                            "message": message
                            },
        )
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Impossible d'envoyer l'alert : {e}")
        raise e

def get_current_price(asin:str):
    proxies = {'http': os.environ["PROXY"],
            'https': os.environ["PROXY"]}

    url = f"https://www.amazon.com/dp/{asin}"
    try:
        response = requests.get(url, proxies=proxies,verify=False)
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error(f"Impossible d'accèder à l'url {url} du à : {e}")
        raise e
    # with open("amazon.html", "w") as f:
    #     f.write(html)
    html = response.text

    tree = HTMLParser(html)
    price = tree.css_first("span.a-price-symbol + span.a-price-whole").text()
    if price:
        return int(price.replace('.',''))
    err_message = f"Impossible de trouver le price sur {url}"
    logger.info(err_message)
    raise ValueError(err_message)

def main(asin:str):
    current_price = get_current_price(asin=asin)
    difference = get_price_difference(current_price=current_price)
    write_price_to_file(price=current_price)

    if difference > 0:
        send_alert(f"La price a dimunier de {difference}%")

if __name__=='__main__':
    asin = 'B00YXO5U40'
    main(asin=asin)
