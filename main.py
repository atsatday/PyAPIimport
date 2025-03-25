import requests
import json
import time

que = input("Введите фразу, которую нужно искать: ")

# Задаем базовый URL и API-ключ
base_url = "https://100-velikih-evreev.slovaronline.com/api/v1-alpha"
api_key = input("Введите API-ключ: ")  # Вставьте свой API-ключ

# Настройки лимитов
requests_per_minute = 60  # Максимальное количество запросов в минуту
pause_time = 60 / requests_per_minute  # Рассчитываем паузу между запросами

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


def search_phrases(query):
    url = f"{base_url}/search"
    params = {
        "q": query,
        "api_key": api_key
    }

    time.sleep(pause_time)  # Пауза перед запросом
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        return response.json().get('result', {}).get('phrases', [])
    else:
        print(f"Ошибка при поиске фраз: {response.status_code} - {response.text}")
        return []


def get_phrase_description(phrase):
    url = f"{base_url}/phrase"
    params = {
        "q": phrase,
        "api_key": api_key
    }

    time.sleep(pause_time)  # Пауза перед запросом
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        return response.json().get('result', [])[0]  # Получаем первое описание
    else:
        print(f"Ошибка при получении описания фразы '{phrase}': {response.status_code} - {response.text}")
        return None


def save_to_json(data, filename='phrases.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def save_only_descriptions_to_txt(phrases_info, filename='descriptions.txt'):
    with open(filename, 'w', encoding='utf-8') as f:
        for info in phrases_info:
            f.write(f"{info['description']}\n")

def save_descriptions_to_json(phrases_info, filename='descriptions.json'):
    # Извлекаем только описания
    descriptions = [{"description": info['description']} for info in phrases_info]

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(descriptions, f, ensure_ascii=False, indent=4)
# Основная логика
if __name__ == "__main__":
    query = que  # Замените на нужное слово для поиска
    phrases = search_phrases(query)

    all_phrases_info = []

    for phrase in phrases:
        description = get_phrase_description(phrase)
        if description:
            all_phrases_info.append(description)

    save_to_json(all_phrases_info)
    print("Все фразы и их описания успешно сохранены в phrases.json.")
    save_descriptions_to_json(all_phrases_info)
    print("Все описания успешно сохранены в descriptions.json.")
    save_only_descriptions_to_txt(all_phrases_info)
    print("Все описания успешно сохранены в descriptions.txt.")
