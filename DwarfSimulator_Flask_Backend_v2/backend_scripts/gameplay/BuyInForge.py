import redis
import json
from backend_scripts.Game_Settings.VariablesForGameplay import update_diamond_click
from backend_scripts.Game_Settings.VariablesForGameplay import update_progressBars_variable
from backend_scripts.Game_Settings.VariablesForGameplay import update_number_for_ui
from backend_scripts.Game_Settings.VariablesForGameplay import update_speed_anim
from backend_scripts.Game_Settings.VariablesForGameplay import update_bag

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def buy_in_forge(player_key, index_item):
    current_entry_json = redis_client.get(player_key)

    if not current_entry_json:
        return {"error": "Player not connected or invalid key"}

    try:
        current_entry = json.loads(current_entry_json)

        inventory = current_entry.get("inventory")
        game_data = current_entry.get("game_data")
        
        purchased_goods = current_entry.get("purchased_goods")
        purchased_goods_in_inventory = purchased_goods.get("purchased_goods_in_inventory")
        purchased_goods_in_game_data = purchased_goods.get("purchased_goods_in_game_data")

        current_forge_data = inventory.get(index_item)

        player_gold = purchased_goods_in_game_data.get("gold")
        price_item = current_forge_data.get("price_product")
        quantity_product = current_forge_data.get("quantity_product")
        max_quantity_product = current_forge_data.get("max_quantity_product")
        level_product = current_forge_data.get("level_product")
        max_level_product = current_forge_data.get("max_level_product")
        ui_payButton = "Купить"

        if player_gold >= price_item:
            if quantity_product < max_quantity_product:
                player_gold -= price_item
                quantity_product += 1

                if quantity_product < max_quantity_product:
                    ui_payButton = "Купить"
                    next_price_item = price_item
                else:
                    next_price_item = (level_product + 1) * price_item

                    ui_payButton = f"Lvl: {level_product}"
                    
                update_variable_for_gameplay(index_item, current_entry, level_product, player_key)

                if index_item not in purchased_goods_in_inventory:

                    purchased_goods_in_inventory[index_item] = {
                        "updated_quantity_product": quantity_product,
                        "updated_level_product" : level_product,
                        "price_product" : next_price_item
                    }
                else:
                    purchased_goods_in_inventory[index_item]["updated_quantity_product"] = quantity_product
                
                purchased_goods["purchased_goods_in_inventory"] = purchased_goods_in_inventory
                purchased_goods["purchased_goods_in_game_data"]["gold"] = player_gold

                current_forge_data["quantity_product"] = quantity_product
                current_forge_data["price_product"] = next_price_item
                game_data["gold"] = player_gold

                redis_client.set(player_key, json.dumps(current_entry))
                
                buy_item = {
                    "quantity_product": current_forge_data["quantity_product"],
                    "player_gold": game_data["gold"],
                    "price": update_number_for_ui(next_price_item),
                    "ui_payButton" : ui_payButton
                }

                return buy_item
            elif quantity_product == max_quantity_product and level_product < max_level_product:
                if player_gold >= (price_item * level_product):
                    player_gold -= price_item * level_product
                    level_product += 1

                    if level_product < max_level_product:
                        next_price_item = (level_product + 1) * price_item
                        
                        ui_payButton = f"Lvl: {level_product}"
                    else:
                        next_price_item = ""
                        ui_payButton = "MAX"
                    
                    update_variable_for_gameplay(index_item, current_entry, level_product, player_key)
                    
                    if index_item not in purchased_goods_in_inventory:
                        purchased_goods_in_inventory[index_item] = {
                        "updated_quantity_product": quantity_product,
                        "updated_level_product" : level_product,
                        "price_product" : next_price_item
                        }
                    else:
                        purchased_goods_in_inventory[index_item]["updated_level_product"] = level_product
                        purchased_goods_in_inventory[index_item]["price_product"] = next_price_item
                    
                    purchased_goods["purchased_goods_in_inventory"] = purchased_goods_in_inventory
                    purchased_goods["purchased_goods_in_game_data"]["gold"] = player_gold

                    current_forge_data["level_product"] = level_product
                    current_forge_data["price_product"] = next_price_item
                    game_data["gold"] = player_gold

                    redis_client.set(player_key, json.dumps(current_entry))

                    print(f"current_forge_data price_product : {current_forge_data["price_product"]}")
                    
                    update_item = {
                        "player_gold": game_data["gold"],
                        "price": update_number_for_ui(next_price_item),
                        "ui_payButton" : ui_payButton
                    }

                    return update_item
                else:
                    return {"error": "You do not have sufficient funds to purchase"}
        else:
            return {"error": "Insufficient gold to purchase item"}

    except (json.JSONDecodeError, TypeError) as e:
        return {"error": f"Failed to process data: {str(e)}"}
    
def update_variable_for_gameplay(index_item, current_entry, level_product, player_key):
    variables_for_gameplay = current_entry.get("variables_for_gameplay")
    tools = variables_for_gameplay.get("tools")
    
    max_value_bag = tools["bag"]
    diamond_click = variables_for_gameplay["shaft_diamond_for_click"]
    progress_bars = variables_for_gameplay["buff_debuff_progressBars"]
    speed_animation = variables_for_gameplay["speed_animation"]

    match(index_item):
        case "1":
            diamond_click = update_diamond_click(tools["pick"], level_product, diamond_click)
        case "2":
            max_value_bag = update_bag(max_value_bag, level_product)
        case "3":
            diamond_click = update_diamond_click(tools["shovel"], level_product, diamond_click)
        case "4":
            diamond_click = update_diamond_click(tools["hammer"], level_product, diamond_click)
        case "5":
            progress_bars = update_progressBars_variable(tools["wooden_spacers"], level_product, progress_bars)
        case "6":
            speed_animation = update_speed_anim(level_product, speed_animation)
        case "7":
            progress_bars = update_progressBars_variable(tools["boots"], level_product, progress_bars)

    tools["bag"] = max_value_bag
    variables_for_gameplay["shaft_diamond_for_click"] = diamond_click
    variables_for_gameplay["buff_debuff_progressBars"] = progress_bars
    variables_for_gameplay["speed_animation"] = speed_animation

    current_entry["variables_for_gameplay"] = variables_for_gameplay
    variables_for_gameplay["tools"] = tools

    redis_client.set(player_key, json.dumps(current_entry))
    variables_for_gameplay = current_entry.get("variables_for_gameplay")