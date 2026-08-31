import json
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from functions import page_down, collect_product_info


def get_products_links(max_pages=46):
    # Оптимізація 1: Налаштування драйвера для швидкості
    options = uc.ChromeOptions()
    options.page_load_strategy = 'eager'  # Не чекаємо повного завантаження всіх скриптів/картинок

    # Вимикаємо завантаження зображень
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    driver = uc.Chrome(options=options)

    base_url = 'https://retromagaz.com/games-switch'
    all_products_urls = []

    for page in range(1, max_pages + 1):
        current_url = f'{base_url}?page={page}'
        driver.get(current_url)
        print(f"Обробка сторінки: {driver.current_url}")

        try:
            # Оптимізація 2: Розумне очікування замість time.sleep()
            # Чекаємо до 5 секунд, поки не з'являться картки товарів
            wait = WebDriverWait(driver, 5)
            find_links = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'game-card__title')))

            products_urls = list(set(link.get_attribute("href") for link in find_links))

            if not products_urls:
                print(f"[!] На сторінці {page} немає товарів (кінець пагінації)")
                break

            all_products_urls.extend(products_urls)
            print(f'[+] Зібрано {len(products_urls)} посилань з сторінки {page}')

        except Exception as e:
            print(f'[!] Помилка при зборі посилань на сторінці {page}: {e}')
            break  # Або continue, якщо сайт іноді "блимає"

    # Оптимізація 3: Виправлено логіку запису файлів
    products_urls_dict = {k: v for k, v in enumerate(all_products_urls)}

    with open('products_urls_dict.json', "w", encoding='utf-8') as file:
        json.dump(products_urls_dict, file, indent=4, ensure_ascii=False)

    print(f"Всього зібрано посилань: {len(all_products_urls)}. Починаємо збір даних...")

    products_data = []

    # Збір даних по кожному товару
    for url in all_products_urls:
        try:
            data = collect_product_info(driver=driver, url=url)
            products_data.append(data)
        except Exception as e:
            print(f"[!] Помилка збору даних для {url}: {e}")

    with open('PRODUCTS_DATA.json', 'w', encoding='utf-8') as file:
        json.dump(products_data, file, indent=4, ensure_ascii=False)

    driver.quit()


def main():
    get_products_links()


if __name__ == '__main__':
    main()