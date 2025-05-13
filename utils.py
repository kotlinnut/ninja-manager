import json
import os
from datetime import datetime


class NinjaData:
    def __init__(self, data_file="data/ninjas.json", rules_file="data/rules.txt",
                 scrolls_file="data/scrolls.json"):
        self.data_file = data_file
        self.rules_file = rules_file
        self.scrolls_file = scrolls_file
        self.ensure_data_file()
        self.ensure_rules_file()
        self.ensure_scrolls_file()

    def ensure_scrolls_file(self):
        os.makedirs(os.path.dirname(self.scrolls_file), exist_ok=True)
        if not os.path.exists(self.scrolls_file):
            self.save_scrolls([])

    def load_scrolls(self):
        try:
            with open(self.scrolls_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    def save_scrolls(self, scrolls):
        with open(self.scrolls_file, 'w', encoding='utf-8') as f:
            json.dump(scrolls, f, ensure_ascii=False, indent=2)

    def add_scroll(self, name):
        scrolls = self.load_scrolls()
        if name not in scrolls:
            scrolls.append(name)
            self.save_scrolls(scrolls)

    def remove_scroll(self, name):
        scrolls = self.load_scrolls()
        if name in scrolls:
            scrolls.remove(name)
            self.save_scrolls(scrolls)

    def ensure_data_file(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        if not os.path.exists(self.data_file):
            self.save_data([])

    def ensure_rules_file(self):
        os.makedirs(os.path.dirname(self.rules_file), exist_ok=True)
        if not os.path.exists(self.rules_file):
            self.save_rules("在此输入规则说明...")

    def load_data(self):
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    def save_data(self, data):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_rules(self):
        try:
            with open(self.rules_file, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return "在此输入规则说明..."

    def save_rules(self, rules):
        with open(self.rules_file, 'w', encoding='utf-8') as f:
            f.write(rules)

    def add_ninja(self, name, rank):
        data = self.load_data()

        ninja = {
            "name": name,
            "rank": rank,
            "created_at": datetime.now().isoformat()
        }

        data.append(ninja)
        self.save_data(data)

    def delete_ninja(self, name):
        data = self.load_data()
        data = [n for n in data if n["name"] != name]
        self.save_data(data)

    def get_ninjas(self, rank=None):
        data = self.load_data()
        if rank:
            return [n for n in data if n["rank"] == rank]
        return data