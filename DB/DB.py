import json
import sqlite3
import time
from html import escape

import requests
from multipledispatch import dispatch


class DB:
    """Wraps sqlite calls for ease and readability"""
    BASE_URL = "http://services.runescape.com/m=itemdb_oldschool/api/catalogue/detail.json"
    UPDATE_INTERVAL = 600

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def init_table(self, item_data: dict) -> None:
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS ITEMS( id INTEGER, name TEXT, price INTEGER, touched INTEGER,
            CONSTRAINT unique_column UNIQUE (id) )
            """)
        with open(item_data, 'r') as infile:
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
            UPDATE items SET price = {new_price} WHERE id = '{id}'
        """
                            )
        self.conn.commit()
        return new_price

    @dispatch(str)
    def update_price(self, item: str):
        """Overload str -> int"""
        return self.update_price(self.get_id(item))

    @dispatch(int)
    def get_stored_price(self, item_id: int):
        """Gets price for the provided item ID from the database if column is younger than refresh interval,
        updates the price from the osrs API if older than refresh
        """

        self.cursor.execute(f"SELECT price, touched FROM items WHERE id = '{item_id}'")

        price, touched = self.cursor.fetchone()

        if int(time.time()) - touched > self.UPDATE_INTERVAL or price == 0:
            price = self.update_price(item_id)

        return price

    @dispatch(str)
    def get_stored_price(self, name: str):
        """Gets price for the provided item name"""
        return self.get_stored_price(self.get_id(name))

    @dispatch(int)
    def fetch_price(self, item_id: int):
        """Updates the price of an item in the database"""

        req = requests.get(f"{self.BASE_URL}?item={item_id}")

        price = req.json()['item']['current']['price']

        if type(price) != int:
            price = int(price.replace(",", ""))

        return price
