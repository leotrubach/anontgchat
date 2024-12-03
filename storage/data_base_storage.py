from data import generate_nick
from exceptions import RoomDoesNotExist, RoomAlreadyExists, NotInRoom, NoCreator
import psycopg


class DataBaseStorage:
    def __init__(self):

        self.connection = psycopg.connect(
            "postgres://postgres:Arkasha2007@127.0.0.1:5432/postgres"
        )
        self.connection.autocommit = True

        with self.connection.cursor() as cur:
            cur.execute(
                "CREATE TABLE IF NOT EXISTS room(id SERIAL PRIMARY KEY,name TEXT NOT NULL,creator_user_id integer NOT NULL,is_private BOOLEAN)"
            )
            cur.execute(
                "CREATE TABLE IF NOT EXISTS room_members (id SERIAL REFERENCES room ( id ), user_id integer NOT NULL)"
            )
            cur.execute(
                "CREATE TABLE IF NOT EXISTS nickname (user_id integer NOT NULL,nick TEXT NOT NULL)"
            )

    def select_data(self, command: str, params: tuple):
        with self.connection.cursor() as cur:
            cur.execute(command, params)
            return cur.fetchall()

    def data(self, command: str, params: tuple):
        with self.connection.cursor() as cur:
            cur.execute(command, params)

    def get_room_members(self, room_name) -> list:
        """возвращает id всех учасников в комнате"""
        cur = self.select_data("SELECT 1 FROM room WHERE name = %s", (room_name,))
        if not cur:
            raise RoomDoesNotExist("Нет такой комнаты")

        x = []
        v = self.select_data(
            f"SELECT room_members.user_id FROM room_members JOIN room ON room_members.id = room.id WHERE room.name = %s",
            (room_name,),
        )
        for i in v:
            x.append(i[0])
        return x

    def get_user_create(self, room_name):
        return self.select_data(
            f"SELECT room.creator_user_id FROM room WHERE name = %s", (room_name,)
        )[0][0]

    def create(self, is_public, room_name, user_id) -> None:
        """Создание комноты.

        В начале проверяется есть ли эта комната.(Выдается ошибка)
        В словаре room_members создается имя комноты со значением set()
        В словаре creators создается имя комноты со значением user_id
        В словаре room_visibility создается имя комноты со значением True or False
        """
        with self.connection.cursor() as cur:
            cur.execute(
                "CREATE TABLE IF NOT EXISTS room(id SERIAL PRIMARY KEY,name TEXT NOT NULL,creator_user_id integer NOT NULL,is_private BOOLEAN)"
            )

        with self.connection.cursor() as cur:
            cur.execute(
                "CREATE TABLE IF NOT EXISTS room_members (id SERIAL REFERENCES room ( id ), user_id integer NOT NULL)"
            )
        cur = self.select_data(f"SELECT 1 FROM room WHERE name = %s", (room_name,))
        if cur:
            raise RoomAlreadyExists("Уже есть комната с таким названием")

        with self.connection.cursor() as cur:
            cur.execute(
                f"INSERT INTO room ( name, creator_user_id, is_private) VALUES (%s, %s , %s)",
                (room_name, user_id, is_public),
            )

        return self.select_data(
            f"SELECT room.name FROM room WHERE name = %s AND is_private = True",
            (room_name,),
        )

    def user_room_by_id(self, user_id: int) -> str:
        """Возвращает имя комнаты где находится учасник"""
        cur = self.select_data(
            f"SELECT 1 FROM room_members WHERE user_id = %s", (user_id,)
        )
        if not cur:
            raise NotInRoom("Вы не в комнате")

        x = self.select_data(
            f"SELECT room.name FROM room_members JOIN room ON room.id = room_members.id WHERE user_id = %s",
            (user_id,),
        )[0][0]

        return x

    def get_nick(self, user_id: int) -> list:

        x = self.select_data(
            f"SELECT nickname.nick FROM nickname WHERE user_id = %s", (user_id,)
        )[0][0]
        return x

    def join(self, room_name, user_id) -> str:
        """Добавляет участника в комноту

        Проверяет есть ли такая комната.(Выдает ошибку)
        Выходит из всех комнат.(Если до этого он был в другой)
        В словаре room_members добавляется в set  id пользователя
        В словаре user_room создается id пользователя со значением именем комнаты
        Добавляется сгенерированый ник
        Возвращает ник пользователя
        """
        cur = self.select_data(f"SELECT 1 FROM room WHERE name = %s", (room_name,))
        if not cur:
            raise RoomDoesNotExist("Нет такой комнаты")

        with self.connection.cursor() as cur:
            cur.execute(f"DELETE FROM room_members WHERE user_id = %s", (user_id,))

        room_id = self.select_data(
            f"SELECT room.id FROM room WHERE name = %s", (room_name,)
        )
        self.data(
            f"INSERT INTO room_members (id, user_id)  VALUES (%s,%s)",
            (room_id[0][0], user_id),
        )
        self.data(f"DELETE FROM nickname WHERE user_id =%s", (user_id,))

        nick = generate_nick()
        self.data(
            "INSERT INTO nickname (user_id, nick) VALUES (%s, %s)", (user_id, nick)
        )
        return nick

    def part(self, user_id) -> str:
        """Выход из комнаты

        Проверяет в комнате ли пользователь.(Выдает ошибку)
        Удоляет пользователя из словаря room_members и user_room по id
        Возвращяет никнейм
        """

        cur = self.select_data(
            f"SELECT 1 FROM room_members WHERE user_id = %s", (user_id,)
        )
        if not cur:
            raise NotInRoom("Вы не в комнате")

        self.data(f"DELETE FROM room_members WHERE user_id = %s", (user_id,))
        return self.select_data(
            f"SELECT nickname.nick FROM nickname WHERE user_id = %s", (user_id,)
        )[0][0]

    def list(self) -> list:
        """Возвраящает список комнат"""

        x = []
        with self.connection.cursor() as cur:
            cur.execute("SELECT room.name FROM room WHERE is_private = True ")
            v = cur.fetchall()
        for i in v:
            x.append(i[0])
        return x

    def delete_room(self, room_name, user_id) -> list:
        """Удаление комнаты

        Проверяет есть ли комната.(Выдает ошибку)
        Удоляет пользователя из user_room,creators,room_members (пропадает комната),room_visibility
        """
        list_of_id = []

        cur = self.select_data(f"SELECT 1 FROM room WHERE name = %s", (room_name,))
        if not cur:
            raise RoomDoesNotExist("Нет такой комнаты")

        cur = self.select_data(
            "SELECT 1 FROM room WHERE creator_user_id = %s AND name = %s",
            (user_id, room_name),
        )
        if not cur:
            raise NoCreator("Вы не создатель")

        room_id = next(
            iter(
                self.select_data(
                    f"SELECT room.id FROM room WHERE room.name= %s", (room_name,)
                )
            )
        )[0]
        x = self.select_data(
            f"SELECT room_members.user_id FROM room_members WHERE id = %s",
            (room_id,),
        )
        for b in x:
            list_of_id.append(b[0])
        self.data(f"DELETE FROM room_members WHERE id =%s", (room_id,))
        with self.connection.cursor() as cur:
            cur.execute(f"DELETE FROM room WHERE name = %s", (room_name,))
        return list_of_id

    def kick_user(self, user_id, user_nick, access) -> None:
        """
        Если вы не создатель выдает ошибку
        Удаление пользователя из set() в room_members
        """
        room_id_by_room_members = list(
            next(
                iter(
                    self.select_data(
                        f"SELECT room_members.id FROM room_members WHERE user_id = %s",
                        (user_id,),
                    )
                )
            )
        )[0]
        creator_user_id_by_room = self.select_data(
            f"SELECT room.creator_user_id FROM room WHERE id = %s",
            (room_id_by_room_members,),
        )[0][0]
        if user_id != creator_user_id_by_room:
            raise NoCreator("Вы не создатель")
        user_nick = f"{user_nick} {access}"
        v = self.select_data(
            f"SELECT nickname.user_id FROM nickname WHERE nick = %s", (user_nick,)
        )[0][0]
        self.data(f"DELETE FROM room_members WHERE user_id = %s ", (v,))

    def is_user_in_room(self, user_id) -> str:
        """Проверяет находится ли пользователь в комнате проо отправке сообщения"""
        cur = self.select_data(
            f"SELECT 1 FROM room_members WHERE user_id = %s", (user_id,)
        )
        if not cur:
            raise NotInRoom("Вы не в комнате")

        return self.select_data(
            f"SELECT nickname.nick FROM nickname WHERE user_id = %s", (user_id,)
        )[0][0]
