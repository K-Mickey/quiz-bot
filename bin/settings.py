from decouple import config

TG_TOKEN = config("TG_TOKEN")
REDIS_URL = config("REDIS_URL")

LOG_LEVEL = config("LOG_LEVEL", default="INFO")
LOG_FORMAT = config(
    "LOG_FORMAT",
    default="[%(asctime)s] [%(levelname)s] [%(name)s - %(filename)s] > %(lineno)d - %(message)s",
)
