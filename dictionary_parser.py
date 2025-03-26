import os
import json
import time
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def load_dictionaries():
    """Загружает словари из JSON файла"""
    try:
        with open('dictionaries.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
    except Exception as e:
        print(f"🚨 Ошибка загрузки dictionaries.json: {e}")
        return []


def sanitize_filename(name):
    """Очищает имя для использования в названиях файлов"""
    return re.sub(r'[<>:"/\\|?*]', '', name).replace(' ', '_')[:50]


def get_all_words(dictionary_url):
    """Получает все слова из словаря"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    try:
        response = requests.get(dictionary_url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Универсальные селекторы для разных словарей
        word_elements = soup.select('div.article-link a, .name-list a, a.name-link, .list-group-item a, .word-item a')
        words = {elem.text.strip() for elem in word_elements if elem.text.strip()}

        # Дополнительный поиск через алфавитный указатель
        if len(words) < 10:
            alphabet_blocks = soup.find_all('div', class_=re.compile('alphabet|letters', re.I))
            for block in alphabet_blocks:
                letter_links = block.find_all('a', href=True)
                for link in letter_links:
                    letter_url = urljoin(dictionary_url, link['href'])
                    if letter_words := get_words_from_letter_page(letter_url):
                        words.update(letter_words)
                    time.sleep(1)  # Задержка между запросами

        return sorted(words) if words else None

    except Exception as e:
        print(f"Ошибка при обработке словаря {dictionary_url}: {e}")
        return None


def get_words_from_letter_page(url):
    """Извлекает слова со страницы конкретной буквы"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return {item.text.strip() for item in soup.select('.word-list li, .article-item, .article-link a') if
                item.text.strip()}
    except Exception as e:
        print(f"Ошибка при обработке страницы буквы: {e}")
        return None


def search_phrases(query, base_url, api_key, headers, pause_time):
    """Поиск фраз через API"""
    try:
        time.sleep(pause_time)
        response = requests.get(
            f"{base_url}/search",
            params={"q": query, "api_key": api_key},
            headers=headers,
            timeout=10
        )
        return response.json().get('result', {}).get('phrases', []) if response.status_code == 200 else []
    except Exception as e:
        print(f"Ошибка поиска для '{query}': {e}")
        return []


def get_phrase_description(phrase, base_url, api_key, headers, pause_time):
    """Получение описания фразы через API"""
    try:
        time.sleep(pause_time)
        response = requests.get(
            f"{base_url}/phrase",
            params={"q": phrase, "api_key": api_key},
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            result = response.json().get('result', [{}])
            return result[0] if result else None
    except Exception as e:
        print(f"Ошибка получения описания для '{phrase}': {e}")
    return None


def save_data(data, folder, filename):
    """Сохраняет данные в файл"""
    try:
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)

        if filename.endswith('.json'):
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                if isinstance(data, list):
                    f.write('\n'.join(data))
                else:
                    f.write(str(data))

        return True
    except Exception as e:
        print(f"Ошибка сохранения {filepath}: {e}")
        return False


def process_dictionary(dictionary, api_key=None):
    """Обрабатывает один словарь"""
    print(f"\n{'=' * 60}")
    print(f"📚 Словарь: {dictionary.get('title', 'Без названия')}")
    print(f"🔗 URL: {dictionary.get('url')}")

    if not dictionary.get('url'):
        print("⏭ Пропускаем - нет URL")
        return False

    # Создаем папку для словаря
    folder_name = os.path.join("BaseSlovar", sanitize_filename(dictionary.get('title', 'Unnamed_Dictionary')))
    print(f"📁 Папка: {folder_name}")

    # Получаем слова из словаря
    words = get_all_words(dictionary['url'])
    if not words:
        print("❌ Не удалось получить слова из словаря")
        return False

    print(f"🔠 Найдено слов: {len(words)}")
    print("📝 Примеры:", ', '.join(words[:3]) + (', ...' if len(words) > 3 else ''))

    # Сохраняем все слова
    save_data(words, folder_name, 'all_words.txt')

    # Обработка через API (если есть ключ)
    if api_key:
        process_with_api(words, folder_name, dictionary['url'], api_key)
    else:
        # Без API просто сохраняем слова по отдельности
        words_dir = os.path.join(folder_name, 'words')
        os.makedirs(words_dir, exist_ok=True)
        for i, word in enumerate(words, 1):
            save_data(word, words_dir, f'word_{i}.txt')

    print(f"✅ Готово! Результаты в: {folder_name}")
    return True


def process_with_api(words, folder_name, base_url, api_key):
    """Обрабатывает слова через API"""
    print("\n🔍 Начинаем обработку через API...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    pause_time = 1  # 1 запрос в секунду

    # Создаем подпапки для API результатов
    phrases_dir = os.path.join(folder_name, 'phrases')
    descriptions_dir = os.path.join(folder_name, 'descriptions')
    os.makedirs(phrases_dir, exist_ok=True)
    os.makedirs(descriptions_dir, exist_ok=True)

    api_base_url = base_url + "/api/v1-alpha" if not base_url.endswith('/') else base_url + "api/v1-alpha"

    for i, word in enumerate(words, 1):
        print(f"[{i}/{len(words)}] Обрабатываем: {word}")

        phrases = search_phrases(word, api_base_url, api_key, headers, pause_time)
        if not phrases:
            print(f"  Не найдено фраз для '{word}'")
            continue

        phrases_info = []
        descriptions = []

        for phrase in phrases:
            if desc := get_phrase_description(phrase, api_base_url, api_key, headers, pause_time):
                phrases_info.append(desc)
                if 'description' in desc:
                    descriptions.append(desc['description'])

        if phrases_info:
            # Сохраняем phrases в JSON
            save_data(phrases_info, phrases_dir, f'phrases_{i}.json')
            # Сохраняем descriptions в TXT
            save_data('\n\n'.join(descriptions), descriptions_dir, f'descriptions_{i}.txt')
            print(f"  Сохранено фраз: {len(phrases_info)}")
        else:
            print(f"  Не удалось получить описания для '{word}'")


def main():
    """Основная функция"""
    print("🔄 Загрузка словарей...")
    dictionaries = load_dictionaries()

    if not dictionaries:
        print("❌ Нет словарей для обработки")
        return

    # Создаем базовую папку
    os.makedirs("BaseSlovar", exist_ok=True)

    # Запрашиваем API ключ один раз
    api_key = input("Введите API-ключ (если нет, нажмите Enter): ").strip() or None

    print(f"\n🎯 Найдено словарей: {len(dictionaries)}")
    successful = 0

    for i, dictionary in enumerate(dictionaries, 1):
        print(f"\n{'=' * 30} Словарь {i}/{len(dictionaries)} {'=' * 30}")
        if process_dictionary(dictionary, api_key):
            successful += 1

    print(f"\n{'=' * 60}")
    print(f"🏁 Обработка завершена! Успешно обработано: {successful}/{len(dictionaries)}")
    print(f"💾 Все результаты сохранены в папке BaseSlovar")


if __name__ == "__main__":
    start_time = time.time()
    main()
    print(f"\n⏱ Общее время работы: {time.time() - start_time:.1f} секунд")