from exceptions import BotError
from aiogram.filters.command import CommandObject
from aiogram import types


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
