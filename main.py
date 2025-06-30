import json
import time

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from functions import page_down
from functions import collect_product_info


def get_products_links(max_pages = 46):
    driver = uc.Chrome()
    driver.implicitly_wait(5)

    # вставляємо посилання на сторінку яку будемо парсити
    base_url = 'https://retromagaz.com/games-switch'
    # вставляємо посилання на сторінку яку будемо парсити
    driver.get(url='https://retromagaz.com/games-switch')
    time.sleep(2)

    page_down(driver=driver)
    time.sleep(2)

    print(driver.current_url)

    all_products_urls = []

    for page in range(1, max_pages + 1):
        current_url = f'{base_url}?page={page}'
        driver.get(current_url)
        print(driver.current_url)
        time.sleep(2)

        try:
            find_links = driver.find_elements(By.CLASS_NAME, 'game-card__title')
            products_urls = list(set(f'{link.get_attribute("href")}' for link in find_links))

            if not products_urls:
                print(f"[!] На сторінці {page} немає товарів (кінець пагінації?)")
                break

            all_products_urls.extend(products_urls)
            print(f'[+] Зібрані посилання з сторінки {page}')

        except Exception as e:
            print(f'[!] посилка при зборі посилань на сторінці {page}: {e}')
            continue

    # Зберігаємо посилання в JSON
    products_urls_dict = {}

    for k, v in enumerate(all_products_urls):
        products_urls_dict.update({k: v})

    with open('products_urls_dict.json', "w", encoding='utf-8') as file:
        json.dump(products_urls_dict, file, indent=4, ensure_ascii=False)

        products_data = []

        for url in all_products_urls:
            data = collect_product_info(driver=driver, url=url)
            time.sleep(2)
            products_data.append(data)

        with open('PRODUCTS_DATA.json', 'w', encoding='utf-8') as file:
            json.dump(products_data, file, indent=4, ensure_ascii=False)

        driver.close()
        driver.quit()

def main():
    get_products_links()

if __name__ == '__main__':
    main()