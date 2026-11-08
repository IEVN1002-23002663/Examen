import os

class DevelopmentConfig:
    DEBUG = True
    MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
    MYSQL_USER = os.getenv("MYSQL_USER", "angel")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "root")
    MYSQL_DB = os.getenv("MYSQL_DB", "pizzeria")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_UNIX_SOCKET = None
    MYSQL_CONNECT_TIMEOUT = 10
    MYSQL_CURSORCLASS = None

config = {"development": DevelopmentConfig}