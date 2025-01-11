import json
import redis
import psycopg2
from backend_scripts.Game_Settings.VariablesForGameplay import update_number_for_ui
from backend_scripts.Game_Settings.VariablesForGameplay import variable_for_gameplay
from backend_scripts.Markets.Base.GetForgeData import get_inventory
from backend_scripts.Markets.Base.GetStockExchangeData import get_promotion
from backend_scripts.Markets.Base.GetGameData import get_game_data
from backend_scripts.Game_Settings.connection_BD import connection_parameters

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

total_сonnections = 0

def webSocket_connect(cursor, target_id):
    global total_сonnections

    total_сonnections += 1

    inventory, forge_ui_data = get_inventory(cursor, target_id)
    promotions, promotion_ui_data = get_promotion(cursor, target_id)
    game_data = get_game_data(cursor, target_id)
    variables_for_gameplay = variable_for_gameplay()

    socket_name = f"Socket_{total_сonnections}"

    purchased_goods_in_inventory = {}
    purchased_goods_in_promotion = {}
    purchased_goods_in_game_data = game_data.copy()

    purchased_goods = {
        "purchased_goods_in_inventory" : purchased_goods_in_inventory,
        "purchased_goods_in_promotion" : purchased_goods_in_promotion,
        "purchased_goods_in_game_data" : purchased_goods_in_game_data
    }

    webSocket_connection = {
        "Socket name": socket_name,
        "target_id": target_id,
        "inventory": inventory,
        "promotions": promotions,
        "game_data": game_data,
        "variables_for_gameplay" : variables_for_gameplay,
        "purchased_goods" : purchased_goods
    }

    ui_data = {
        "socket_name": socket_name,
        "forge_data": forge_ui_data,
        "promotions_data": promotion_ui_data,
        "game_data": game_data
    }

    redis_client.set(socket_name, json.dumps(webSocket_connection))

    return json.dumps(ui_data)

def webSocket_disconnect(player_key):
    current_entry_json = redis_client.get(player_key)

    try:
        current_entry = json.loads(current_entry_json)
        player_id_ = current_entry.get("target_id")

        purchased_goods = current_entry.get("purchased_goods")
        purchased_goods_in_inventory = purchased_goods.get("purchased_goods_in_inventory")
        purchased_goods_in_stockExchange = purchased_goods.get("purchased_goods_in_promotion")
        purchased_goods_in_game_data = purchased_goods.get("purchased_goods_in_game_data")
        game_data = current_entry.get("game_data")

        player_diamond = purchased_goods_in_game_data["diamond"]
        player_gold = purchased_goods_in_game_data["gold"]
        player_eri = purchased_goods_in_game_data["eri"]
        player_happiness = purchased_goods_in_game_data["happiness"]
        player_strength = purchased_goods_in_game_data["strength"]
        player_eloquence = purchased_goods_in_game_data["eloquence"]

        print(f"purchased_goods_in_game_data : {purchased_goods_in_game_data}")
        print(f"game_data : {game_data}")

        if purchased_goods_in_inventory:
            connection = psycopg2.connect(**connection_parameters)
            if not connection:
                return {"error": "Failed to connect to the database."}
            
            try:
                with connection.cursor() as cursor:

                    for current_product_id, nested_dict in purchased_goods_in_inventory.items():
                        quantity_product = nested_dict.get("updated_quantity_product", 0)
                        level_product = nested_dict.get("updated_level_product", 0)
                        product_price = nested_dict.get("price_product")
                        
                        print(f"current_product_id : {current_product_id}")
                        print(f"level_product : {level_product}")

                        cursor.execute("""
                            INSERT INTO marketforge_user_products (user_id, product_id, quantity_product, level_product, product_price)
                            VALUES (%s, %s, %s, %s, %s)
                            ON CONFLICT (user_id, product_id)
                            DO UPDATE SET 
                                quantity_product = EXCLUDED.quantity_product,
                                level_product = EXCLUDED.level_product,
                                product_price = EXCLUDED.product_price;
                        """, (player_id_, current_product_id, quantity_product, level_product, product_price))

                        connection.commit()
                    print("Records inserted successfully.")

            except psycopg2.Error as e:
                print(f"Database error: {e}")
                return {"error": "Failed to execute database query."}
            finally:
                connection.close()
                print("Connection to PostgreSQL closed.")

        if purchased_goods_in_stockExchange:
            connection = psycopg2.connect(**connection_parameters)
            if not connection:
                return {"error": "Failed to connect to the database."}
            
            try:
                with connection.cursor() as cursor:

                    for current_promotion_id, nested_dict in purchased_goods_in_stockExchange.items():

                        quantity_promotion = nested_dict.get("updated_quantity_promotion", 0)

                        cursor.execute("""
                            INSERT INTO market_stockexchange_user_promotions (user_id, promotion_id, quantity_promotion)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (user_id, promotion_id)
                            DO UPDATE SET 
                                quantity_promotion = EXCLUDED.quantity_promotion
                        """, (player_id_, current_promotion_id, quantity_promotion))

                    connection.commit()
                    print("Records inserted successfully.")

            except psycopg2.Error as e:
                print(f"Database error: {e}")
                return {"error": "Failed to execute database query."}
            finally:
                connection.close()
                print("Connection to PostgreSQL closed.")
        
        if purchased_goods_in_game_data:
            connection = psycopg2.connect(**connection_parameters)
            if not connection:
                return {"error": "Failed to connect to the database."}
            
            print(f"player_gold : {player_gold}")
            
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                            UPDATE user_game_data
                            SET 
                                diamond = %s,
                                gold = %s,
                                eri = %s,
                                happiness = %s,
                                strength = %s,
                                eloquence = %s
                                WHERE player_id = %s
                                """, (player_diamond, player_gold, player_eri, player_happiness, player_strength, player_eloquence, player_id_))

                    connection.commit()
                    print("Records inserted successfully.")

            except psycopg2.Error as e:
                print(f"Database error: {e}")
                return {"error": "Failed to execute database query."}
            finally:
                connection.close()
                print("Connection to PostgreSQL closed.")
    except (json.JSONDecodeError, TypeError) as e:
        return {"error": f"Failed to process data: {str(e)}"}