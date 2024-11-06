from aiogram.client import bot

from exceptions import RoomDoesNotExist, RoomAlreadyExists, NotInRoom, NoCreator
from data import VISIBILITY_LABELS


class MemoryStorage:
    def __init__(self):
        self.room_members = {}
        self.room_visibility = {}
        self.user_room = {}
        self.name = {}
        self.creators = {}

    def list_of_user_names(self, room_name):
        return [self.name[user_id] for user_id in self.room_members[room_name]]

    def make_add(self, room_name: str, user_id: int):
        self.room_members[room_name].add(user_id)

    def quit_room(self, user_id):
        if user_id in self.user_room:
            name_room = self.user_room[user_id]
            if self.room_members[name_room] != set():
                self.room_members[name_room].discard(user_id)

    def make_create(self, room_name: str, is_public: bool, user_id):
        if room_name in self.room_members:
            raise RoomAlreadyExists("Уже есть комната с таким названием")
        self.room_members[room_name] = set()
        self.creators[room_name] = user_id
        self.room_visibility[room_name] = is_public

    def get_room_members(self, room_name):
        return self.room_members[room_name]

    def create(self, is_public, room_name, user_id):
        self.make_create(room_name, is_public, user_id)
        return VISIBILITY_LABELS[is_public]

    def join(self, room_name, user_id):
        if room_name not in storage.room_members:
            raise RoomDoesNotExist("Нет такой комнаты")
        self.quit_room(user_id)
        self.make_add(room_name, user_id)

        self.user_room[user_id] = room_name
        from data import generate_nick

        self.name[user_id] = generate_nick()

        x = self.list_of_user_names(room_name)
        full_user_names = ", ".join(x)
        if len(x) == 1:
            full_user_names = "Только <b>вы</b>"

        return full_user_names, self.name[user_id], self.user_room[user_id]

    def part(self, user_id):

        if user_id not in self.user_room:
            raise NotInRoom("Вы не в комнате")
        room_name_part = self.user_room[user_id]
        self.user_room.pop(user_id)
        self.room_members[room_name_part].discard(user_id)

        return f"{self.name[user_id]} вышел(а) из комнаты", room_name_part

    def list(self):
        full_massage = "Нет открытых комнат"
        list_of_message = []
        for key in self.room_members.keys():
            if self.room_visibility[key] == True:
                l = []
                if self.room_members[key] == set():
                    part_of_message = f"{key}: Пусто"
                else:
                    for c in self.room_members[key]:
                        l.append(self.name[c])
                    str_of_message = ", ".join(l)
                    part_of_message = f"{key}: {str_of_message}"
                list_of_message.append(part_of_message)
                full_massage = ", ".join(list_of_message)
        return full_massage

    def delete(self, room_name, user_id):
        if room_name not in self.creators:
            raise RoomDoesNotExist("Нет такой комнаты")
        if self.creators[room_name] != user_id:
            raise NoCreator("Вы не создатель")
        self.creators.pop(room_name)
        self.room_members.pop(room_name)

    def annon(self, user_id):

        if user_id not in self.user_room:
            raise NotInRoom("Вы не в комнате")

        return self.name[user_id], self.user_room[user_id]

    async def send_to_chat(self, room_name: str, skip_user: int, message: str):
        for user_id in self.get_room_members(room_name):
            if user_id == skip_user:
                continue
            await bot.send_message(user_id, message)


storage = MemoryStorage()
