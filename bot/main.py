import asyncio
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from handlers import user, worker, deliverier
from misc.db import USERS

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")


async def start():
    bot = Bot(token=TOKEN)

    dp = Dispatcher()
    dp.include_routers(user.router, worker.router, deliverier.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    USERS.update_many({}, {"$set": {"tg_id": None}})

    asyncio.run(start())
