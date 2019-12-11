import os


class Config:
    def __init__(self):
        # app secret key
        self.app_secret_key = os.getenv('APP_SECRET_KEY', '')
        # mysql config
        self.mysql_host = os.getenv("MYSQL_HOST", "")
        self.mysql_user = os.getenv("MYSQL_USER", "")
        self.mysql_pass = os.getenv("MYSQL_PASSWORD", "")
        self.mysql_db = os.getenv("MYSQL_DB", "")
        self.mysql_cursor_class = os.getenv("MYSQL_CURSOR_CLASS", "")


config = Config()
