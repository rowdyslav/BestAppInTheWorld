from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from icecream import ic

from misc.db import USERS
from misc.roles import Deliverier, Manager, User, Worker

from bot.config import HELP_TEXTS
from bot.keyboards import user, worker, manager, deliverier

router = Router()


@router.message(Command('start', 'auth'))
async def auth(message: Message):
    await message.answer("Для авторизации отправте свой логин и пароль через пробел", reply_markup=user.rkm)


@router.message(Command("help"))
async def help(message: Message):
    user_obj = User(USERS.find_one({"tg_id": message.from_user.id})["login"], '')._get()

    await message.answer(
        HELP_TEXTS.get(type(user_obj), "*/auth* - авторизация"),
        parse_mode="Markdown",
        reply_markup=user.rkm,
    )


@router.message(~F.text.startswith('/'))
async def process_auth(message: Message):
    tg_id = message.from_user.id
    q = {"tg_id": tg_id}

    ic(USERS.find_one(q))
    if not (message.text and message.from_user) or USERS.find_one(q):
        return
    try:
        login, password = message.text.split()
    except ValueError:
        await auth(message)
        return
    log_result, user_obj = User(login, password)._login()
    match user_obj:
        case Worker():
            keyboard = worker.rkm
        case Manager():
            keyboard = manager.rkm
        case Deliverier():
            keyboard = deliverier.rkm
        case _:
            await message.answer(log_result)
            return

    USERS.update_one(q, {"$set": {"tg_id": None}})
    USERS.update_one({"login": login}, {"$set": q})

    await message.answer(
        f"Вы авторизованы под логином {login}",
        reply_markup=keyboard,
    )
