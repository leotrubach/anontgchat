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

from package_storage import storage
from exceptions import CommandParseError
from decorators import parse_2_args, parse_1_arg
from data import VISIBILITY

dotenv.load_dotenv()
TOKEN = getenv("BOT_TOKEN")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    from messages import WELCOME_MESSAGE

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
    access = storage.create(is_public, room_name, user_id)
    await message.answer(f"Создана {access} комната по имени : {room_name}")


@dp.message(Command("join"))
@parse_2_args
async def cmd_join(message: Message, command: CommandObject):
    user_id = message.from_user.id
    if not command.args:
        raise CommandParseError("Не передан аргумент")
    room_name, *access = command.args.split()

    full_user_names, nick, room = storage.join(room_name, user_id)
    await message.answer(
        f"Вы успешно присоединились. Ваш ник: {nick}, в комнате есть: {full_user_names}"
    )

    mess = f"К вам присоединился(ась): {nick}"

    await storage.send_to_chat(room, user_id, mess)


@dp.message(Command("del"))
@parse_2_args
async def delete(message: Message, command: CommandObject):
    if not command.args:
        raise CommandParseError("Не передан аргумент")
    user_id = message.from_user.id
    room_name, *access = command.args.split()
    storage.delete(room_name, user_id)
    await message.answer("Комната успешно удалена")


@dp.message(Command("part"))
@parse_1_arg
async def cmd_part(message: Message):
    user_id = message.from_user.id

    mes, room_name_part = storage.part(user_id)
    await storage.send_to_chat(room_name_part, user_id, mes)

    await message.answer("Вы вышли из комнаты, теперь вы не состоите ни в какой группе")


@dp.message(Command("list"))
async def cmd_list(message: Message):
    full_message = storage.list()

    await message.answer(full_message)


@dp.message()
@parse_1_arg
async def default_handler(message: Message):
    user_id = message.from_user.id
    part_of_mes, room_name = storage.annon(user_id)
    message = f"{part_of_mes}: {message.text}"
    await storage.send_to_chat(room_name, user_id, message)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
