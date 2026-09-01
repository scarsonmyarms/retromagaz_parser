import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Імпортуємо ваші функції (переконайтеся, що collect_product_info працює без Selenium, див. примітку нижче)
from functions import page_down, collect_product_info

LINKS_FILE = 'products_urls_dict.json'
DATA_FILE = 'PRODUCTS_DATA.json'


def get_products_links(max_pages=46):
    """Функція збирає посилання і повертає їх список."""
    options = uc.ChromeOptions()
    options.page_load_strategy = 'eager'
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)

    driver = uc.Chrome(options=options, version_main=151)  # або без version_main, якщо оновили Chrome
    base_url = 'https://retromagaz.com/consoles-ps2'
    all_products_urls = []

    try:
        for page in range(1, max_pages + 1):
            driver.get(f'{base_url}?page={page}')
            print(f"[~] Збір посилань. Сторінка: {page}")

            wait = WebDriverWait(driver, 5)
            try:
                find_links = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'game-card__title')))
                products_urls = list(set(link.get_attribute("href") for link in find_links))

                if not products_urls:
                    break

                all_products_urls.extend(products_urls)
            except Exception as e:
                print(f"[!] Товарів на сторінці {page} не знайдено або помилка: {e}")
                break
    finally:
        driver.quit()

    # Зберігаємо у файл
    products_urls_dict = {k: v for k, v in enumerate(all_products_urls)}
    with open(LINKS_FILE, "w", encoding='utf-8') as file:
        json.dump(products_urls_dict, file, indent=4, ensure_ascii=False)

    return all_products_urls


def load_or_scrape_links():
    """Перевіряє наявність файлу і запитує користувача, що робити."""
    if os.path.exists(LINKS_FILE):
        choice = input(f"[?] Знайдено існуючий файл {LINKS_FILE}. Оновити базу посилань? (y/n): ").strip().lower()
        if choice == 'n':
            print("[+] Завантажуємо посилання з файлу...")
            with open(LINKS_FILE, 'r', encoding='utf-8') as file:
                data = json.load(file)
                # Повертаємо тільки значення (самі URL)
                return list(data.values())

    print("[+] Запускаємо браузер для збору нових посилань...")
    return get_products_links()


def main():
    # 1. Отримуємо посилання (або з файлу, або парсимо наново)
    urls = load_or_scrape_links()

    if not urls:
        print("[!] Немає посилань для обробки. Вихід.")
        return

    print(f"\n[+] Починаємо збір даних для {len(urls)} товарів.")
    print("[!] ЩОБ ЗУПИНИТИ ТА ЗБЕРЕГТИ ДАНІ — НАТИСНІТЬ Ctrl+C (або кнопку Stop у PyCharm)\n")

    products_data = []

    # 2. Збір даних у багатопотоковому режимі із перехопленням зупинки
    try:
        # max_workers=5 означає, що скрипт буде обробляти 5 товарів одночасно.
        # Можна змінити на 10, якщо сайт не блокує.
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Запускаємо задачі для кожного URL
            # ЗВЕРНІТЬ УВАГУ: ми більше не передаємо driver!
            future_to_url = {executor.submit(collect_product_info, url): url for url in urls}

            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    data = future.result()
                    if data:
                        products_data.append(data)
                        print(f"[+] Успішно зібрано: {url}")
                except Exception as e:
                    print(f"[-] Помилка при зборі {url}: {e}")

    except KeyboardInterrupt:
        # Цей блок спрацює, якщо ви примусово зупините скрипт
        print("\n\n[!!!] ЗБІР ПЕРЕРВАНО КОРИСТУВАЧЕМ. Зберігаємо те, що встигли зібрати...")

    finally:
        # Цей блок виконається ЗАВЖДИ в кінці (навіть якщо була помилка або зупинка)
        if products_data:
            print(f"[+] Збереження {len(products_data)} товарів у {DATA_FILE}...")
            with open(DATA_FILE, 'w', encoding='utf-8') as file:
                json.dump(products_data, file, indent=4, ensure_ascii=False)
            print("[+] Готово!")
        else:
            print("[-] Немає зібраних даних для збереження.")


if __name__ == '__main__':
    main()