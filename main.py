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


class BotError(Exception):
    def __init__(self, message):
        self.message = message


class CommandParseError(BotError):
    pass


def parse_2_args(wrapped):
    async def wrapper(message: types.Message, command: CommandObject):
        try:
            await wrapped(message=message, command=command)
        except BotError as e:
            await message.answer(e.message)

    return wrapper


def parse_1_arg(wrapped):
    async def wrapper(message: types.Message):
        try:
            await wrapped(message=message)
        except BotError as e:
            await message.answer(e.message)

    return wrapper


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
                self.room_members[name_room].discard(user_id)

    def make_create(self, room_name: str, is_public: bool):
        if room_name in self.room_members:
            raise CommandParseError("Уже есть комната с таким назвванием")
        self.room_members[room_name] = set()
        self.room_visibility[room_name] = is_public

    def get_room_members(self, room_name):
        return self.room_members[room_name]

    def part_of_create(self, is_public, room_name):
        storage.make_create(room_name, is_public)
        return VISIBILITY_LABELS[is_public]

    def part_of_join(self, room_name, user_id):
        if room_name not in storage.room_members:
            raise CommandParseError("Нет такой комнаты")
        storage.quit_room(user_id)
        storage.join_add(room_name, user_id)

        storage.user_room[user_id] = room_name
        from data import generate_nick

        storage.name[user_id] = generate_nick()

        x = storage.l_user_names(room_name)
        full_user_names = ", ".join(x)
        if len(x) == 1:
            full_user_names = "Только <b>вы</b>"

        return full_user_names, storage.name[user_id], storage.user_room[user_id]

    def part_of_part(self, user_id):

        if user_id not in storage.user_room:
            raise CommandParseError("Вы не в комнате")
        room_name_part = storage.user_room[user_id]
        storage.user_room.pop(user_id)
        storage.room_members[room_name_part].discard(user_id)

        return f"{storage.name[user_id]} вышел(а) из комнаты", room_name_part

    def part_of_list(self):
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
        return full_massage

    def part_of_annon(self, user_id):

        if len(storage.user_room) == 1:
            raise CommandParseError("Вы 1 в комнате")

        if user_id not in storage.user_room:
            raise CommandParseError("Вы не в комнате")

        return storage.name[user_id], storage.user_room[user_id]


async def send_to_chat(room_name: str, skip_user: int, message: str):
    for user_id in storage.get_room_members(room_name):
        if user_id == skip_user:
            continue
        await bot.send_message(user_id, message)


storage = MemoryStorage()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    from messages import WELCOME_MESSAGE

    await message.answer(WELCOME_MESSAGE)


VISIBILITY = {"private": False, "public": True}

VISIBILITY_LABELS = {True: "ОТКРЫТАЯ", False: "ЗАКРЫТАЯ"}


@dp.message(Command("create"))
@parse_2_args
async def cmd_create(message: types.Message, command: CommandObject):
    if not command.args:
        raise CommandParseError("Не передан аргкумент")
    room_name, *rest = command.args.split()
    if not rest:
        is_public = False
    else:
        if len(rest) != 1 or rest[0] not in VISIBILITY:
            raise CommandParseError("2 аргумент должен иметь private/public/ПУСТО")
        is_public = VISIBILITY[rest[0]]

    access = storage.part_of_create(is_public, room_name)
    await message.answer(f"Создана {access} комната по имени : {room_name}")


@dp.message(Command("join"))
@parse_2_args
async def cmd_join(message: Message, command: CommandObject):
    user_id = message.from_user.id
    if not command.args:
        raise CommandParseError("Не передан аргкумент")
    room_name, *access = command.args.split()

    full_user_names, nick, room = storage.part_of_join(room_name, user_id)
    await message.answer(
        f"Вы успешно присоединились. Ваше имя: {nick}, в комнате есть: {full_user_names}"
    )

    mess = f"К вам присоединился(ась): {nick}"

    await send_to_chat(room, user_id, mess)


@dp.message(Command("part"))
@parse_1_arg
async def cmd_part(message: Message):
    user_id = message.from_user.id

    mes, room_name_part = storage.part_of_part(user_id)
    await send_to_chat(room_name_part, user_id, mes)

    await message.answer("Вы вышли из комноты, теперь вы не состоите ни в какой группе")


@dp.message(Command("list"))
async def cmd_list(message: Message):
    full_message = storage.part_of_list()

    await message.answer(full_message)


@dp.message()
@parse_1_arg
async def annon_mess(message: Message):
    user_id = message.from_user.id
    part_of_mes, room_name = storage.part_of_annon(user_id)
    message = f"{part_of_mes}: {message.text}"
    await send_to_chat(room_name, user_id, message)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
