import requests
from bs4 import BeautifulSoup
from pprint import pprint

url = "https://books.toscrape.com/"
response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')

aside = soup.find('div', class_='side_categories')
# all categories
categories_div = aside.find("ul").find('li').find('ul')
categories = [el.text.strip() for el in categories_div.children if el.name]
pprint(f'categories:{categories}')
print()
#all images
images_div = soup.find('section').find_all('img')
images = [img.get('src') for img in images_div]

pprint(f'images: {images}')
print()

# all titles
"""
articles = soup.find_all("article", class_="product_pod")
h3_liste= [link.find('h3') for link in articles]
titles = [h3.find("a").get('title') for h3 in h3_liste]

"""

titles =[el.get('title') for el in soup.find_all('a', title=True)]
pprint(f'titles: {titles}')



