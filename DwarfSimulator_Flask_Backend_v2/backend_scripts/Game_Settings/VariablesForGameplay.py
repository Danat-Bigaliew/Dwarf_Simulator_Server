def variable_for_gameplay():
    pick_diamond_click = 5
    bag_for_diamond = 500
    shovel_dimond_click = 6
    hammer_diamond_click = 4
    wooden_spacers_progress_bars = 0.3
    old_gloves_speed_anim = 0.2
    boots = 0.2

    speed_animation_click = 1
    max_progressBars = 100
    buff_debuff_progressBars = 10
    shaft_diamond_for_click = 10
    market_gold_for_click = 10
    market_cell_diamond_for_click = 5
    buy_in_tavern = 3

    tools = {
        "pick" : pick_diamond_click,
        "bag" : bag_for_diamond,
        "shovel" : shovel_dimond_click,
        "hammer" : hammer_diamond_click,
        "wooden_spacers" : wooden_spacers_progress_bars,
        "old_gloves" : old_gloves_speed_anim,
        "boots" : boots
    }

    variables_for_gameplay = {
        "speed_animation" : speed_animation_click,
        "max_progressBars" : max_progressBars,
        "buff_debuff_progressBars" : buff_debuff_progressBars,
        "shaft_diamond_for_click" : shaft_diamond_for_click,
        "market_gold_for_click" : market_gold_for_click,
        "market_cell_diamond_for_click" : market_cell_diamond_for_click,
        "buy_in_tavern" : buy_in_tavern,
        "tools" : tools
    }

    return variables_for_gameplay

def update_diamond_click(buyed_item, level_product, variable):
    buyed_item *= level_product
    buyed_item /= 2
    variable += buyed_item
    return variable

def update_progressBars_variable(buyed_item, level_product, variable):
    buyed_item *= level_product
    variable -= buyed_item * 1.5
    return variable

def update_debuff_progressBars_variable(variable):
    new_variable /= 2
    variable += new_variable
    return variable

def update_bag(buyed_item, level_product):
    variable = buyed_item
    buyed_item *= level_product
    buyed_item /= 4
    variable += buyed_item
    return variable

def update_speed_anim(level_product, variable):
    variable -= level_product * 0.05
    return variable

def update_number_for_ui(number):
    current_number = int(number)
    thousand = 1000
    million = 1000000
    billion = 1000000000

    new_price = number

    if current_number >= thousand and current_number < million:
        current_number /= thousand

        match current_number % 1:
            case 0:
                current_number = int(current_number)

        new_price = f"{current_number}k"

    elif current_number >= million and current_number < billion:
        current_number / million
        new_price = f"{current_number}m"
    elif current_number >= billion:
        current_number / billion
        new_price = f"{current_number}b"

    return new_price