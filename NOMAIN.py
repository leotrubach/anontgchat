import asyncio
import logging
import sys
from os import getenv
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters.command import CommandObject
from aiogram.types import Message
from aiogram.filters import Command
import dotenv

dotenv.load_dotenv()
TOKEN = getenv("BOT_TOKEN")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()

room_members = {}
room_visibility = {}
user_room = {}
name = {}

class CommandParseError(Exception):
    def __init__(self, message):
        self.message = message

def validate_parse(wrapped):
    async def wrapper(message: types.Message, command: CommandObject):
        try:
            await wrapped(message=message, command=command)
        except CommandParseError as e:
            await message.answer(e.message)
    return wrapper

def l_user_names(room_name):
    return [name[user_id] for user_id in room_members[room_name]]

def join_add(room_name: str, user_id: int):
    room_members[room_name].add(user_id)


def join_remove(user_id):
    if user_id in user_room:
        name_room = user_room[user_id]
        if room_members[name_room] != set():
            room_members[name_room].remove(user_id)

def make_create(room_name: str, is_public: bool):
    if room_name in room_members:
        raise CommandParseError("Уже есть комната с таким назвванием")
    room_members[room_name] = set()
    room_visibility[room_name] = is_public

async def send_to_chat(room_name: str, skip_user: int, message: str):
    for user_id in room_members[room_name]:
        if user_id == skip_user:
            continue
        await bot.send_message(user_id, message)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    from messages import WELCOME_MESSAGE
    await message.answer(WELCOME_MESSAGE)

VISIBILITY = {
    "private": False,
    "public": True
}

VISIBILITY_LABELS = {
    True: "ОТКРЫТАЯ",
    False: "ЗАКРЫТАЯ"
}

@dp.message(Command("create"))

@validate_parse
async def cmd_create(message: types.Message, command: CommandObject):
    room_name, *rest = command.args.split()

    if not rest:
        is_public = False
    else:
        if len(rest) != 1 or rest[0] not in VISIBILITY:
            raise CommandParseError("2 аргумент должен иметь private/public/ПУСТО")
        is_public = VISIBILITY[rest[0]]
    
    make_create(room_name, is_public)
    await message.answer(f"Создана {VISIBILITY_LABELS[is_public]} комната по имени : {room_name}")


@dp.message(Command("join"))
@validate_parse
async def cmd_join(message: Message, command: CommandObject):

    room_name, *access = command.args.split()

    if not room_name:
        raise CommandParseError("Не передан аргкумент")

    if room_name not in room_members:
        raise CommandParseError("Нет такой комнаты")

    user_id = message.from_user.id

    join_remove(user_id)
    join_add(room_name, user_id)

    user_room[user_id] = room_name
    from data import generate_nick
    name[user_id] = generate_nick()
    x  = l_user_names(room_name)
    full_user_names = ", ".join(x)
    if len(x) == 1:
        full_user_names = "Только <b>вы</b>"

    await message.answer(f"Вы успешно присоединились. Ваше имя: {name[user_id]}, в комнате есть: {full_user_names}")

    mess = f"К вам присоединился(ась): {name[user_id]}"

    await send_to_chat(user_room[user_id], user_id, mess)

@dp.message(Command("part"))
async def cmd_part(message: Message):
    user_id = message.from_user.id

    if user_id not in user_room:
        await message.answer("Вы не в комнате")
        return
    room_name_part = user_room[user_id]
    user_room.pop(user_id)
    room_members[room_name_part].remove(user_id)

    mes = f"{name[user_id]} вышел(а) из комнаты"

    await send_to_chat(room_name_part, user_id, mes)

    await message.answer("Вы вышли из комноты, теперь вы не состоите ни в какой группе")

@dp.message(Command("list"))
async def cmd_list(message: Message):
    full_massage = "Нет открытых комнат"
    list_of_message = []
    for key in room_members.keys():
        if room_visibility[key] == True:
            l = []
            if room_members[key] == set():
                part_of_message = f"{key}: Пусто"
            else:
                for c in room_members[key]:
                    l.append(name[c])
                str_of_message = ", ".join(l)
                part_of_message = f"{key}: {str_of_message}"
            list_of_message.append(part_of_message)
            full_massage = ", ".join(list_of_message)

    await message.answer(full_massage)

@dp.message()
async def annon_mess(message: Message):
    if len(user_room)==1:
        await message.answer("Вы 1 в комнате")

    user_id = message.from_user.id

    if message.from_user.id not in user_room:
        await message.answer("Вы не в комнате")
        return

    message = f"{name[message.from_user.id]}: {message.text}"

    await send_to_chat(user_room[user_id], user_id, message)

async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())