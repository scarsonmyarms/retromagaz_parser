import gspread
import json
from decouple import config


def clean_data(data):
    """Очищення даних та фільтрація товарів без ціни"""
    cleaned = []
    for item in data:
        if item is None:
            continue

        # 1. Пропускаємо товари, де ціна None (null) або порожня
        raw_price = item.get('product_base_price')
        if raw_price is None or raw_price == '':
            continue

        try:
            # Очищаємо від пробілів (наприклад "1 500" -> "1500")
            price = str(raw_price).replace(' ', '')

            # 2. Якщо після очищення це число - зберігаємо, інакше пропускаємо
            if price.isdigit():
                item['product_base_price'] = int(price)
                cleaned.append(item)
        except Exception as e:
            print(f"Помилка опрацювання елемента: {item.get('product_name', 'Unknown')}, помилка: {e}")

    return cleaned


def upload_to_google_sheets(json_file, spreadsheet_url, sheet_name):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cleaned_data = clean_data(data)
    if not cleaned_data:
        print(f"[-] Немає валідних даних (з цінами) для завантаження на аркуш '{sheet_name}'")
        return

    token = config('JSON_KEY')
    client = gspread.service_account(filename=token)

    try:
        # Відкриття вашої існуючої таблиці за прямим посиланням
        spreadsheet = client.open_by_url(spreadsheet_url)

        # Пошук або створення потрібного аркуша
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            print(f"[~] Аркуш '{sheet_name}' не знайдено. Створюємо новий...")
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=10)

        # Формування даних
        headers = ["Название игры", "Цена", "Состояние", "Язык"]
        all_rows = [headers]

        for item in cleaned_data:
            name = item.get('product_name', '')
            condition = "Новый" if "Новий" in name else "Б/У" if "Б/У" in name else ""
            language = "Русский" if "Російська" in name or "Російські" in name else "Украинский" if "Українські" in name else "Английский" if "Англійська" in name else ""

            all_rows.append([
                name,
                item.get('product_base_price', ''),
                condition,
                language
            ])

        # Пакетний запис даних
        worksheet.clear()
        worksheet.update(values=all_rows, range_name='A1')

        # Стилізація
        worksheet.format("A1:D1", {
            "textFormat": {"bold": True},
            "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}
        })
        worksheet.columns_auto_resize(0, 3)

        print(f"[+] Дані успішно завантажені на аркуш '{sheet_name}'. Всього товарів: {len(all_rows) - 1}")

    except Exception as e:
        print(f"[-] Помилка при роботі з Google Sheets: {e}")


if __name__ == '__main__':
    # 1. Вставте сюди повне посилання на вашу створену таблицю
    TABLE_URL = "https://docs.google.com/spreadsheets/d/1PabVQZFytlfIxgaj4I1GldhovM_VuTMQZpMX2KzmPU4/edit"

    # 2. Вказуємо файл, посилання і точну назву аркуша
    upload_to_google_sheets('PRODUCTS_DATA.json', TABLE_URL, 'PS2-1')