import json

from DB import DB

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
            herb: item_db.get_stored_price(herb),
            grimy_herb: item_db.get_stored_price(grimy_herb)
        },
        "ingredients": {
            ingredient: item_db.get_stored_price(ingredient)
        },
        "products": {
            result_3: item_db.get_stored_price(result_3),
            result_4: item_db.get_stored_price(result_4)
        }
    }

    print(json.dumps(prices, indent=2))
    return prices

def eval_margins(potion):
    pass


if __name__ == '__main__':
    with open(potion_data, 'r') as infile:
        potions = json.loads(infile.read())

    item_db = DB("data/items.db")
    item_db.init_table(objects)

    for potion in potions:
        eval_recipe(potion)
