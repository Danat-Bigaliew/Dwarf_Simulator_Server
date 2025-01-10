import json
import psycopg2
from flask import Flask, request, jsonify
from backend_scripts.Game_Settings.connection_BD import connection_parameters
from backend_scripts.WebSocket.WebSocketConnect import webSocket_connect

app = Flask(__name__)

def authorization_user():
    data = request.get_json()

    login = data.get('loginUser')
    password = data.get('passwordUser')
    nickname = data.get('nicknameUser')

    try:
        conn = psycopg2.connect(**connection_parameters)
        print("Подключение к базе данных выполнено успешно")

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id
            FROM players
            WHERE login = %s AND password = %s AND nickname = %s
            """,
            (login, password, nickname)
        )
        user_data = cursor.fetchone()

        if user_data:
            user_id = user_data[0]
            print(f"Пользователь найден: ID = {user_id}")

            response_string = webSocket_connect(cursor, user_id)

            try:
                response_dict = json.loads(response_string)
                return jsonify(response_dict), 200
            
            except json.JSONDecodeError:
                response_dict = {"error": "Failed to parse response"}

            cursor.close()
            conn.close()
        else:
            cursor.close()
            conn.close()
            return jsonify({"error": "Пользователь с указанными данными не существует"}), 404

    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return jsonify({"error": f"Database connection error: {e}"}), 500