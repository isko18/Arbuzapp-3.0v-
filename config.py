import sys
from loguru import logger


BOT_NAME ='@wmclick_bot'

# Конфигурация
USER_ID = 4444444  # ID Telegram пользователя
KEY = "click-secret"
BYTE_KEY = KEY.encode("UTF-8")
PROXY_EXISTS = False
PROXY = 'YOUR_PROXY'  # if needed

logger.remove()
logger.add(sys.stdout, colorize=True,
           format="<bold>[ArbuzApp]</bold> <white>{time:YYYY-MM-DD HH:mm:ss.SSS}</white> <red>|</red> <level>{level: <8}</level> <red>|</red> <level>{message}</level>")
