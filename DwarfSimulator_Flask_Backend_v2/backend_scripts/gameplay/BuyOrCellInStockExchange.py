import redis
import json

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def buy_in_stockExchange(player_key, index_item, task):
    current_entry_json = redis_client.get(player_key)

    if not current_entry_json:
        return {"error": "Player not connected or invalid key"}

    try:
        current_entry = json.loads(current_entry_json)

        promotion = current_entry.get("promotions")
        purchased_goods = current_entry.get("purchased_goods")
        purchased_goods_in_stockExchange = purchased_goods.get("purchased_goods_in_promotion")
        purchased_goods_in_game_data = purchased_goods.get("purchased_goods_in_game_data")

        current_stockExchange_data = promotion.get(index_item)

        player_gold = purchased_goods_in_game_data.get("gold")
        price_item = current_stockExchange_data.get("price")
        quantity_product = current_stockExchange_data.get("quantity")

        match task:
            case "buyInStockExchange":
                if player_gold >= price_item:

                    quantity_product += 1
                    player_gold -= price_item

                    if index_item not in purchased_goods_in_stockExchange:
                        purchased_goods_in_stockExchange[index_item] = {
                            "updated_quantity_promotion": quantity_product
                            }
                    else:
                        purchased_goods_in_stockExchange[index_item]["updated_quantity_promotion"] = quantity_product

                    current_stockExchange_data["quantity"] = quantity_product
                    purchased_goods_in_game_data["gold"] = player_gold

                    redis_client.set(player_key, json.dumps(current_entry))

                    buy_item = {
                    "quantity_product": quantity_product,
                    "player_gold": player_gold
                    }

                    return buy_item
                else:
                    return {"message": "You do not have sufficient funds to purchase"}
            case "cellInStockExchange":
                if quantity_product > 0:

                    quantity_product -= 1
                    player_gold += price_item

                    purchased_goods_in_stockExchange[index_item]["updated_quantity_promotion"] -= quantity_product
                    current_stockExchange_data["quantity"] = quantity_product
                    purchased_goods_in_game_data["gold"] = player_gold

                    redis_client.set(player_key, json.dumps(current_entry))

                    cell_item = {
                        "quantity_product": quantity_product,
                        "player_gold": player_gold
                        }
                    print(f"cell_item : {cell_item}")

                    return cell_item
                else:
                    return {"message": "Insufficient funds to purchase"}

    except (json.JSONDecodeError, TypeError) as e:
        return {"error": f"Failed to process data: {str(e)}"}