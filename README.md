# PyAPIimport
Этот код написан на Python и предназначен для поиска фраз через API.  А в общем, код позволяет пользователю искать фразы через API *.slovaronline.com, получать их описания и сохранять эти данные в формате JSON и текстовом формате. Он также учитывает лимиты на количество запросов, добавляя паузы между ними.

А вот и объяснение кода

▍Импорт библиотек

import requests
import json
import time

- requests: используется для выполнения HTTP-запросов.
- json: для работы с JSON-данными.
- time: для управления временем (например, для пауз между запросами).

▍Ввод данных

que = input("Введите фразу, которую нужно искать: ")
api_key = input("Введите API-ключ: ")

- Пользователь вводит фразу для поиска и API-ключ.

▍Настройки

base_url = "https://100-velikih-evreev.slovaronline.com/api/v1-alpha"
requests_per_minute = 60pause_time = 60 / requests_per_minute

- base_url: базовый URL для API.- requests_per_minute: максимальное количество запросов, которые можно отправить в минуту (60).
- pause_time: время паузы между запросами для соблюдения лимита.

▍Заголовки

headers = {    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

- Заголовок User-Agent, который помогает избежать блокировок со стороны сервера.

▍Функция поиска фраз

def search_phrases(query):
    ...

- Отправляет GET-запрос на поиск фраз и возвращает список найденных фраз.

▍Функция получения описания фразы

def get_phrase_description(phrase):
    ...

- Отправляет GET-запрос для получения описания конкретной фразы и возвращает это описание.

▍Сохранение данных
def save_to_json(data, filename='phrases.json'):
    ...

- Сохраняет данные в формате JSON в указанный файл.

def save_only_descriptions_to_txt(phrases_info, filename='descriptions.txt'):
    ...

- Сохраняет только описания фраз в текстовый файл.

def save_descriptions_to_json(phrases_info, filename='descriptions.json'):
    ...

- Сохраняет только описания фраз в формате JSON.

▍Основная логика

if name == "__main__":
    ...

- Запускает основную логику программы: принимает ввод пользователя, выполняет поиск фраз, получает их описания и сохраняет результаты в файлы.
