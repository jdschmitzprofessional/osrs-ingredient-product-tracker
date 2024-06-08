import json
import sqlite3
import time
import os
from html import escape

import requests
from multipledispatch import dispatch


class SQLite_DB:
    """Wraps sqlite calls for ease and readability"""
    BASE_URL = "http://services.runescape.com/m=itemdb_oldschool/api/catalogue/detail.json"
    UPDATE_INTERVAL = 600
    CWD = os.getcwd()
    ITEM_MAPPING = "data/Objects_87.json"
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def init_table(self) -> None:
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS ITEMS( id INTEGER, name TEXT, price INTEGER, touched INTEGER,
            CONSTRAINT unique_column UNIQUE (id) )
            """)

        with open(self.ITEM_MAPPING, 'r') as infile:
            item_data_init = json.loads(infile.read())
        for item in item_data_init:
            self.conn.execute(f"""
                    INSERT OR IGNORE INTO items VALUES('{item['id']}', '{escape(item['name'], quote=True)}', 
                    '0', {int(time.time())})
                """
                              )
        self.conn.commit()

    def get_id(self, item_name: str) -> int:
        """it get id, when have item"""
        self.cursor.execute(f"SELECT id FROM items WHERE name = '{escape(item_name, quote=True)}'")
        return self.cursor.fetchone()[0]

    def get_item(self, item_id: int) -> str:
        """it get item, when have id"""
        self.cursor.execute(f"SELECT name FROM items WHERE id = '{item_id}'")
        return self.cursor.fetchone()[0]

    @dispatch(int)
    def update_price(self, id) -> int:

        new_price = self.fetch_price(id)

        self.cursor.execute(f"""
            UPDATE items SET price = {new_price}, touched = {int(time.time())} WHERE id = '{id}'
        """
                            )
        self.conn.commit()
        return new_price



    @dispatch(int)
    def get_price(self, item_id: int):
        """Gets price for the provided item ID from the database if column is younger than refresh interval,
        updates the price from the osrs API if older than refresh
        """

        self.cursor.execute(f"SELECT price, touched FROM items WHERE id = '{item_id}'")

        price, touched = self.cursor.fetchone()

        if (int(time.time()) - touched) > self.UPDATE_INTERVAL or price == 0:
            price = self.update_price(item_id)

        return price



    @dispatch(int)
    def fetch_price(self, item_id: int):
        """Updates the price of an item in the database"""
        req = requests.get(f"{self.BASE_URL}?item={item_id}")

        price = self.standardize_price(req.json()['item']['current']['price'])

        return price

    @dispatch(str)
    def standardize_price(self, price: str) -> int:
        """Standardizes prices into an integer from the approximate price given by the osrs ge api"""
        if "." in price:

            if price.endswith("m"):
                factor = 1000000
                price = float(price.replace("m", ""))

            elif price.endswith("k"):
                factor = 1000
                price = float(price.replace("k", ""))

            final_int = int(price * factor)
            return final_int

        return int(price.replace(",",""))


### Overloads ###

    @dispatch(int)
    def standardize_price(self, price: int):
        "Int prices do not need to be modified"
        return price

    @dispatch(str)
    def get_price(self, name: str):
        """Gets price for the provided item name"""
        return self.get_price(self.get_id(name))

    @dispatch(str)
    def update_price(self, item: str):
        """Overload str -> int"""
        return self.update_price(self.get_id(item))