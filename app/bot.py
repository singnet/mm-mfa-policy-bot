from mmpy_bot import Bot, Settings
from plugin import MFAPlugin
from settings import BotSettings

bot = Bot(
    settings=Settings(
        MATTERMOST_URL = BotSettings.MATTERMOST_URL,
        MATTERMOST_PORT = BotSettings.MATTERMOST_PORT,
        BOT_TOKEN = BotSettings.BOT_TOKEN,
        SSL_VERIFY = BotSettings.SSL_VERIFY,
        DEBUG = BotSettings.DEBUG
    ),
    plugins=[MFAPlugin()]
)
bot.run()