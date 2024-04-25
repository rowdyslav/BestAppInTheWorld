from aiogram import Router, types
from aiogram.filters import Command, CommandObject

from misc.db import DISHES, USERS
from misc.roles import Worker, Manager, User

router = Router()


@router.message(Command("review"))
async def review(message: types.Message, command: CommandObject):
    user_obj = User(USERS.find_one({"tg_id": message.from_user.id})["login"], '')._get()

    if not type(user_obj) in (Worker, Manager):
        await message.answer("Вашей роли недоступна эта команда!")
        return

    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return

    try:
        *dish_title, score = command.args.split(" ", maxsplit=1)
        dish_title = " ".join(dish_title)
        score = int(score)
    except ValueError:
        await message.answer("*/review <имя блюда> <число от 1 до 5>*", parse_mode="Markdown")
        return

    q = {"title": dish_title}

    dish = DISHES.find_one(q)
    if not dish:
        await message.answer("Блюдо не найдено!")
        return

    DISHES.update_one(
        q,
        {
            "$inc": {
                "scores": {
                    "sum": score,
                    "len": 1,
                }
            }
        },
    )

    await message.answer(
        f"Блюду {dish_title} успешно поставлена оценка {score}!",
    )
