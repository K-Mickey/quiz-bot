from decouple import config

TOKEN = config("TG_TOKEN")
REDIS_URL = config("TG_REDIS_URL")
LOG_LEVEL = config("LOG_LEVEL", default="INFO")
LOG_FORMAT = config(
    "LOG_FORMAT",
    default="[%(asctime)s] [%(levelname)s] [%(name)s - %(filename)s] > %(lineno)d - %(message)s",
)
