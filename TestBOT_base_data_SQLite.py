import unittest

import sqlite3
import exceptions
from storage.data_base_by_SQLite import DataBaseStorageBySQLite

"""
Тесты:
- join в существующую комнату +
- join в несуществующую комнату + 
- join когда не в комнате +
- join когда уже в той комнате, куда присоединяется + 
- join когда в другой комнате + 
- part когда в комнате + 
- part когда не в комнате + 
- create когда комната уже есть с таким именем + 
- create когда комнаты нет с таким именем + 
- create приватной комнаты + 
- create публичной комнаты +
- delete когда комната есть + 
- delete когда комнаты нет +
- list  + 
"""


class SimpleUnitTest(unittest.TestCase):
    storage_class = DataBaseStorageBySQLite

    def drop_table(self):
        self.connection = sqlite3.connect("database_SQLite/database.db")
        with self.connection as conn:
            cur = conn.cursor()
            cur.execute("DROP TABLE IF  EXISTS room ")
            cur.execute("DROP TABLE IF  EXISTS room_members ")
            cur.execute("DROP TABLE IF  EXISTS nickname ")

    def test_kick(self):
        self.drop_table()
        storage = self.storage_class()
        storage.create(True, "csgo", 1212)
        storage.join("csgo", 1212)
        user_1 = storage.join("csgo", 1111)
        storage.kick_user(1212, user_1)
        self.assertEqual(storage.get_room_members("csgo"), [1212])
        self.drop_table()

    def test_join_exist_room(self):
        self.drop_table()

        storage = self.storage_class()
        storage.create(True, "csgo", 1212)
        storage.join("csgo", 1212)
        self.assertEqual(storage.get_room_members("csgo"), [1212])
        self.assertEqual(storage.user_room_by_id(1212), "csgo")
        self.drop_table()

    def test_join_no_exist_room(self):
        self.drop_table()

        storage = self.storage_class()
        storage.create(True, "csgo", 1212)
        with self.assertRaises(exceptions.RoomDoesNotExist):
            storage.join("csgo2", 1212)
        self.drop_table()

    def test_join_in_room(self):
        self.drop_table()

        storage = self.storage_class()
        storage.create(True, "csgo2", 1212)
        storage.create(True, "csgo", 1212)
        storage.join("csgo", 1212)

        self.assertEqual(storage.get_room_members("csgo"), [1212])
        self.assertNotIn(1212, storage.get_room_members("csgo2"))
        self.assertEqual(storage.user_room_by_id(1212), "csgo")
        self.drop_table()

    def test_join_other_room(self):
        self.drop_table()

        storage = self.storage_class()
        storage.create(True, "csgo", 1212)
        storage.join("csgo", 1212)
        storage.create(True, "csgo2", 1212)
        storage.join("csgo2", 1212)
        self.assertEqual(storage.get_room_members("csgo2"), [1212])
        self.assertNotIn(1212, storage.get_room_members("csgo"))
        self.drop_table()

    def test_part(self):
        self.drop_table()

        storage = self.storage_class()
        storage.create(True, "csgo", 1212)
        storage.join("csgo", 1212)
        storage.part(1212)
        self.assertEqual(storage.get_room_members("csgo"), [])
        self.assertNotIn(1212, storage.get_room_members("csgo"))
        self.drop_table()

    def test_part_no_in_room(self):

        self.drop_table()

        storage = self.storage_class()
        with self.assertRaises(exceptions.NotInRoom):
            storage.part(1212)
        self.drop_table()

    def test_create_have_already(self):
        self.drop_table()

        storage = self.storage_class()
        storage.create(True, "csgo", 1212)
        with self.assertRaises(exceptions.RoomAlreadyExists):
            storage.create(True, "csgo", 1212)
        self.drop_table()

    def test_create(self):
        self.drop_table()

        storage = self.storage_class()
        storage.create(True, "csgo", 1212)
        self.assertEqual(storage.get_room_members("csgo"), [])
        self.assertEqual(storage.get_user_create("csgo"), 1212)
        self.drop_table()

    def test_create_public(self):
        self.drop_table()

        storage = self.storage_class()
        is_public = storage.create(True, "csgo", 1212)
        self.assertTrue(is_public)
        self.drop_table()

    def test_create_private(self):
        self.drop_table()

        storage = self.storage_class()
        is_public = storage.create(False, "csgo", 1212)
        self.assertFalse(is_public)
        self.drop_table()

    def test_delete_have_room(self):
        self.drop_table()

        storage = self.storage_class()
        storage.create(True, "csgo", 1212)
        storage.delete_room("csgo", 1212)
        with self.assertRaises(exceptions.RoomDoesNotExist):
            storage.get_room_members("csgo")
        self.drop_table()

    def test_delete_do_not_have_room(self):
        self.drop_table()

        storage = self.storage_class()
        with self.assertRaises(exceptions.RoomDoesNotExist):
            storage.delete_room("csgo", 1212)
        self.drop_table()

    def test_list(self):
        self.drop_table()

        storage = self.storage_class()
        storage.create(True, "csgo", 1212)
        list = storage.list()
        self.assertEqual(list, ["csgo"])
        self.drop_table()
