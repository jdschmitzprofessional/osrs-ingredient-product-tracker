import json
import sqlite3
from html import escape
import time

import requests
from multipledispatch import dispatch


class DB:
    """Wraps sqlite calls for ease and readability"""
    BASE_URL = "http://services.runescape.com/m=itemdb_oldschool/api/catalogue/detail.json"

    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def init_table(self, item_data):
        self.conn.execute("CREATE TABLE IF NOT EXISTS items ("
                          "id INTEGER, name TEXT, price INTEGER, touched INTEGER)")
        with open(item_data, 'r') as infile:
            item_data_init = json.loads(infile.read())
            for item in item_data_init:
                self.conn.execute(f"SELECT 1 WHERE EXISTS ( " + \
                                  f"SELECT name FROM items WHERE id = {item_data_init[item['id']]})")

                self.conn.execute(f"INSERT INTO items VALUES('{item['id']}'," + \
                                  f"'{escape(item['name'], quote=True)}', '0')")
            self.conn.commit()

    def get_id(self, item_name):
        """it get id, when have item"""
        self.cursor.execute(f"SELECT id FROM items WHERE name = '{escape(item_name, quote=True)}'")
        return self.cursor.fetchone()[0]

    def get_item(self, item_id):
        """it get item, when have id"""
        self.cursor.execute(f"SELECT name FROM items WHERE id = '{item_id}'")
        return self.cursor.fetchone()[0]

    @dispatch(int)
    def get_stored_price(self, item_id: int):
        """Gets price for the provided item ID"""
        self.cursor.execute(f"SELECT price FROM items WHERE id = '{item_id}'")
        return self.cursor.fetchone()[0]

    @dispatch(str)
    def get_stored_price(self, name: str):
        """Gets price for the provided item name"""
        self.cursor.execute(f"SELECT price FROM items WHERE name = '{name}'")
        return self.cursor.fetchone()[0]

    @dispatch(str)
    def update_price(self, item):
        self.update_price(self.get_item(item))

    @dispatch(int)
    def update_price(self, item_id):
        req = requests.get(f"{self.BASE_URL}?item={self.get_id(item_id)}")
        price = req.json()['item']['current']['price']
        if type(price) == int:
            return price
        else:
            return int(price.replace(",", ""))
