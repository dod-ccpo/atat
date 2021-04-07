import configparser
import os

config = configparser.RawConfigParser()


class ReadConfig:
    @staticmethod
    def getApplicationURL():
        url = os.getenv("baseURL")
        return url

    @staticmethod
    def getLoginLocalURL():
        url2 = os.getenv("loginURL")
        return url2
