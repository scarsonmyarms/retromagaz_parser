import re
import time as tm
from bs4 import BeautifulSoup


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

def collect_product_info(driver, url=''):

    driver.switch_to.new_window('tab')

    tm.sleep(3)
    driver.get(url=url)
    tm.sleep(3)

    page_source = str(driver.page_source)
    soup = BeautifulSoup(page_source, 'lxml')

    product_name = soup.find('p', class_='h1').text.strip()
    print(product_name)

    try:
        price_info = soup.find('span', class_='price')
        price = price_info.text.strip().replace("за ", "")
        print(price)
    except Exception as e:
        print(f"посилка при парсингу {url}: {e}")
        price = None

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    product_data = (
        {
            'product_name': product_name,
            'product_base_price': price,
        }
    )

    # driver.close()
    # driver.switch_to.window(driver.window_handles[0])

    return product_data
