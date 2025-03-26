import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin
import time
from random import uniform


def get_dictionaries(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Добавляем случайную задержку от 1 до 3 секунд перед запросом
        time.sleep(uniform(1, 3))

        print(f"Запрашиваю страницу: {url}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        dictionaries = []

        # Находим таблицу со словарями
        table = soup.find('table', class_='table')
        if not table:
            print("Не найдена таблица со словарями")
            return []

        # Парсим строки таблицы (пропускаем заголовок)
        rows = table.find_all('tr')[1:]  # пропускаем первый tr (заголовок)

        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 2:  # Проверяем, что есть хотя бы 2 колонки
                # Название и ссылка
                link = cols[1].find('a')
                if link:
                    title = link.get('title', link.text.strip())
                    href = link.get('href')

                    # Категории
                    categories = []
                    category_tags = cols[2].find_all('a')
                    for tag in category_tags:
                        categories.append(tag.text.strip())

                    # Автор (может быть пустым)
                    author = cols[3].text.strip() if len(cols) > 3 else ""

                    # Количество слов
                    word_count = cols[4].text.strip() if len(cols) > 4 else ""

                    # Формируем полный URL
                    full_url = urljoin('https:', href) if href.startswith('//') else urljoin(url, href)

                    dictionaries.append({
                        'title': title,
                        'url': full_url,
                        'categories': categories,
                        'author': author,
                        'word_count': word_count
                    })

        return dictionaries

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return []


def save_to_json(data, filename='dictionaries.json'):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Данные успешно сохранены в {filename}")
    except Exception as e:
        print(f"Ошибка при сохранении в JSON: {e}")


if __name__ == '__main__':
    target_url = 'https://slovaronline.com/dictionaries'
    dictionaries_list = get_dictionaries(target_url)

    if dictionaries_list:
        save_to_json(dictionaries_list)
        print(f"Найдено {len(dictionaries_list)} словарей.")
        print("Пример первой записи:")
        print(json.dumps(dictionaries_list[0], ensure_ascii=False, indent=2))
    else:
        print("Не удалось получить список словарей.")
