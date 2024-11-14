import unittest

import exceptions
from storage.memory import MemoryStorage

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
    def test_kick(self):
        storage = MemoryStorage()
        storage.create(True, "csgo", 1212)
        user_2 = storage.join("csgo", 1212)
        user_1 = storage.join("csgo", 1111)
        storage.kick_user(1212, user_1)
        self.assertEqual(storage.get_room_members("csgo"), {1212})
        self.assertTrue(storage.is_user_in_room(1212))

    def test_join_exist_room(self):
        storage = MemoryStorage()
        storage.create(True, "csgo", 1212)
        storage.join("csgo", 1212)
        self.assertEqual(storage.get_room_members("csgo"), {1212})

    def test_join_no_exist_room(self):
        storage = MemoryStorage()
        storage.create(True, "csgo", 1212)
        with self.assertRaises(exceptions.RoomDoesNotExist):
            storage.join("csgo2", 1212)

    def test_join_in_room(self):
        storage = MemoryStorage()
        storage.create(True, "csgo", 1212)
        storage.join("csgo", 1212)
        storage.create(True, "csgo2", 1212)
        storage.join("csgo", 1212)
        self.assertEqual(storage.get_room_members("csgo"), {1212})

    def test_join_other_room(self):
        storage = MemoryStorage()
        storage.create(True, "csgo", 1212)
        storage.join("csgo", 1212)
        storage.create(True, "csgo2", 1212)
        storage.join("csgo2", 1212)
        self.assertEqual(storage.get_room_members("csgo2"), {1212})

    def test_part(self):
        storage = MemoryStorage()
        storage.create(True, "csgo", 1212)
        storage.join("csgo", 1212)
        storage.part(1212)
        self.assertEqual(storage.get_room_members("csgo"), set())

    def test_part_no_in_room(self):
        storage = MemoryStorage()
        with self.assertRaises(exceptions.NotInRoom):
            storage.part(1212)

    def test_create_have_already(self):
        storage = MemoryStorage()
        storage.create(True, "csgo", 1212)
        with self.assertRaises(exceptions.RoomAlreadyExists):
            storage.create(True, "csgo", 1212)

    def test_create(self):
        storage = MemoryStorage()
        storage.create(True, "csgo", 1212)
        self.assertEqual(storage.get_room_members("csgo"), set())

    def test_create_public(self):
        storage = MemoryStorage()
        is_public = storage.create(True, "csgo", 1212)
        self.assertTrue(is_public)

    def test_create_private(self):
        storage = MemoryStorage()
        is_public = storage.create(False, "csgo", 1212)
        self.assertFalse(is_public)

    def test_delete_have_room(self):
        storage = MemoryStorage()
        storage.create(True, "csgo", 1212)
        storage.delete_room("csgo", 1212)
        with self.assertRaises(exceptions.RoomDoesNotExist):
            storage.get_room_members("csgo")

    def test_delete_do_not_have_room(self):
        storage = MemoryStorage()
        with self.assertRaises(exceptions.RoomDoesNotExist):
            storage.delete_room("csgo", 1212)
            storage.get_room_members("csgo")

    def test_list(self):
        storage = MemoryStorage()
        storage.create(True, "csgo", 1212)
        list = storage.list()
        self.assertEqual(list, ["csgo"])
