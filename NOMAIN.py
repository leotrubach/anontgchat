import asyncio
import logging
import sys
from os import getenv
import random
from aiogram import Bot, Dispatcher, html , types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters.command import Command, CommandObject
from aiogram.types import Message
from aiogram import F
from aiogram.filters import Command
import dotenv
dotenv.load_dotenv()

TOKEN = "7669873713:AAEuC9-p_WzAE9m_SqfgVOChS64ute25Bvc"

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()


async def error_no_arg(message: types.Message,command: CommandObject):

    if command.args is None:
        await message.answer(
            "Ошибка: не переданы аргументы"
        )
        return
async def error_only_1_word(message: types.Message, args):
    if len(args) != 1:
        await message.answer("Название комнаты должен быть из 1 слова ")
        return




pril = ['Шумные',
'Шуршащие',
'Пушистые',
'Липкие',
'Хрустящие',
'Задорные',
'Прыгающие',
'Колючие',
'Пузырящиеся',
'Щекочущие']

sush = ['Облака',
'Вертолёты',
'Молекулы',
'Орешки',
'Зонты',
'Пиксели',
'Ёжики',
'Лабиринты',
'Жуки',
'Пельмениэ']

room_members = {}

user_room = {}

name = {}


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Хочешь создать комнату(/create) \nВступить в чужую?(/join 'название комнаты') ")

@dp.message(Command("create"))
async def cmd_create(message: types.Message, command: CommandObject):
    await error_no_arg(message, command)

    args = command.args.split()

    await error_only_1_word(message, args)

    room_name = args[0]
    if room_name in room_members:
        await message.answer("Такая комната уже существует")
        return

    room_members[room_name] = set()

    await message.answer(f"создана комната по имени:{room_name}")
@dp.message(Command("join"))
async def cmd_join(message: Message, command: CommandObject):

    await error_no_arg(message, command)

    args = command.args.split()
    await error_only_1_word(message, args)

    room_name = args[0]



    if room_name not in room_members:
        await message.answer("Нет такой комнаты")
        return

    if message.from_user.id  in user_room:
        room_members[user_room[message.from_user.id]].remove(message.from_user.id)

    room_members[room_name].add(message.from_user.id)
    user_room[message.from_user.id] = room_name


    x, y = random.choice(pril), random.choice(sush)
    name[message.from_user.id] = f"{x} {y}"

    user_names = []
    for l_user in room_members[room_name]:
        if l_user == message.from_user.id:
            continue
        user_names.append(name[l_user])
    full_user_names = ", ".join(user_names)

    await message.answer(f"Вы успешно присоединились. Ваше имя: {name[message.from_user.id]}, в комноте есть: {full_user_names}")

    for user_id in room_members[user_room[message.from_user.id]]:
        if user_id == message.from_user.id:
            continue
        await bot.send_message(user_id, f"К вам присоединился: {name[message.from_user.id]}")

@dp.message()
async def annon_mess(message: Message):
    if message.from_user.id not in user_room:
        return
    for user_id in room_members[user_room[message.from_user.id]]:
        if user_id == message.from_user.id:
            continue

        await bot.send_message(user_id,f"{name[message.from_user.id]}: {message.text}")




async def main() -> None:

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())