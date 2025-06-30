import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from decouple import config


def clean_data(data):
    """Очищення даних від null и перетворення цін в числа"""
    cleaned = []
    for item in data:
        if item is None:
            continue
        try:
            # Видаляємо пробіли в цінах та перетворюємо в число
            price = item.get('product_base_price', '').replace(' ', '')
            if price.isdigit():
                item['product_base_price'] = int(price)
            cleaned.append(item)
        except Exception as e:
            print(f"Помилка опрацювання елемента: {item}, помилка: {e}")
    return cleaned


def upload_to_google_sheets(json_file, spreadsheet_name):
    # 1. Загрузка и очищення даних
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cleaned_data = clean_data(data)
    if not cleaned_data:
        print("Немає даних для завантаження")
        return

    # 2. Авторизація в Google Sheets API
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]

    token = config('JSON_KEY') # це JSON-ключ із .env

    # Вкажіть шлях до вашого JSON-ключа сервісного аккаунта
    creds = ServiceAccountCredentials.from_json_keyfile_name(token, scope)
    client = gspread.authorize(creds)

    try:
        # 3. Відкриття та створення таблиці
        try:
            spreadsheet = client.open(spreadsheet_name)
        except gspread.SpreadsheetNotFound:
            spreadsheet = client.create(spreadsheet_name)

        # 4. Робота с листом
        try:
            worksheet = spreadsheet.worksheet("prervirka") # тут назва листа
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title="perevirka", rows=1000, cols=10) # тут назва листа

        # 5. Підготовка даних
        headers = ["Название игры", "Цена", "Состояние", "Язык"]
        rows = []

        for item in cleaned_data:
            name = item.get('product_name', '')

            # Отримуємо стан (Новый/Б/У)
            condition = "Новый" if "Новий" in name else "Б/У" if "Б/У" in name else ""

            # Отримуємо мову
            language = "Русский" if "Російська" in name or "Російські" in name else "Украинский" if "Українські" in name else "Английский" if "Англійська" in name else ""

            row = [
                name,
                item.get('product_base_price', ''),
                condition,
                language
            ]
            rows.append(row)

        # 6. Запис даних
        worksheet.clear()
        worksheet.append_row(headers)
        worksheet.append_rows(rows)

        # 7. Форматування
        worksheet.format("A1:D1", {
            "textFormat": {"bold": True},
            "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9}
        })

        # Автонастройка ширини столбців
        worksheet.columns_auto_resize(0, 3)

        print(f"Данные успешно загружены в таблицу: {spreadsheet_name}")
        print(f"Ссылка на таблицу: https://docs.google.com/spreadsheets/d/{spreadsheet.id}")

    except Exception as e:
        print(f"Ошибка при работе с Google Sheets: {e}")


# Використання
if __name__ == '__main__':
    upload_to_google_sheets('products_data.json', 'retromagaz parser')