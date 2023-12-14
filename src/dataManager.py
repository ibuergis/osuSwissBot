import os
import json


class DataManager:

    __path = os.getcwd()

    @staticmethod
    def jsonExists(name: str = '') -> bool:
        try:
            with open(os.getcwd() + '//data//' + name + '.json', 'r') as f:
                f.close()
                return True

        except FileNotFoundError:
            return False

    @staticmethod
    def getJson(name: str = '') -> dict | None:
        if DataManager.jsonExists(name):
            with open(os.getcwd() + '//data//' + name + '.json', 'r') as f:
                data: dict = json.load(f)
                f.close()

        else:
            return None

        return data

    @staticmethod
    def setJson(name: str = '', data: dict = {}) -> dict:
        try:
            with open(os.getcwd() + '//data//' + name + '.json', 'w') as f:
                json.dump(data, f, indent=4)
                f.close()

            return data

        except FileNotFoundError:
            with open(os.getcwd() + '//data//' + name + '.json', 'w+') as f:
                json.dump(data, f)
                f.close()

            return data

    @staticmethod
    def getOrCreateJson(name: str = '') -> dict | None:
        if DataManager.jsonExists(name):
            with open(os.getcwd() + '//data//' + name + '.json', 'r') as f:
                data: dict = json.load(f)
                f.close()

        else:
            return {}

        return data
