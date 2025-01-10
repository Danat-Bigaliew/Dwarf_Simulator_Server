def get_game_data(cursor, target_id):
    try:
        cursor.execute(# переделать
            """
            SELECT 
                player_id, diamond, gold, eri, happiness, strength, eloquence
            FROM 
                user_game_data
            WHERE 
                player_id = %s
            """,
            (target_id,)
        )

        result = cursor.fetchone()

        if result is None:
            print(f"No data found for player_id: {target_id}")
            return {}

        game_data = {
            'player_id': result[0],
            'diamond': result[1],
            'gold': result[2],
            'eri': result[3],
            'happiness': result[4],
            'strength': result[5],
            'eloquence': result[6]
        }

        print(f"У игрока {game_data["gold"]} голды")

        # Возврат данных
        return game_data

    except Exception as e:
        print(f"Error in get_game_data: {e}")
        return {}