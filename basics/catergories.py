import requests
from bs4 import BeautifulSoup as bs

URL = "https://books.toscrape.com/"

def cotegories(seuil=1):
    """
        Shows the names of categories whose number of books
        does not reach the number defined in the threshold.
    """
    with requests.Session() as session:
        response = session.get(URL)

        soup = bs(response.text, 'html.parser')


        #get all categorises with her link
        #aside = soup.find('div', class_='side_categories')

        #catergorises_link = [[c.text.strip(), c.get("href")] for c in aside.find_all('a')[1:]]
        aside = soup.select("div.side_categories a")[1:]
        catergorises_link = [[c.text.strip(), c.get("href")] for c in aside]
        #pprint(catergorises_link)

        # catergories with books number
        for cl in catergorises_link:
            bl = session.get(URL+cl[1])
            cl_soup = bs(bl.text,'html.parser')
            num = cl_soup.find('form', method='get').find('strong').text
            if int(num)<=seuil:
                print(f"La categories {cl[0]} n'a pas suffisament de livres ({num})")


if __name__=='__main__':
    cotegories(seuil=2)