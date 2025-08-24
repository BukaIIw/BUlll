from flask import Flask, request, jsonify, send_from_directory
import json
import os
from googlesearch import search
from datetime import datetime

# Инициализация Flask
app = Flask(__name__, static_folder='.')

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

# Поиск в интернете через googlesearch-python
def search_web(query):
    try:
        # Поиск первых 3 результатов
        results = list(search(query, num_results=3, lang="ru"))
        if results:
            return f"Найденные ссылки: {', '.join(results)}. Посмотри там!"
        return "Ничего не нашел, попробуй другой вопрос!"
    except Exception as e:
        return f"Ошибка поиска: {str(e)}"

# Обучение на основе истории
def train_from_history(message, response):
    history = load_history()
    user_message_lower = message.lower().strip()
    # Добавляем новый ответ в историю
    history.append({"user": user_message_lower, "bot": response, "timestamp": datetime.now().isoformat()})
    save_history(history)
    return history

# Эндпоинт для обработки сообщений
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    if not user_message:
        return jsonify({'response': 'Пожалуйста, отправьте сообщение!'})
    
    # Поиск ответа в интернете
    web_response = search_web(user_message)
    
    # Обучение на основе текущего запроса и ответа
    history = train_from_history(user_message, web_response)
    
    # Улучшение ответа на основе предыдущих диалогов
    improved_response = improve_response(user_message, history)
    
    return jsonify({'response': improved_response})

# Улучшение ответа на основе истории
def improve_response(message, history):
    message_lower = message.lower().strip()
    similar_responses = []
    
    for entry in history[-10:]:  # Берем последние 10 записей для анализа
        if message_lower in entry["user"]:
            similar_responses.append(entry["bot"])
    
    if similar_responses:
        return f"На основе прошлого: {random.choice(similar_responses)}. Также: {search_web(message)}"
    return search_web(message)

import random
# Главная страница
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# Запуск сервера
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
