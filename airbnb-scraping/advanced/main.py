from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup as bs
import webbrowser

from datetime import datetime
from dateutil.relativedelta import relativedelta
from price import average_price

SBR_WS_CDP = 'wss://brd-customer-hl_b80a27e6-zone-scraping_browser1:2w444ddbtzfi@brd.superproxy.io:9222'
def debug_view(page):
    client = page.context.new_cdp_session(page)
    frame_tree = client.send('Page.getFrameTree', {})
    frame_id = frame_tree['frameTree']['frame']['id']
    inspect = client.send('Page.inspect', {'frameId': frame_id})
    inspect_url = inspect['url']
    print('Inspect session at', inspect_url)
    webbrowser.open(inspect_url)

def route_intercept(route):
    if route.request.resource_type == "image":
        return route.abort()
    return route.continue_()

def run(pw, city:str, bright_data:bool=False, headless:bool=True):
    print("Connecting Scraping Browser")
    if bright_data:
        browsers = pw.chromium.connect_over_cdp(SBR_WS_CDP)
    else:
        browsers = pw.chromium.launch(headless=headless)

    context = browsers.new_context()
    context.set_default_timeout(60000)
    page = context.new_page()
    #page.route("**/*", route_intercept)

    if bright_data and not headless:
        debug_view(page)

    url = f'https://www.airbnb.fr/'
    #url = "https://www.airbnb.fr/s/Ouagadougou--Centre--Burkina-Faso/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2024-03-01&monthly_length=1&monthly_end_date=2024-06-01&price_filter_input_type=0&channel=EXPLORE&query=Ouagadougou%2C%20Centre&place_id=ChIJzUSqzuyVLg4Rizt0nHlnn3k&date_picker_type=monthly_stay&adults=1&source=structured_search_input_header&search_type=autocomplete_click"

    page.goto(url)
    page.get_by_role("button", name="Continuer sans accepter").click()
    page.get_by_test_id("structured-search-input-field-query").click()
    page.get_by_test_id("structured-search-input-field-query").fill(city)
    page.get_by_test_id("option-0").click()

    page.get_by_test_id("expanded-searchbar-dates-months-tab").click()
    page.locator(".d1u68d5p").first.click()
    page.get_by_test_id("structured-search-input-field-guests-button").click()
    page.get_by_test_id("stepper-adults-increase-button").click()
    page.get_by_test_id("structured-search-input-search-button").click()
    #
    # content = page.content()
    # soup = bs(content, 'html.parser')
    #
    # print(soup.prettify())
    # num_page = 0
    # while True:
    #     num_page += 1
    #     print(num_page)
    #     next_button = page.get_by_label("Suivant", exact=True)
    #     if next_button.get_attribute("aria-disabled") == 'true':
    #         break
    #     next_button.click()
    #     page.wait_for_timeout(1000)


    today = datetime.today()
    for i in range(1, 13):
        next_month = today + relativedelta(months=i, day=1)
        next_month_str = next_month.strftime('%d/%m/%Y')
        page.wait_for_timeout(2000)

        html = page.content()
        average = average_price(html = html)
        print(f"Average price for {next_month_str} is : {average}")
        page.get_by_test_id("little-search").click()
        page.get_by_role("button").filter(has_text="Modifier").click()
        page.wait_for_timeout(800)
        page.get_by_test_id(f"calendar-day-{next_month_str}").last.click()
        page.locator("button:has-text('Appliquer')").click()
        page.wait_for_timeout(400)
        page.get_by_test_id("structured-search-input-search-button").click()
        page.wait_for_timeout(400)

    browsers.close()

if __name__ == '__main__':
    with sync_playwright() as playwright:
        run(playwright,
            city="Ouagadougou",
            bright_data=False,
            headless=True)
