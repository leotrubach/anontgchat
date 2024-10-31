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

TOKEN = getenv("BOT_TOKEN")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()

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



async def send_to_chat(room_name: str, skip_user: int, message: str):
    for user_id in room_members[room_name]:
        if user_id == skip_user:
            continue
        await bot.send_message(user_id, message)
    return


@dp.message(Command("create"))
@validate_parse
async def cmd_create(message: types.Message, command: CommandObject):
    room_name = parse_room_name(command)

    if room_name in room_members:
        await message.answer("Такая комната уже существует")
        return

    room_members[room_name] = set()
    await message.answer(f"Создана комната по имени: {room_name}")


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

    from data import generate_nick
    name[message.from_user.id] = generate_nick()
    user_names = []

    for l_user in room_members[room_name]:
        if l_user == message.from_user.id:
            continue
        user_names.append(name[l_user])

    user_id = message.from_user.id
    full_user_names = ", ".join(user_names)
    if full_user_names == "":
        full_user_names = "Только <b>вы</b>"
    await message.answer(f"Вы успешно присоединились. Ваше имя: {name[message.from_user.id]}, в комнате есть: {full_user_names}")

    message = f"К вам присоединился: {name[message.from_user.id]}"

    await send_to_chat(room_name, user_id, message)

@dp.message(Command("part"))
async def cmd_part(message: Message):
    room_members[user_room[message.from_user.id]].remove(message.from_user.id)
    messege =  f"{name[message.from_user.id]} вышел из комнаты"
    user_id = message.from_user.id
    await send_to_chat(user_room[message.from_user.id],user_id, messege)
    await message.answer("Вы вышли из комноты, теперь вы не состоите ни в какой группе")



@dp.message(Command("list"))
async def cmd_list(message: Message):
    list_of_message = []
    for key in room_members.keys():
        if room_members[key] == set():
            part_of_message = f"{key}: Пусто"
        else:
            l = []
            for c in room_members[key]:
                l.append(name[c])
            str_of_message = ", ".join(l)
            part_of_message = f"{key}: {str_of_message}"
        list_of_message.append(part_of_message)
        full_massage = ", ".join(list_of_message)
    await message.answer(f"{full_massage}")



@dp.message()
async def annon_mess(message: Message):

    user_id = message.from_user.id
    if message.from_user.id not in user_room:
        return
    message = f"{name[message.from_user.id]}: {message.text}"

    await send_to_chat(user_room[user_id], user_id, message)






async def main() -> None:

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())