from data import generate_nick
from exceptions import RoomDoesNotExist, RoomAlreadyExists, NotInRoom, NoCreator
import json


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

        # nickname : user_id
        self.name_reverse = {}

    def list_of_user_names(self, room_name) -> list:
        """Возвращает список никнеймов"""
        return [self.name[user_id] for user_id in self.room_members[room_name]]

    def quit_room(self, user_id) -> None:
        """удоляет участника из комнаты"""
        if user_id in self.user_room:
            name_room = self.user_room[user_id]
            self.room_members[name_room].discard(user_id)

    def get_room_members(self, room_name) -> str:
        """возвращает id всех учасников в комнате"""
        if self.room_members == {}:
            raise RoomDoesNotExist("Нет такой комнаты")
        return self.room_members[room_name]

    def create(self, is_public, room_name, user_id) -> None:
        """Создание комноты.

        В начале проверяется есть ли эта комната.(Выдается ошибка)
        В словаре room_members создается имя комноты со значением set()
        В словаре creators создается имя комноты со значением user_id
        В словаре room_visibility создается имя комноты со значением True or False
        """
        if room_name in self.room_members:
            raise RoomAlreadyExists("Уже есть комната с таким названием")
        self.room_members[room_name] = set()
        self.creators[room_name] = user_id
        self.room_visibility[room_name] = is_public
        return self.room_visibility[room_name]

    def user_room_by_id(self, user_id) -> dict:
        """Возвращает имя комнаты где находится учасник"""

        return self.user_room[user_id]

    def gen_nick(self, user_id) -> dict:
        """Генерирует ник и добавляет в словарь"""
        nick = generate_nick()
        self.name[user_id] = nick
        self.name_reverse[nick] = user_id
        return self.name

    def get_nick(self, user_id):
        return self.name[user_id]

    def join(self, room_name, user_id) -> str:
        """Добавляет участника в комноту

        Проверяет есть ли такая комната.(Выдает ошибку)
        Выходит из всех комнат.(Если до этого он был в другой)
        В словаре room_members добавляется в set  id пользователя
        В словаре user_room создается id пользователя со значением именем комнаты
        Добавляется сгенерированый ник
        Возвращает ник пользователя
        """
        if room_name not in self.room_members:
            raise RoomDoesNotExist("Нет такой комнаты")
        self.quit_room(user_id)
        self.room_members[room_name].add(user_id)
        self.user_room[user_id] = room_name
        self.gen_nick(user_id)
        return self.name[user_id]

    def part(self, user_id) -> str:
        """Выход из комнаты

        Проверяет в комнате ли пользователь.(Выдает ошибку)
        Удоляет пользователя из словаря room_members и user_room по id
        Возвращяет никнейм
        """

        if user_id not in self.user_room:
            raise NotInRoom("Вы не в комнате")

        self.room_members[self.user_room_by_id(user_id)].discard(user_id)

        self.user_room.pop(user_id)

        return self.name[user_id]

    def list(self) -> list:
        """Возвраящает список комнат"""
        l = []
        for key, value in self.room_visibility.items():
            if value:
                l.append(key)
        return l

    def delete_room(self, room_name, user_id) -> list:
        """Удаление комнаты

        Проверяет есть ли комната.(Выдает ошибку)
        Удоляет пользователя из user_room,creators,room_members (пропадает комната),room_visibility
        """
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

    def kick_user(self, user_id, user_nick) -> None:
        """
        Если вы не создатель выдает ошибку
        Удаление пользователя из set() в room_members
        """
        if self.creators[self.user_room[user_id]] != user_id:
            raise NoCreator("Вы не создатель комнаты")
        room_name = self.user_room[self.name_reverse[user_nick]]
        self.room_members[room_name].discard(self.name_reverse[user_nick])

    def is_user_in_room(self, user_id) -> str:
        """Проверяет находится ли пользователь в комнате проо отправке сообщения"""
        if user_id not in self.user_room:
            raise NotInRoom("Вы не в комнате")
        return self.name[user_id]
