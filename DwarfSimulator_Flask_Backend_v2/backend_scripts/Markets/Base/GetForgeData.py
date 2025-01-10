from backend_scripts.Game_Settings.VariablesForGameplay import update_number_for_ui

def get_inventory(cursor, target_id):
    try:
        cursor.execute(
            """
            SELECT 
                mf.product_id AS product_id,
                mf.title AS title,
                mf.description AS description,
                mf.quantity AS quantity_product,
                mf.max_quantity AS max_quantity,
                mf.level AS level_product,
                mf.max_level AS max_level,
                mf.price AS price
            FROM 
                market_forge AS mf
            """
        )
        forge_products = cursor.fetchall()

        inventory = {}
        all_level = {}
        all_quantity = {}
        all_price = {}

        for record in forge_products:
            product_id = record[0]
            title = record[1]
            description = record[2]
            quantity_product = record[3]
            max_quantity = record[4]
            level_product = record[5]
            max_level = record[6]
            price = record[7]

            inventory[product_id] = {
                "quantity_product": quantity_product,
                "max_quantity_product": max_quantity,
                "level_product": level_product,
                "max_level_product": max_level,
                "price_product": price
            }

            all_level[product_id] = level_product
            all_quantity[product_id] = quantity_product
            all_price[product_id] = price

        cursor.execute(
            """
            SELECT 
                uf.product_id AS product_id,
                uf.quantity_product AS user_quantity_product,
                uf.level_product AS user_level_product,
                uf.product_price AS user_price_product
            FROM 
                marketforge_user_products AS uf
            WHERE 
                uf.user_id = %s
            """,
            (target_id,)
        )
        user_products = cursor.fetchall()

        for record in user_products:
            product_id = record[0]
            user_quantity_product = record[1]
            user_level_product = record[2]
            user_price_product = record[3]

            if product_id in inventory:
                user_level_product += 1
                inventory[product_id]["quantity_product"] = user_quantity_product
                inventory[product_id]["level_product"] = user_level_product
                inventory[product_id]["price_product"] = user_price_product

                if all_level[product_id] < user_level_product:
                    all_level[product_id] = user_level_product

                if all_quantity[product_id] < user_quantity_product:
                    all_quantity[product_id] = user_quantity_product

                if all_price[product_id] < user_price_product:
                    all_price[product_id] = user_price_product

        sorted_inventory = dict(sorted(inventory.items(), key=lambda item: int(item[0])))

        cursor.execute(
            """
            SELECT 
                product_id,
                title,
                description,
                max_quantity,
                max_level,
                price
            FROM 
                market_forge
            """
        )
        forge_records = cursor.fetchall()

        forge_ui_data = {}
        for record in forge_records:
            product_id = record[0]
            title = record[1]
            description = record[2]
            max_quantity = record[3]
            max_level = record[4]
            price = sorted_inventory[product_id]["price_product"]
            level_product = sorted_inventory[product_id]["level_product"]

            price_for_ui = update_number_for_ui(price)
            
            if (
                product_id in sorted_inventory
                and sorted_inventory[product_id]["quantity_product"] < max_quantity
            ):
                level_value = "Купить"
            elif (
                product_id in sorted_inventory
                and sorted_inventory[product_id]["quantity_product"] == max_quantity
                and sorted_inventory[product_id]["level_product"] < max_level
            ):
                level_value = f"Lvl: {all_level.get(product_id, 0)}"
            elif (
                product_id in sorted_inventory
                and sorted_inventory[product_id]["quantity_product"] == max_quantity
                and sorted_inventory[product_id]["level_product"] == max_level
            ):
                level_value = "MAX"

            forge_ui_data[product_id] = {
                'title': title,
                'description': description,
                'price_for_ui' : price_for_ui,
                'level': level_value
            }

        return sorted_inventory, forge_ui_data

    except Exception as e:
        print(f"Error in get_inventory: {e}")
        return {}, {}