from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup as bs


html = ''
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://faso7.com/?s=Vole")
    page.get_by_role("button", name="Refuser").click()
    page.get_by_label("Fermer").click()
    page.wait_for_timeout(2000)
    html = page.content()
    



soup = bs(html,"html.parser")
container = soup.find("div", class_="container-wrapper")

titles_nodes = container.select("h2.post-title")

titles = [title.text for title in titles_nodes]

print(titles)