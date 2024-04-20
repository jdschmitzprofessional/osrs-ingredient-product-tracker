from sqlite_db import SQLite_DB

import time
import json
from prometheus_client import start_http_server, Gauge





class Exporter:

    DEFAULT_PORT = 80
    DEFAULT_POLL_INTERVAL_SECONDS = 300
    ILLEGAL_CHARACTERS = [
        "(",
        ")",
        " ",
        "'"
    ]

    def __init__(self, port = None, polling_interval_seconds = None, items: list = []):
        self.prom_port = self.DEFAULT_PORT
        self.poll_interval = self.DEFAULT_POLL_INTERVAL_SECONDS

        self.db = SQLite_DB("data/items.db")
        if port:
            self.prom_port = port
        if polling_interval_seconds:
            self.poll_interval = polling_interval_seconds
        self.items = {}
        for item in items:
            self.items[item] = Gauge(self.scrub_item_name(item), f"{item} price")


    def scrub_item_name(self, item):
        scrubbed_item = item.lower()

        for char in self.ILLEGAL_CHARACTERS:
            scrubbed_item = scrubbed_item.replace(char, "_")

        if scrubbed_item.endswith("_"):
            scrubbed_item = scrubbed_item[:-1]
        return scrubbed_item

    def refresh_cycle(self):
        while True:
            self.fetch()
            time.sleep(self.poll_interval)

    def fetch(self):
        for item, gauge in self.items.items():
            gauge.set(self.db.get_price(item))

    def start_server(self):
        start_http_server(addr="0.0.0.0", port=self.prom_port)


if __name__ == '__main__':
    print("Load items")
    with open("data/items.json", "r") as infile:
        items = json.loads(infile.read())

    print("Instantiate class")
    exporter = Exporter(items=items)

    print("Start exporter")
    exporter.start_server()

    print("Start refresh loop")
    exporter.refresh_cycle()