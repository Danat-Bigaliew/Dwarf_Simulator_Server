import json
import psycopg2
from flask import Flask, request, jsonify
from backend_scripts.Game_Settings.connection_BD import connection_parameters
from backend_scripts.WebSocket.WebSocketConnect import webSocket_connect

app = Flask(__name__)

def registration_user():
    data = request.get_json()

    login = data.get('loginUser')
    password = data.get('passwordUser')
    nickname = data.get('nicknameUser')

    try:
        conn = psycopg2.connect(**connection_parameters)
        print("Подключение к базе данных выполнено успешно")

        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM players WHERE login = %s AND password = %s AND nickname = %s",
            (login, password, nickname)
        )
        if cursor.fetchone() is not None:
            return jsonify({"message": "This login, password, and nickname combination already exists. Please enter different data."}), 400

        cursor.execute("SELECT 1 FROM players WHERE login = %s", (login,))
        if cursor.fetchone() is not None:
            return jsonify({"message": "This login already exists. Please enter another login."}), 400

        cursor.execute("SELECT 1 FROM players WHERE password = %s", (password,))
        if cursor.fetchone() is not None:
            return jsonify({"message": "This password already exists. Enter another password."}), 400

        cursor.execute("SELECT 1 FROM players WHERE nickname = %s", (nickname,))
        if cursor.fetchone() is not None:
            return jsonify({"message": "This nickname already exists. Enter another nickname"}), 400

        cursor.execute("SELECT id FROM players ORDER BY id DESC LIMIT 1")
        last_id_row = cursor.fetchone()
        new_id = (last_id_row[0] + 1) if last_id_row else 1

        cursor.execute(
            "INSERT INTO players (id, login, password, nickname) VALUES (%s, %s, %s, %s);",
            (new_id, login, password, nickname)
        )

        cursor.execute(
            "INSERT INTO user_game_data (player_id) VALUES (%s);",
            (new_id,)
        )

        conn.commit()

        response_string = webSocket_connect(cursor, new_id)

        cursor.close()
        conn.close()

        print("Connection closed")

        try:
            response_dict = json.loads(response_string)
            return jsonify(response_dict), 200
            
        except json.JSONDecodeError:
                response_dict = {"error": "Failed to parse response"}

    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return jsonify({"error": f"Database connection error: {e}"}), 500