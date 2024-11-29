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
import json
from exceptions import CommandParseError
from decorators import parse_2_args, parse_1_arg
from data import VISIBILITY
from data import VISIBILITY_LABELS
from storage.data_base_storage import DataBaseStorage
from messages import WELCOME_MESSAGE

dotenv.load_dotenv()
TOKEN = getenv("BOT_TOKEN")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()
storage = DataBaseStorage()


async def send_to_chat(room_name: str, skip_user: int, message: str):
    for user_id in storage.get_room_members(room_name):
        if user_id == skip_user:
            continue
        await bot.send_message(user_id, message)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(WELCOME_MESSAGE)


@dp.message(Command("create"))
@parse_2_args
async def cmd_create(message: types.Message, command: CommandObject):
    if not command.args:
        raise CommandParseError("Не передан аргумент")
    room_name, *rest = command.args.split()
    if not rest:
        is_public = False
    else:
        if len(rest) != 1 or rest[0] not in VISIBILITY:
            raise CommandParseError("2-й аргумент должен иметь private/public")
        is_public = VISIBILITY[rest[0]]
    user_id = message.from_user.id
    storage.create(is_public, room_name, user_id)
    await message.answer(
        f"Создана {VISIBILITY_LABELS[is_public]} комната по имени : {room_name}"
    )


@dp.message(Command("join"))
@parse_2_args
async def cmd_join(message: Message, command: CommandObject):
    user_id = message.from_user.id
    if not command.args:
        raise CommandParseError("Не передан аргумент")
    room_name, *access = command.args.split()

    nick = storage.join(room_name, user_id)
    x = list(map(storage.get_nick, storage.get_room_members(room_name)))
    full_user_names = ", ".join(x)
    if len(x) == 1:
        full_user_names = "Только <b>вы</b>"

    await message.answer(
        f"Вы успешно присоединились. Ваш ник: {nick}, в комнате есть: {full_user_names}"
    )

    mess = f"К вам присоединился(ась): {nick}"

    await send_to_chat(storage.user_room_by_id(user_id), user_id, mess)


@dp.message(Command("del"))
@parse_2_args
async def delete(message: Message, command: CommandObject):
    if not command.args:
        raise CommandParseError("Не передан аргумент")
    user_id = message.from_user.id
    room_name, *access = command.args.split()
    list_of_id = storage.delete_room(room_name, user_id)
    for id in list_of_id:
        if user_id == id:
            continue
        await bot.send_message(id, "Комната была удалена создателем")
    await message.answer("Комната успешно удалена")


@dp.message(Command("part"))
@parse_1_arg
async def cmd_part(message: Message):
    user_id = message.from_user.id
    room_name_part = storage.user_room_by_id(user_id)

    mes = storage.part(user_id)

    await send_to_chat(room_name_part, user_id, f"{mes} вышел(а) из комнаты")

    await message.answer("Вы вышли из комнаты, теперь вы не состоите ни в какой группе")


@dp.message(Command("list"))
@parse_1_arg
async def cmd_list(message: Message):
    list_of_rooms = storage.list()
    str_rooms = ", ".join(list_of_rooms)
    if not str_rooms:
        raise CommandParseError("Нет открытых комнат")
    await message.answer(str_rooms)


@dp.message(Command("kiсk"))
@parse_2_args
async def cmd_kiсk(message: Message, command: CommandObject):
    if not command.args:
        raise CommandParseError("Не передан аргумент")
    user_id = message.from_user.id
    user_nick, *access = command.args.split()

    storage.kick_user(user_id, user_nick)
    message = "Вы были выгнаны создателем комнаты"
    await send_to_chat(
        storage.user_room_by_id(user_id),
        user_id,
    )


@dp.message()
@parse_1_arg
async def default_handler(message: Message):
    user_id = message.from_user.id
    part_of_mes = storage.is_user_in_room(user_id)
    message = f"{part_of_mes}: {message.text}"
    await send_to_chat(storage.user_room_by_id(user_id), user_id, message)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
