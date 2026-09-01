import re
import time as tm
from bs4 import BeautifulSoup
import requests


def page_down(driver):
    driver.execute_script('''
                            const scrollStep = 200; // Розмір кроку прокрутки (в пікселях)
                            const scrollInterval = 100; // Інтервал між кроками (в мілісекундах)

                            const scrollHeight = document.documentElement.scrollHeight;
                            let currentPosition = 0;
                            const interval = setInterval(() => {
                                window.scrollBy(0, scrollStep);
                                currentPosition += scrollStep;

                                if (currentPosition >= scrollHeight) {
                                    clearInterval(interval);
                                }
                            }, scrollInterval);
                        ''')


# Видаліть аргумент driver з функції
def collect_product_info(url):
    # Додаємо заголовки, щоб сайт думав, що ми звичайний користувач
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    # Завантажуємо сторінку миттєво
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()  # Перевіряє чи немає помилки 404/500

    # Парсимо
    soup = BeautifulSoup(response.text, 'lxml')

    product_name = soup.find('p', class_='h1').text.strip()
    print(product_name)

    try:
        price_info = soup.find('span', class_='price')
        price = price_info.text.strip().replace("за ", "")
        print(price)
    except Exception as e:
        print(f"посилка при парсингу {url}: {e}")
        price = None

    product_data = (
        {
            'product_name': product_name,
            'product_base_price': price,
        }
    )


    return product_data
