import logging


class LogGen:
    @staticmethod
    def loggen():
        logging.basicConfig(
            format="%(asctime)s %(message)s",
            datefmt="%m/%d/%Y %I:%M:%S %p",
            filename="./Logs/example.log",
            level=logging.INFO,
        )
        logger = logging.getLogger()
        return logger
