from decouple import config

TG_TOKEN = config("TG_TOKEN")
TG_REDIS_URL = config("TG_REDIS_URL")

VK_TOKEN = config("VK_TOKEN")
VK_REDIS_URL = config("VK_REDIS_URL")

LOG_LEVEL = config("LOG_LEVEL", default="INFO")
LOG_FORMAT = config(
    "LOG_FORMAT",
    default="[%(asctime)s] [%(levelname)s] [%(name)s - %(filename)s] > %(lineno)d - %(message)s",
)
