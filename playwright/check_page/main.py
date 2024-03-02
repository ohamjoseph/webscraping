from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup as bs
import sys


def run(pw, url: str, mot: str = "") -> bool:
    """
        pw : instance playwright
        url : le site web a verifier
        mot : le mot a verifier
    """
    browser = pw.chromium.launch()
    page = browser.new_page()
    page.goto(url)
    content = page.content()
    soup = bs(content, "html.parser")
    text = soup.text
    return mot.lower() in text.lower()


if __name__ == "__main__":
    # Exemple : python3 main.py https://www.google.fr/ recherche
    url, mot = sys.argv[1], sys.argv[2]
    #url = "https://www.google.fr/"
    #mot = "recherche"
    with sync_playwright() as playwright:
        print(run(playwright, url=url, mot=mot))
