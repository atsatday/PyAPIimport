import requests
import json
import time
from bs4 import BeautifulSoup

def get_all_names_from_100_velikih(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        alphabet_block = soup.find('div', {'class': 'alphabet'})
        if not alphabet_block:
            print("Не удалось найти блок с алфавитом.")
            return None

        letter_links = alphabet_block.find_all('a', {'class': 'btn btn-sm btn-circle btn-white'})
        if not letter_links:
            print("Не найдены ссылки на буквы.")
            return None

        all_names = []

        for link in letter_links:
            letter_url = "https://100-velikih-evreev.slovaronline.com" + link['href']
            letter_names = get_names_from_letter_page(letter_url)
            if letter_names:
                all_names.extend(letter_names)
            time.sleep(1)  # Задержка между запросами

        return all_names

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к сайту: {e}")
        return None
    except Exception as e:
        print(f"Ошибка при обработке HTML: {e}")
        return None


def get_names_from_letter_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        name_elements = soup.select('div.article-link a')

        names = [element.text.strip() for element in name_elements if element.text.strip()]
        return names

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к странице буквы: {e}")
        return None
    except Exception as e:
        print(f"Ошибка при обработке HTML на странице буквы: {e}")
        return None


def search_phrases(query, base_url, api_key, headers, pause_time):
    url = f"{base_url}/search"
    params = {
        "q": query,
        "api_key": api_key
    }

    time.sleep(pause_time)
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        return response.json().get('result', {}).get('phrases', [])
    else:
        print(f"Ошибка при поиске фраз: {response.status_code} - {response.text}")
        return []


def get_phrase_description(phrase, base_url, api_key, headers, pause_time):
    url = f"{base_url}/phrase"
    params = {
        "q": phrase,
        "api_key": api_key
    }

    time.sleep(pause_time)
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        return response.json().get('result', [{}])[0]  # Безопасное получение первого элемента
    else:
        print(f"Ошибка при получении описания фразы '{phrase}': {response.status_code} - {response.text}")
        return None


def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def save_only_descriptions_to_txt(phrases_info, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for info in phrases_info:
            f.write(f"{info.get('description', 'Нет описания')}\n")


if __name__ == "__main__":
    # Парсинг имен
    url = "https://100-velikih-evreev.slovaronline.com"
    names = get_all_names_from_100_velikih(url)

    if not names:
        print("Не удалось получить список имен.")
        exit()

    print(f"Найдено {len(names)} имен:")
    for name in names:
        print(name)

    # Настройки API (если нужно)
    base_url = "https://100-velikih-evreev.slovaronline.com/api/v1-alpha"  # Убедитесь, что URL API корректен
    api_key = input("Введите API-ключ: ")  # Ввод API-ключа один раз
    requests_per_minute = 60
    pause_time = 60 / requests_per_minute

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    for i, name in enumerate(names, 1):
        print(f"\nОбработка {i}/{len(names)}: {name}")
        phrases = search_phrases(name, base_url, api_key, headers, pause_time)

        all_phrases_info = []  # Сбрасываем для каждого имени

        for phrase in phrases:
            description = get_phrase_description(phrase, base_url, api_key, headers, pause_time)
            if description:
                all_phrases_info.append(description)

        # Сохраняем данные с нумерацией по порядку
        if all_phrases_info:
            save_to_json(all_phrases_info, f"phrases_{i}.json")
            save_only_descriptions_to_txt(all_phrases_info, f"descriptions_{i}.txt")
            print(f"Данные сохранены в файлы phrases_{i}.json и descriptions_{i}.txt")
        else:
            print(f"Нет данных для сохранения по имени '{name}'.")

    print("\nВсе данные успешно обработаны!")