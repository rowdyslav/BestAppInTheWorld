import telebot
from telebot.types import Message
from dotenv import load_dotenv
from os import environ
from db_conn import DISHES, USERS
from roles import User

from icecream import ic

load_dotenv()
TOKEN = environ["TELEGRAM_TOKEN"]

HELP_TEXT = """/help - помощь(это сообщение)
/auth - авторизация
/menu - посмотреть меню
/review <имя блюда> <оценка> - оставить отзыв о блюде"""
START_TEXT = """Это бот для организации корпоротивного питания
(добавлять отзывы и оценку блюду)
/help - помощь"""

bot = telebot.TeleBot(TOKEN)


# Handle '/start' and '/help'
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        START_TEXT,
    )


@bot.message_handler(commands=["help"])
def help(message):
    bot.reply_to(
        message,
        HELP_TEXT,
    )


@bot.message_handler(commands=["menu"])
def menu(message):
    status_message = bot.send_message(
        message.chat.id,
        "Загрузка..",
    )
    dishes = list(DISHES.find())
    ans_message = []
    for i in dishes:
        current = []
        for j in ["title", "cost", "structure"]:
            current.append(str(i[j]))
        try:
            current.append(str(sum(i["scores"]) / len(i["scores"])))
        except ZeroDivisionError:
            current.append("Нет оценок")
        ans_message.append(": ".join(current))
    ans_message = "\n".join(ans_message)

    bot.delete_message(message.chat.id, status_message.message_id)

    bot.send_message(
        message.chat.id,
        ans_message,
    )


@bot.message_handler(commands=["review"])
def review(message: Message):
    status_message = bot.send_message(
        message.chat.id,
        "Загрузка..",
    )
    args = message.text.split()  # type: ignore

    dish_title = "".join(args[1:-1])
    q = {"title": dish_title}

    dish = DISHES.find_one(q)
    if not dish:
        bot.reply_to(message, "Блюдо не найдено!")
        return
    if not args[-1].isnumeric() or not 1 <= int(args[-1]) <= 5:
        bot.reply_to(message, f'Ожидалось число от 1 до 5, получено "{args[-1]}"')
        return

    DISHES.update_one(q, {"$push": {"scores": int(args[-1])}})
    bot.delete_message(message.chat.id, status_message.message_id)

    bot.reply_to(
        message,
        f"Блюду {dish_title} успешно поствлена оценка {args[-1]}!",
    )


@bot.message_handler(commands=["auth"])
def auth(message):
    user_data = USERS.find_one({"tg_id": message.from_user.id})
    if user_data:
        msg = bot.send_message(message.chat.id, "Вы авторизованны")
    else:
        send_msg = bot.send_message(
            message.chat.id,
            "Отправте свой логин и пароль на разных строчках",
        )
        bot.register_next_step_handler(send_msg, back_auth)


def back_auth(message):
    data = message.text.split("\n")  # создаем список ['логин', 'пароль']
    login, password = data
    log_user = User(login, password)
    log_result = log_user._login()

    q = {"login": login}
    if not log_result[
        1
    ]:  # если такой комбинации не существует, ждём команды /start Опять
        bot.send_message(message.chat.id, log_result[0])
        user_data = USERS.find_one(q)
    else:  # а если существует, переходим к следующему шагу
        USERS.update_one(q, {"$set": {"tg_id": message.from_user.id}})
        msg = bot.send_message(message.chat.id, "Вы авторизованны")
        # bot.register_next_step_handler(msg, next_step_func)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)


bot.infinity_polling()
