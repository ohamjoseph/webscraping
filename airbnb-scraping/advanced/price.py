import re
from bs4 import BeautifulSoup as bs


def average_price(html: str) -> int:
    prices = []

    soup = bs(html, 'html.parser')
    divs = soup.find_all('div', {'data-testid': 'card-container'})

    for div in divs:
        price_node = div.find('span', class_='_1y74zjx') or div.find('span', class_='_tyxjp1')
        if not price_node:
            continue
        price = re.sub(r"\D", "", price_node.text)

        if price.isdigit():
            prices.append(int(price))
        else:
            ...

    return round(sum(prices) / len(prices)) if len(prices) else 0
