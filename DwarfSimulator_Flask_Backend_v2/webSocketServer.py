import json
import redis
import asyncio
import threading
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from backend_scripts.gameplay.BuyInForge import buy_in_forge
from backend_scripts.Game_Settings.VariablesForGameplay import variable_for_gameplay
from backend_scripts.gameplay.BuyOrCellInStockExchange import buy_in_stockExchange
from backend_scripts.WebSocket.WebSocketConnect import webSocket_disconnect
from backend_scripts.gameplay.MainGameplay_Clicker import main_gameplay
from mainTimer import start_timer

app = FastAPI()
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

active_connections = []

async def timer_message_callback(message):
    if not isinstance(message, str):
        if active_connections:
            for websocket in active_connections:
                try:
                    await websocket.send_text(json.dumps({"message": message}))
                except Exception as e:
                    print(f"Ошибка при отправке сообщения пользователю: {e}")
        else:
            print("Нет активных подключений. Сообщение не отправлено.")
    else:
        print(f"Таймер сообщает: {message}")

def run_timer():
    asyncio.run(start_timer(timer_message_callback))

timer_thread = threading.Thread(target=run_timer, daemon=True)
timer_thread.start()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Обработка WebSocket соединений."""
    await websocket.accept()
    print("Клиент подключен")
    active_connections.append(websocket)
    variable_for_gameplay()
    player_key = None

    try:
        while True:
            message = await websocket.receive_text()
            try:
                data = json.loads(message)
                if isinstance(data, dict) and len(data) == 1:
                    player_key, message = next(iter(data.items()))
                    if isinstance(message, dict) and len(message) == 1:
                        task, index_item = next(iter(message.items()))

                        if task == "MainGamePlay":
                            response = main_gameplay(player_key, index_item)
                        elif task == "buyInForge":
                            response = buy_in_forge(player_key, index_item)
                        elif task in ["buyInStockExchange", "cellInStockExchange"]:
                            response = buy_in_stockExchange(player_key, index_item, task)
                        else:
                            response = {"error": "Unknown task"}

                        await websocket.send_text(json.dumps(response))
                    else:
                        await websocket.send_text(json.dumps({"error": "Invalid inner dictionary structure"}))
                else:
                    await websocket.send_text(json.dumps({"error": "Invalid JSON structure"}))
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Invalid JSON format"}))
    except WebSocketDisconnect:
        if player_key:
            webSocket_disconnect(player_key)
            redis_client.delete(player_key)
            print(f"Клиент с ключом '{player_key}' отключился")
        else:
            print("Клиент отключился ничего не сделав")
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)
        print("Подключение удалено")