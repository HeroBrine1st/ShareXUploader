import os
import dotenv
dotenv.load_dotenv()

TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": os.getenv("MYSQL_HOST"),
                "port": int(os.getenv("MYSQL_PORT")),
                "user": os.getenv("MYSQL_USER"),
                "password": os.getenv("MYSQL_PASSWORD"),
                "database": os.getenv("MYSQL_DATABASE")
            }
        }
    },
    "apps": {
        "uploader": {
            "models": ["aerich.models", "uploader.models"],
            "default_connection": "default",
        }
    }
}

ROOT_PATH = os.getenv("ROOT_URL")
DATA_PATH = os.getenv("DATA_PATH")
# REAL_IP_HEADER TODO
# MAX_IP_ACCOUNTS TODO
# ALLOW_UPLOAD_BY_DEFAULT TODO