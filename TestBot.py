import unittest
from storage.memory import MemoryStorage


class SimpleUnitTest(unittest.TestCase):
    def test_kick(self):
        storage = MemoryStorage()
        storage.create(True, "csgo", 1212)
        storage.join("csgo", 1212)
        storage.join("csgo", 1111)
        user_1 = storage.name[1111]
        user_2 = storage.name[1212]
        print(user_2, user_1)
        print(storage.name1)
        print(storage.room_members)
        storage.kick_user(1212, user_1)
        self.assertEqual(storage.get_room_members("csgo"), {1212})
