import asyncio
import logging
import sys
from os import getenv
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters.command import Command, CommandObject
from aiogram.types import Message
from aiogram.filters import Command
import dotenv
dotenv.load_dotenv()

TOKEN = getenv("BOT_TOKEN")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()

room_members_public = {}

room_members_private = {}

user_room = {}

name = {}

# class CommandParseError(Exception):
#     def __init__(self, message):
#         self.message = message

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Это анонимный чат. \nТы можешь создать открытую /create <название комнаты> <public> \nили \nзакрытую/create <название комнаты> <ничего/private> комнату для общения.\n С помощью /list ты можешь посмотреть ОТКРЫТЫЕ комнаты.\n С помощью /part ты можешь выйти из комнаты.\n Желаем хорошо пообщяться :) ")


# def parse_room_name(command: CommandObject):
#     if command.args is None:
#         raise CommandParseError("Ошибка: не переданы аргументы")
#
#
#     args = command.args.split()
#
#     if len(args) == 1:
#         raise CommandParseError("Создана закрытая комната (по умолчанию)")
#

#     room_name = args[0]

#     return room_name


# def validate_parse(wrapped):
#     async def wrapper(message: types.Message, command: CommandObject):
#         try:
#             await wrapped(message=message, command=command)
#         except CommandParseError as e:
#             await message.answer(e.message)
#
#
#     return wrapper
async def return_arg(command, message):
    try:
        try:
            room_name, access = command.args.split()
            if access == "private":
                room_members_private[room_name[0]] = set()
                await message.answer(f"Создана ЗАКРЫТАЯ комната по имени: {room_name[0]}")
            if access == "public":
                room_members_public[room_name[0]] = set()
                await message.answer(f"Создана ОТКРЫТАЯ комната по имени: {room_name[0]}")
        except ValueError:
            room_name = command.args.split()
            room_members_private[room_name[0]] = set()
            await message.answer(f"Создана ЗАКРЫТАЯ (по умолчанию) комната по имени : {room_name[0]}")
    except AttributeError:
        await message.answer("Ошибка: не переданы аргументы")

async def send_to_chat(room_name: str, skip_user: int, message: str):
    def send_message(user_id,skip_user):
        if user_id == skip_user:
            return
        bot.send_message(user_id, message)

    if room_name[0] in room_members_public:
        for user_id in room_members_public[room_name]:
            send_message(user_id, skip_user)
        return
    else:
        for user_id in room_members_private[room_name]:
            send_message(user_id, skip_user)
        return


@dp.message(Command("create"))
# @validate_parse
async def cmd_create(message: types.Message, command: CommandObject):
    await return_arg(command, message)


@dp.message(Command("join"))
# @validate_parse
async def cmd_join(message: Message, command: CommandObject):
    try:
        try:
            room_name, access = command.args.split()
        except ValueError:
            room_name = command.args.split()
        if room_name[0] not in room_members_public:
            if room_name[0]not in room_members_private:
                await message.answer(f"Нет такой комнаты{room_members_public} {room_members_private}")
                return


        if message.from_user.id in user_room:
            try:
                if room_members_private[user_room[message.from_user.id]] != set():
                    room_members_private[user_room[message.from_user.id]].remove(message.from_user.id)
            except KeyError:
                if room_members_public[user_room[message.from_user.id]] != set():
                    room_members_public[user_room[message.from_user.id]].remove(message.from_user.id)

        if room_name[0] in room_members_private:
            room_members_private[room_name[0]].add(message.from_user.id)
        else:
            room_members_public[room_name[0]].add(message.from_user.id)
        user_room[message.from_user.id] = room_name[0]

        from data import generate_nick
        name[message.from_user.id] = generate_nick()
        user_names = []
        if room_name[0] in room_members_private:
            for l_user in room_members_private[room_name[0]]:
                if l_user == message.from_user.id:
                    continue
                user_names.append(name[l_user])
        else:
            for l_user in room_members_public[room_name[0]]:
                if l_user == message.from_user.id:
                    continue
                user_names.append(name[l_user])

        user_id = message.from_user.id
        full_user_names = ", ".join(user_names)

        if full_user_names == "":
            full_user_names = "Только <b>вы</b>"

        await message.answer(f"Вы успешно присоединились. Ваше имя: {name[message.from_user.id]}, в комнате есть: {full_user_names}")

        message = f"К вам присоединился: {name[message.from_user.id]}"

        await send_to_chat(user_room[user_id], user_id, message)
    except AttributeError:
        await message.answer("Ошибка: не передан аргумент")

@dp.message(Command("part"))
async def cmd_part(message: Message):
    try:
        try:
            room_members_public[user_room[message.from_user.id]].remove(message.from_user.id)
        except KeyError:
            room_members_private[user_room[message.from_user.id]].remove(message.from_user.id)

        messege = f"{name[message.from_user.id]} вышел из комнаты"

        user_id = message.from_user.id
        await send_to_chat(user_room[message.from_user.id],user_id, messege)

        await message.answer("Вы вышли из комноты, теперь вы не состоите ни в какой группе")
    except KeyError:
        await message.answer("Вы не в комнате")



@dp.message(Command("list"))
async def cmd_list(message: Message):
    try:
        list_of_message = []

        for key in room_members_public.keys():

            if room_members_public[key] == set():
                part_of_message = f"{key}: Пусто"

            else:
                l = []
                for c in room_members_public[key]:
                    l.append(name[c])
                str_of_message = ", ".join(l)
                part_of_message = f"{key}: {str_of_message}"

            list_of_message.append(part_of_message)
            full_massage = ", ".join(list_of_message)

        await message.answer(f"{full_massage}")
    except UnboundLocalError:
        await message.answer("Нет открытых комнат")


@dp.message()
async def annon_mess(message: Message):
    if user_room == {}:
        await message.answer("Вы не в комнате")
        return
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