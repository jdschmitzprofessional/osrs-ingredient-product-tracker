import json
import math

from sqlite_db import SQLite_DB

objects = "data/Objects_87.json"
potion_data = "data/potions.json"

def eval_recipe(potion):

    herb = potion['herb']
    grimy_herb = f"Grimy {herb.lower()}"
    ingredient = potion['ingredient']
    result_3 = potion['product']
    result_4 = result_3.replace("3", "4")

    prices = {
        "herbs": {
            "clean": {
                "name": herb,
                "price": item_db.get_price(herb)
            },
            "grimy": {
                "name": grimy_herb,
                "price": item_db.get_price(grimy_herb)
            }
        },
        "ingredients": {
            ingredient: item_db.get_price(ingredient)
        },
        "products": {
            result_3: item_db.get_price(result_3),
            result_4: item_db.get_price(result_4)
        }
    }

    ingredient_ppd_grimy = math.ceil((item_db.get_price(grimy_herb) + item_db.get_price(ingredient)) / 3)
    ingredient_ppd_clean = math.ceil((item_db.get_price(herb) + item_db.get_price(ingredient)) / 3)
    price_per_dose = min(ingredient_ppd_grimy, ingredient_ppd_clean)
    price_per_dose_stocked = min(ingredient_ppd_grimy, ingredient_ppd_clean) - math.ceil(item_db.get_price(ingredient) / 3)
    margins = {
        "name": potion['name'],
        "min_price_per_dose": price_per_dose,
        "grimy": item_db.get_price(grimy_herb),
        "clean": item_db.get_price(herb),
        "Price(3)": item_db.get_price(result_3),
        "Price(4)": item_db.get_price(result_4),
        "profit(3)": item_db.get_price(result_3) - math.ceil(price_per_dose * 3),
        "profit(3) stocked ingredient": item_db.get_price(result_3) - math.ceil(price_per_dose_stocked * 3),
        "profit(4)": item_db.get_price(result_4) - math.ceil(price_per_dose * 4),
        "profit(4) stocked ingredient": item_db.get_price(result_4) - math.ceil(price_per_dose_stocked * 4),
    }

    return prices, margins





if __name__ == '__main__':
    with open(potion_data, 'r') as infile:
        potions = json.loads(infile.read())

    item_db = SQLite_DB("data/items.db")
    item_db.init_table(objects)
    for potion in potions:
        recipe, margin = eval_recipe(potion)
        print(json.dumps(margin, indent=1))

