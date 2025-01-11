import requests
import psycopg2
from backend_scripts.Game_Settings.connection_BD import connection_parameters

def get_promotion(cursor, target_id):
    try:
        cursor.execute(
            """
            SELECT 
                up.promotion_id AS promotion_id,
                up.quantity_promotion AS quantity,
                se.price AS price
            FROM 
                market_stockexchange_user_promotions AS up
            LEFT JOIN 
                market_stockexchange AS se 
            ON 
                up.promotion_id = se.promotion_id
            WHERE 
                up.user_id = %s
            UNION
            SELECT 
                se.promotion_id AS promotion_id,
                0 AS quantity,
                se.price AS price
            FROM 
                market_stockexchange AS se
            WHERE 
                se.promotion_id NOT IN (
                    SELECT promotion_id 
                    FROM market_stockexchange_user_promotions 
                    WHERE user_id = %s
                )
            """,
            (target_id, target_id)
        )
        promotion_records = cursor.fetchall()

        quantityes = {}

        for record in promotion_records:
            quantity = record[1] if record[1] != 0 else 0
            quantityes[record[0]] = quantity

        quantity = dict(sorted(quantityes.items()))  

        promotions = {
            record[0]: {
                'quantity_promotion': record[1],
                'price': record[2],
                'quantity': record[1] if record[1] != 0 else 0
            }
            for record in promotion_records
        }

        cursor.execute(
            """
            SELECT 
                promotion_id,
                title,
                description,
                price,
                price_sign
            FROM 
                market_stockexchange
            """
        )
        stock_exchange_records = cursor.fetchall()

        promotion_ui_data = {
            record[0]: {
                'title': record[1],
                'description': record[2],
                'price': record[3],
                'price_sign': record[4],
                'quantity_promotion': quantityes.get(record[0], 0)
            }
            for record in stock_exchange_records
        }

        return promotions, promotion_ui_data

    except Exception as e:
        print(f"Error in getInventory: {e}")
        return {}, {}
    
def update_stock_exchange_price():
    try:
        connection = psycopg2.connect(
            dbname=connection_parameters["dbname"],
            user=connection_parameters["user"],
            password=connection_parameters["password"],
            host=connection_parameters["host"],
            port=connection_parameters["port"]
        )
        cursor = connection.cursor()

        url_prices = "https://api.binance.com/api/v3/ticker/price"
        url_24h = "https://api.binance.com/api/v3/ticker/24hr"

        response_prices = requests.get(url_prices)
        response_prices.raise_for_status()
        prices = response_prices.json()

        response_24h = requests.get(url_24h)
        response_24h.raise_for_status()
        changes_24h = {item["symbol"]: float(item["priceChangePercent"]) for item in response_24h.json()}

        target_symbols = [
            "BTCUSDT", 
            "ETHUSDT", 
            "BNBUSDT", 
            "ADAUSDT", 
            "XRPUSDT", 
            "SOLUSDT", 
            "DOGEUSDT", 
            "DOTUSDT", 
            "MATICUSDT", 
            "SHIBUSDT"
            ]

        target_prices = [crypto for crypto in prices if crypto["symbol"] in target_symbols]
        sorted_prices = sorted(target_prices, key=lambda x: float(x['price']), reverse=True)

        stock_exchange_data = {}

        for index, crypto in enumerate(sorted_prices, start=1):
            symbol = crypto['symbol']
            price = round(float(crypto['price']), 3)
            change_percent = changes_24h.get(symbol, 0)

            price_sign = "+" if change_percent >= 0 else "-"

            stock_exchange_data[index] = {
                "promotion_price": price,
                "price_sign": price_sign
            }

            cursor.execute(
                """
                UPDATE market_stockexchange
                SET price = %s, price_sign = %s
                WHERE promotion_id = %s
                """,
                (price, price_sign, index)
            )
        connection.commit()
        return stock_exchange_data

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при подключении к API Binance: {e}")
        return None