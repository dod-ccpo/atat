import configparser
import os

config = configparser.RawConfigParser()


class ReadConfig:
    @staticmethod
    def getApplicationURL():
        url = os.getenv("baseUrl")
        return url

    @staticmethod
    def getLoginLocalURL():
        url2 = os.getenv("loginUrl")
        return url2
    
