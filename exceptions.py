class BotError(Exception):
    def __init__(self, message):
        self.message = message


class CommandParseError(BotError):

    pass


class RoomDoesNotExist(BotError):
    pass


class NoCreator(BotError):
    pass


class RoomAlreadyExists(BotError):
    pass


class NotInRoom(BotError):
    pass
