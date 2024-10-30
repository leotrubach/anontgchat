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
        await message.answer("Ошибка: не переданы аргументы")
        return
async def error_only_1_word(message: types.Message, args):
    if len(args) != 1:
        await message.answer("Название комнаты должен быть из 1 слова ")
        return



room_members = {}

user_room = {}

name = {}


class CommandParseError(Exception):
    def __init__(self, message):
        self.message = message

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Хочешь создать комнату(/create) \nВступить в чужую?(/join 'название комнаты') ")


def parse_room_name(command: CommandObject):
    if command.args is None:
        raise CommandParseError("Ошибка: не переданы аргументы")

    args = command.args.split()

    if len(args) != 1:
        raise CommandParseError("Название комнаты должено быть из 1 слова")

    room_name = args[0]
    return room_name


def validate_parse(wrapped):
    async def wrapper(message: types.Message, command: CommandObject):
        try:
            await wrapped(message=message, command=command)
        except CommandParseError as e:
            await message.answer(e.message)

    return wrapper


def skip(message):
    for user_id in room_members[user_room[message.from_user.id]]:
        if user_id == message.from_user.id:
            continue
        
    return user_id

@dp.message(Command("create"))
@validate_parse
async def cmd_create(message: types.Message, command: CommandObject):
    room_name = parse_room_name(command)

    if room_name in room_members:
        await message.answer("Такая комната уже существует")
        return

    room_members[room_name] = set()
    await message.answer(f"Создана комната по имени:{room_name}")


@dp.message(Command("join"))
@validate_parse
async def cmd_join(message: Message, command: CommandObject):
    room_name = parse_room_name(command)

    if room_name not in room_members:
        await message.answer("Нет такой комнаты")
        return

    if message.from_user.id in user_room:
        room_members[user_room[message.from_user.id]].remove(message.from_user.id)

    room_members[room_name].add(message.from_user.id)
    user_room[message.from_user.id] = room_name

#сделать нормальные ники
    from data import nick
    name[message.from_user.id] = nick

    user_names = []
    for l_user in room_members[room_name]:
        if l_user == message.from_user.id:
            continue
        user_names.append(name[l_user])
    full_user_names = ", ".join(user_names)
    if full_user_names == "":
        full_user_names = "Только <b>вы</b>"
    await message.answer(f"Вы успешно присоединились. Ваше имя: {name[message.from_user.id]}, в комноте есть: {full_user_names}")



    user_id = skip(message)
    print(user_id)
    await bot.send_message(user_id, f"К вам присоединился: {name[message.from_user.id]}")


@dp.message()
async def annon_mess(message: Message):
    if message.from_user.id not in user_room:
        return


    user_id = skip(message)

    await bot.send_message(user_id,f"{name[message.from_user.id]}: {message.text}")




async def main() -> None:

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())