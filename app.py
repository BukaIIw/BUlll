# Веб-приложение с чат-ботом, который ищет информацию в интернете
from flask import Flask, request, jsonify, send_from_directory
import json
import os
import requests
import random

# Инициализация Flask
app = Flask(__name__, static_folder='.')

# API-ключ для SerpApi (замени на свой ключ)
SERP_API_KEY = "YOUR_SERPAPI_KEY_HERE"  # Получи ключ на https://serpapi.com/

# Базовые ответы для простых фраз
responses = {
    "привет": ["Привет! Как дела?", "Здорово, привет!"],
    "как дела": ["Отлично, а у тебя?", "Норм, как у тебя дела?"],
    "что делаешь": ["Ищу инфу для тебя!", "Болтаю и шарю в интернете."],
    "пока": ["Пока-пока!", "До встречи!"],
    "кто ты": ["Я ИИ-бот, который ищет ответы в интернете!", "Твой помощник по поиску инфы!"]
}

# Файл для хранения истории диалогов
HISTORY_FILE = "chat_history.json"

# Загрузка истории диалогов
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# Сохранение истории диалогов
def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# Поиск в интернете через SerpApi
def search_web(query):
    try:
        url = f"https://serpapi.com/search.json?q={query}&api_key={SERP_API_KEY}"
        response = requests.get(url)
        data = response.json()
        # Извлекаем первый результат поиска
        if "organic_results" in data and len(data["organic_results"]) > 0:
            result = data["organic_results"][0].get("snippet", "Не нашел точного ответа.")
            return result
        return "Ничего не нашел, попробуй другой вопрос!"
    except Exception as e:
        return f"Ошибка поиска: {str(e)}"

# Получение ответа бота
def get_response(message):
    message = message.lower().strip()
    # Проверяем, есть ли ответ в словаре
    for key in responses:
        if key in message:
            return random.choice(responses[key])
    
    # Если нет в словаре, ищем в интернете
    web_result = search_web(message)
    return web_result

# Главная страница
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# Эндпоинт для обработки сообщений
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    if not user_message:
        return jsonify({'response': 'Пожалуйста, отправьте сообщение!'})
    
    # Получение ответа
    response = get_response(user_message)
    
    # Сохранение в историю
    history = load_history()
    history.append({"user": user_message, "bot": response})
    save_history(history)
    
    # Имитация самообучения: добавляем новый ответ в словарь
    if len(history) % 10 == 0:
        last_entry = history[-1]
        user_message_lower = user_message.lower().strip()
        if user_message_lower not in responses:
            responses[user_message_lower] = [response]
            print(f"Добавлен новый ответ: {user_message_lower} -> {response}")

    return jsonify({'response': response})

# Запуск сервера
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
