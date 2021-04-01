import configparser
import os

config = configparser.RawConfigParser()
config.read(".//Configurations//config.ini")


class ReadConfig:
    @staticmethod
    def getApplicationURL():
        url = os.getenv("baseURL")
        return url

    @staticmethod
    def getLoginLocalURL():
        url2 = os.getenv("loginURL")
        return url2

    @staticmethod
    def getUserName():
        username = config.get("common items", "username")
        return username

    @staticmethod
    def getPassword():
        password = config.get("common items", "password")
        return password
