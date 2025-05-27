from vkbottle import Bot

from bin.vk_handlers import labeler


def run_bot(bot_token: str):
    bot = Bot(
        token=bot_token,
        labeler=labeler,
    )
    bot.run_forever()
