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




class CommandParseError(Exception):
    def __init__(self, message):
        self.message = message
class UserIsNotMemberOfRoom(Exception):
    def __init__(self, message):
        self.message = message


def parse(wrapped):
    async def wrapper(message: types.Message):
        try:
            await wrapped(message=message)
        except UserIsNotMemberOfRoom as l:
            await message.answer(l.message)
    return wrapper

def validate_parse(wrappe):
    async def wrapp(message: types.Message, command: CommandObject):
        try:
            await wrappe(message=message, command=command)
        except CommandParseError as e:
            await message.answer(e.message)
    return wrapp

class MemoryStorage:
    def __init__(self):
        self.room_members = {}
        self.room_visibility = {}
        self.user_room = {}
        self.name = {}

    def l_user_names(self, room_name):
        return [self.name[user_id] for user_id in self.room_members[room_name]]

    def join_add(self, room_name: str, user_id: int):
        self.room_members[room_name].add(user_id)

    def quit_room(self, user_id):
        if user_id in self.user_room:
            name_room = self.user_room[user_id]
            if self.room_members[name_room] != set():
                self.room_members[name_room].remove(user_id)

    def make_create(self,room_name: str, is_public: bool):
        if room_name in self.room_members:
            raise CommandParseError("Уже есть комната с таким назвванием")
        self.room_members[room_name] = set()
        self.room_visibility[room_name] = is_public

    def get_room_members(self,room_name):
        return self.room_members[room_name]
    async def send_to_chat(self,room_name: str, skip_user: int, message: str):
        for user_id in self.get_room_members(room_name):
            if user_id == skip_user:
                continue
            await bot.send_message(user_id, message)
storage = MemoryStorage()
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
    
    storage.make_create(room_name, is_public)
    await message.answer(f"Создана {VISIBILITY_LABELS[is_public]} комната по имени : {room_name}")


@dp.message(Command("join"))
@validate_parse
async def cmd_join(message: Message, command: CommandObject):
    if not command.args:
        raise CommandParseError("Не передан аргкумент")
    room_name, *access = command.args.split()

    if room_name not in storage.room_members:
        raise CommandParseError("Нет такой комнаты")

    user_id = message.from_user.id

    storage.quit_room(user_id)
    storage.join_add(room_name, user_id)

    storage.user_room[user_id] = room_name
    from data import generate_nick
    storage.name[user_id] = generate_nick()
    x = storage.l_user_names(room_name)
    full_user_names = ", ".join(x)
    if len(x) == 1:
        full_user_names = "Только <b>вы</b>"

    await message.answer(f"Вы успешно присоединились. Ваше имя: {storage.name[user_id]}, в комнате есть: {full_user_names}")

    mess = f"К вам присоединился(ась): {storage.name[user_id]}"

    await storage.send_to_chat(storage.user_room[user_id], user_id, mess)

@dp.message(Command("part"))
async def cmd_part(message: Message):
    user_id = message.from_user.id

    if user_id not in storage.user_room:
        await message.answer("Вы не в комнате")
        return
    room_name_part = storage.user_room[user_id]
    storage.user_room.pop(user_id)
    storage.room_members[room_name_part].remove(user_id)

    mes = f"{storage.name[user_id]} вышел(а) из комнаты"

    await storage.send_to_chat(room_name_part, user_id, mes)

    await message.answer("Вы вышли из комноты, теперь вы не состоите ни в какой группе")

@dp.message(Command("list"))
async def cmd_list(message: Message):
    full_massage = "Нет открытых комнат"
    list_of_message = []
    for key in storage.room_members.keys():
        if storage.room_visibility[key] == True:
            l = []
            if storage.room_members[key] == set():
                part_of_message = f"{key}: Пусто"
            else:
                for c in storage.room_members[key]:
                    l.append(storage.name[c])
                str_of_message = ", ".join(l)
                part_of_message = f"{key}: {str_of_message}"
            list_of_message.append(part_of_message)
            full_massage = ", ".join(list_of_message)

    await message.answer(full_massage)

@dp.message()
@parse
async def annon_mess(message: Message):
    if len(storage.user_room) == 1:
        raise UserIsNotMemberOfRoom("Вы 1 в комнате")

    user_id = message.from_user.id

    if user_id not in storage.user_room:
        raise UserIsNotMemberOfRoom("Вы не в комнате")

    message = f"{storage.name[user_id]}: {message.text}"

    await storage.send_to_chat(storage.user_room[user_id], user_id, message)

async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())