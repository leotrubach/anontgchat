import unittest
import os
import exceptions
from storage.json_storage import JsonStorage

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
    storage_class = JsonStorage

    def remove_all_json_files(self):
        list_of_jsons = [
            "room_members.json",
            "room_visibility.json",
            "creators.json",
            "name.json",
            "user_room.json",
        ]

        for item in list_of_jsons:
            path = os.path.join(
                "C:\\", "Users", "Гала", "PycharmProjects", "demo-tg-bot", "jsons", item
            )
            if os.path.exists(path):
                os.remove(path)
            else:
                continue

    def test_kick(self):
        self.remove_all_json_files()

        storage = self.storage_class()
        storage.create(True, "csgo", 1212)
        storage.join("csgo", 1212)
        user_1 = storage.join("csgo", 1111)
        storage.kick_user(1212, user_1)
        self.assertEqual(storage.get_room_members("csgo"), {1212})
        self.remove_all_json_files()

    def test_join_exist_room(self):
        self.remove_all_json_files()

        storage = self.storage_class()
        storage.create(True, "csgo", 1212)
        storage.join("csgo", 1212)
        self.assertEqual(storage.get_room_members("csgo"), {1212})
        self.assertEqual(storage.user_room_by_id(1212), "csgo")
        self.remove_all_json_files()

    def test_join_no_exist_room(self):
        self.remove_all_json_files()

        storage = self.storage_class()
        storage.create(True, "csgo", 1212)
        with self.assertRaises(exceptions.RoomDoesNotExist):
            storage.join("csgo2", 1212)
        self.remove_all_json_files()

    def test_join_in_room(self):
        self.remove_all_json_files()

        storage = self.storage_class()
        storage.create(True, "csgo2", 1212)
        storage.create(True, "csgo", 1212)
        storage.join("csgo", 1212)

        self.assertEqual(storage.get_room_members("csgo"), {1212})
        self.assertNotIn(1212, storage.get_room_members("csgo2"))
        self.assertEqual(storage.user_room_by_id(1212), "csgo")
        self.remove_all_json_files()

    def test_join_other_room(self):
        self.remove_all_json_files()

        storage = self.storage_class()
        storage.create(True, "csgo", 1212)
        storage.join("csgo", 1212)
        storage.create(True, "csgo2", 1212)
        storage.join("csgo2", 1212)
        self.assertEqual(storage.get_room_members("csgo2"), {1212})
        self.assertNotIn(1212, storage.get_room_members("csgo"))
        self.remove_all_json_files()

    def test_part(self):
        self.remove_all_json_files()

        storage = self.storage_class()
        storage.create(True, "csgo", 1212)
        storage.join("csgo", 1212)
        storage.part(1212)
        self.assertEqual(storage.get_room_members("csgo"), set())
        self.assertNotIn(1212, storage.get_room_members("csgo"))
        self.remove_all_json_files()

    def test_part_no_in_room(self):
        self.remove_all_json_files()

        storage = self.storage_class()
        with self.assertRaises(exceptions.NotInRoom):
            storage.part(1212)
        self.remove_all_json_files()

    def test_create_have_already(self):
        self.remove_all_json_files()

        storage = self.storage_class()
        storage.create(True, "csgo", 1212)
        with self.assertRaises(exceptions.RoomAlreadyExists):
            storage.create(True, "csgo", 1212)
        self.remove_all_json_files()

    def test_create(self):
        self.remove_all_json_files()

        storage = self.storage_class()
        storage.create(True, "csgo", 1212)
        self.assertEqual(storage.get_room_members("csgo"), set())
        self.assertEqual(storage.get_user_create("csgo"), 1212)
        self.remove_all_json_files()

    def test_create_public(self):
        self.remove_all_json_files()

        storage = self.storage_class()
        is_public = storage.create(True, "csgo", 1212)
        self.assertTrue(is_public)
        self.remove_all_json_files()

    def test_create_private(self):
        self.remove_all_json_files()

        storage = self.storage_class()
        is_public = storage.create(False, "csgo", 1212)
        self.assertFalse(is_public)
        self.remove_all_json_files()

    def test_delete_have_room(self):
        self.remove_all_json_files()

        storage = self.storage_class()
        storage.create(True, "csgo", 1212)
        storage.delete_room("csgo", 1212)
        with self.assertRaises(exceptions.RoomDoesNotExist):
            storage.get_room_members("csgo")
        self.remove_all_json_files()

    def test_delete_do_not_have_room(self):
        self.remove_all_json_files()

        storage = self.storage_class()
        with self.assertRaises(exceptions.RoomDoesNotExist):
            storage.delete_room("csgo", 1212)
        self.remove_all_json_files()

    def test_list(self):
        self.remove_all_json_files()

        storage = self.storage_class()
        storage.create(True, "csgo", 1212)
        list = storage.list()
        self.assertEqual(list, ["csgo"])
        self.remove_all_json_files()
