import time
from loguru import logger
import asyncio

import config
from arbuz import ArbuzApp
from telegramclient import MyTelegramClient
from utils import parse_url_hash

async def main():
    telegram_client = MyTelegramClient(r'./tdata')

    # 1. Authorize
    await telegram_client.authorize()

    # 2. Get info about self
    await telegram_client.load_info()

    # 3. Get/Start chat
    chat, bot = await telegram_client.get_chat(config.BOT_NAME)
    logger.info(chat)

    # 4. Send /start command
    await telegram_client.send_start_command(chat)

    # 5. Find message
    result = await telegram_client.find_webview_message(chat)
    if result is None:
        logger.error("Не удалось найти сообщение с веб-кнопкой.")
        return
    message, button = result
    logger.info(message)

    # 6. Make web view request
    webview_url = await telegram_client.make_webview_request(chat, bot, message, button)
    logger.info(webview_url)
    
    # Extract tgWebAppData
    hash_params = parse_url_hash(webview_url)
    telegram_init_data = hash_params.get('tgWebAppData', [None])[0]
    
    if not telegram_init_data:
        logger.error("Failed to extract tgWebAppData from the webview URL.")
        return
    
    logger.info(f"Extracted tgWebAppData: {telegram_init_data}")

    # Initialize ArbuzApp with extracted tgWebAppData
    app = ArbuzApp(config.USER_ID, config.BYTE_KEY, telegram_init_data)
    
    # Example usage of ArbuzApp methods
    time_sleep, last_click = start(app)

    while True:
        try:
            error, click, energy, last_click, h = app.click(last_click)
            if error is not None:
                if error == "NOT_ENOUGH_ENERGY":
                    time_sleep, last_click = start(app)
                    time.sleep(time_sleep)
                else:
                    logger.error(error)
                    time.sleep(10)
            else:
                logger.success(f"+{click} COINS | {energy} ENERGY | hash: {h}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")

        time.sleep(0.7)

def start(app: ArbuzApp) -> tuple[int, float]:
    coins, energy_boost, energy_limit, last_click = app.me_info()
    if energy_boost == 0:
        logger.error("Energy boost is zero, cannot calculate time sleep.")
        return 10, last_click
    time_sleep = int(energy_limit / energy_boost)
    message = (f"Status Info\n"
               f"{fcoin(coins)} COINS\n"
               f"{energy_boost} EB\n"
               f"{energy_limit} EL\n"
               f"{time_sleep} sec. TS")
    logger.info(message)

    return time_sleep, last_click

def fcoin(number: float) -> str:
    if number < 1000:
        return str(number)
    if number < 1000000:
        return f"{number / 1000:.1f}K"
    if number < 1000000000:
        return f"{number / 1000000:.3f}M"
    if number < 1000000000000:
        return f"{number / 1000000000:.3f}B"

    return f"{number / 1000000000000:.3f}T"

if __name__ == "__main__":
    asyncio.run(main())
