from app import mysql as __mysql


class Room:
    table = "rooms"
    name_col = "name"
    slots_col = "slots"

    def __init__(self, name, slots):
        self.name = name
        self.slots = slots

    def insert(self):
        cur = __mysql.connection.cursor()

        cur.close()


def create_room(name, slots):
    r = Room(name, slots)
    r.insert()
