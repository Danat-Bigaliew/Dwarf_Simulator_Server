import redis
import json
from backend_scripts.Game_Settings.VariablesForGameplay import update_number_for_ui

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def main_gameplay(player_key, index_item):
    current_entry_json = redis_client.get(player_key)

    if not current_entry_json:
        return {"error": "Player not connected or invalid key"}

    try:
        current_entry = json.loads(current_entry_json)

        variable_for_gameplay = current_entry.get("variables_for_gameplay")

        max_progressBars = variable_for_gameplay["max_progressBars"]
        buff_debuff_progressBars = variable_for_gameplay["buff_debuff_progressBars"]
        bag = variable_for_gameplay["tools"]["bag"]

        diamond_for_click = variable_for_gameplay["shaft_diamond_for_click"]
        market_gold_for_click = variable_for_gameplay["market_gold_for_click"]
        diamond_cell_per_click = variable_for_gameplay["market_cell_diamond_for_click"]

        buy_in_tavern = variable_for_gameplay["buy_in_tavern"]

        purchased_goods_game_data = current_entry.get("purchased_goods").get("purchased_goods_in_game_data")
        
        player_diamond = purchased_goods_game_data.get("diamond", 0)
        player_gold = purchased_goods_game_data.get("gold")

        player_happiness = purchased_goods_game_data.get("happiness", 0)
        player_strength = purchased_goods_game_data.get("strength", 0)
        player_eloquence = purchased_goods_game_data.get("eloquence", 0)

        match index_item:
            case "shaft":
                print(f"Shaft is open")
                if player_happiness >= buff_debuff_progressBars:
                    if player_diamond + diamond_for_click <= bag:
                        player_diamond += diamond_for_click

                        player_happiness -= buff_debuff_progressBars

                        if player_eloquence + buff_debuff_progressBars < max_progressBars:
                            player_eloquence += buff_debuff_progressBars
                        else:
                            player_eloquence = max_progressBars
                        
                        if player_strength + buff_debuff_progressBars < max_progressBars:
                            player_strength += buff_debuff_progressBars
                        else:
                            player_strength = max_progressBars

                    purchased_goods_game_data["diamond"] = player_diamond
                    purchased_goods_game_data["happiness"] = player_happiness
                    purchased_goods_game_data["strength"] = player_strength
                    purchased_goods_game_data["eloquence"] = player_eloquence

                    current_entry["purchased_goods"]["purchased_goods_in_game_data"] = purchased_goods_game_data

                    redis_client.set(player_key, json.dumps(current_entry))
                
                else:
                    return {"message" : "Покупка невозможна, вы устали"}

                return {
                    "message" : "Покупка совершена",
                    "player_diamond": update_number_for_ui(player_diamond),
                    "happiness" : player_happiness, 
                    "strength" : player_strength,
                    "eloquence" : player_eloquence
                }
            case "market":
                print(f"Market is open")

                if player_strength >= buff_debuff_progressBars:
                    player_gold += market_gold_for_click
                    player_diamond -= diamond_cell_per_click
                    player_strength -= buff_debuff_progressBars
                    
                    if player_happiness + buff_debuff_progressBars < max_progressBars:
                        player_happiness += buff_debuff_progressBars
                    else:
                        player_happiness = max_progressBars
                    
                    if player_eloquence + buff_debuff_progressBars < max_progressBars:
                        player_eloquence += buff_debuff_progressBars
                    else:
                        player_eloquence = max_progressBars
                
                purchased_goods_game_data["diamond"] = player_diamond
                purchased_goods_game_data["gold"] = player_gold
                purchased_goods_game_data["happiness"] = player_happiness
                purchased_goods_game_data["strength"] = player_strength
                purchased_goods_game_data["eloquence"] = player_eloquence

                current_entry["purchased_goods"]["purchased_goods_in_game_data"] = purchased_goods_game_data

                redis_client.set(player_key, json.dumps(current_entry))
 
                return {
                    "message" : "Покупка совершена",
                    "player_diamond": update_number_for_ui(player_diamond),
                    "player_gold": update_number_for_ui(player_gold),
                    "happiness" : player_happiness, 
                    "strength" : player_strength,
                    "eloquence" : player_eloquence
                }
            case "tavern":
                print(f"Shaft is open")
                if player_eloquence >= buff_debuff_progressBars:
                    player_gold -= buy_in_tavern
                    player_eloquence -= buff_debuff_progressBars

                    if player_happiness + buff_debuff_progressBars < max_progressBars:
                        player_happiness += buff_debuff_progressBars
                    else:
                        player_happiness = max_progressBars
                    
                    if player_strength + buff_debuff_progressBars < max_progressBars:
                        player_strength += buff_debuff_progressBars
                    else:
                        player_strength = max_progressBars
                    
                purchased_goods_game_data["gold"] = player_gold
                purchased_goods_game_data["happiness"] = player_happiness
                purchased_goods_game_data["strength"] = player_strength
                purchased_goods_game_data["eloquence"] = player_eloquence

                current_entry["purchased_goods"]["purchased_goods_in_game_data"] = purchased_goods_game_data

                redis_client.set(player_key, json.dumps(current_entry))
 
                return {
                    "message" : "Покупка совершена",
                    "player_diamond": update_number_for_ui(player_gold),
                    "happiness" : player_happiness, 
                    "strength" : player_strength,
                    "eloquence" : player_eloquence
                }

    except (json.JSONDecodeError, TypeError) as e:
        return {"error": f"Failed to process data: {str(e)}"}