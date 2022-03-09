import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
DB_URI = os.getenv("DB_URI", "sqlite://database.db")

TORTOISE_ORM = {
    "connections": {"default": DB_URI},
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
