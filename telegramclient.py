from pprint import pprint

from loguru import logger
from telethon import types
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
from opentele.api import API, UseCurrentSession
from opentele.td import TDesktop
from telethon.tl.functions.messages import GetDialogsRequest, RequestWebViewRequest
from telethon.tl.types import InputPeerEmpty


class MyTelegramClient:
    def __init__(self, tdata_path):
        self.me = None
        self.client = None
        self.tdata_path = tdata_path
        # api = API.TelegramWeb_Z

    async def authorize(self):

        if self.client and self.client.is_connected():
            return self.client

        try:
            tdesk = TDesktop(self.tdata_path)
            logger.info(f"Loaded TDesktop from path: {self.tdata_path}")
        except Exception as e:
            logger.error(f"Ошибка при инициализации TDesktop: {e}")
            return False

        try:
            client = await tdesk.ToTelethon("telethon.session", UseCurrentSession, api=API.TelegramAndroid.Generate())
            await client.connect()
            if not await client.is_user_authorized():
                logger.error("User is not authorized. Please check your TData files.")
                return None
            if client.is_connected():
                self.client = client
            return client
        except SessionPasswordNeededError:
            logger.error("Password required for the session. Please provide the password in your TData files.")
            return None
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return None

    async def load_info(self):

        if not self.me:
            logger.info('Получаем инфо о себе')
            self.me = await self.client.get_me()
        logger.info(self.me)

    async def get_chat(self, username):
        # Fetch all dialogs (chats and users)
        user_chat = await self.client.get_entity(username)
        user = await self.client.get_input_entity(username)
        # If user_chat is not found, initiate a new chat
        if user_chat is None:
            user = await self.client.get_input_entity(username)
            user_chat = await self.client.send_message(user, '/start')

        return user_chat, user
    
    async def send_start_command(self, chat):
        message = await self.client.send_message(chat, '/start')
        logger.info(f"Sent /start command: {message}")
        return message
    
    async def find_webview_message(self, chat, limit=100):
        logger.debug(f"Ищем сообщение с веб-кнопкой в чате {chat.id}")
        async for message in self.client.iter_messages(chat, limit=limit):
            if message.reply_markup and isinstance(message.reply_markup, types.ReplyInlineMarkup):
                for row in message.reply_markup.rows:
                    for button in row.buttons:
                        if isinstance(button, types.KeyboardButtonWebView):
                            return message, button
        logger.debug("Сообщение с веб-кнопкой не найдено.")
        return None
    
    

    async def make_webview_request(self, chat, bot, message, webview_button):
        webview_request = await self.client(RequestWebViewRequest(
            peer=message.peer_id,
            bot=bot,
            platform="browser",
            from_bot_menu=True,
            url=webview_button.url,
            start_param='start'
        ))
        logger.info(f"WebView request made with URL: {webview_button.url}")
        return webview_request.url

