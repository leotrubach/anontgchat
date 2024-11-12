from data import generate_nick
from exceptions import RoomDoesNotExist, RoomAlreadyExists, NotInRoom, NoCreator


class MemoryStorage:

    def __init__(self):
        # имя комноты : сет user_id
        self.room_members = {}

        # имя комноты:  открыта или нет
        self.room_visibility = {}

        # user_id : имя комноты
        self.user_room = {}

        # user_id :nickname
        self.name = {}

        # имя комноты  : user_id
        self.creators = {}

    def list_of_user_names(self, room_name):
        return [self.name[user_id] for user_id in self.room_members[room_name]]

    def quit_room(self, user_id):
        if user_id in self.user_room:
            name_room = self.user_room[user_id]
            self.room_members[name_room].discard(user_id)

    def get_room_members(self, room_name):
        return self.room_members[room_name]

    def create(self, is_public, room_name, user_id):
        if room_name in self.room_members:
            raise RoomAlreadyExists("Уже есть комната с таким названием")
        self.room_members[room_name] = set()
        self.creators[room_name] = user_id
        self.room_visibility[room_name] = is_public

    def user_room_by_id(self, user_id):
        return self.user_room[user_id]

    def list_of_user_names_by_room_name(self, room_name):
        return self.list_of_user_names(room_name)

    def gen_nick(self, user_id):
        self.name[user_id] = generate_nick()
        return self.name

    def join(self, room_name, user_id):
        if room_name not in self.room_members:
            raise RoomDoesNotExist("Нет такой комнаты")
        self.quit_room(user_id)
        self.room_members[room_name].add(user_id)
        self.user_room[user_id] = room_name
        self.gen_nick(user_id)
        return self.name[user_id]

    def part(self, user_id):

        if user_id not in self.user_room:
            raise NotInRoom("Вы не в комнате")

        self.room_members[self.user_room_by_id(user_id)].discard(user_id)

        self.user_room.pop(user_id)

        return self.name[user_id]

    def list(self):
        l = []
        for key, value in self.room_visibility.items():
            if value:
                l.append(key)
        return l

    def delete_room(self, room_name, user_id):
        list_of_id = []
        if room_name not in self.creators:
            raise RoomDoesNotExist("Нет такой комнаты")
        if self.creators[room_name] != user_id:
            raise NoCreator("Вы не создатель")
        for key in self.user_room.keys():
            if self.user_room[key] == room_name:
                list_of_id.append(key)
        for key in list_of_id:
            self.user_room.pop(key)

        self.creators.pop(room_name)
        self.room_members.pop(room_name)
        self.room_visibility.pop(room_name)
        return list_of_id

    def is_user_in_room(self, user_id):

        if user_id not in self.user_room:
            raise NotInRoom("Вы не в комнате")

        return self.name[user_id]
