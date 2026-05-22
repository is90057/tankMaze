import uuid
import string
import random
import time
from .game import GameManager
from .map_generator import generate_map
from .bot_runner import load_bot_from_file
from .ai_bot import AITankBot

COLORS = ["orange", "red", "purple", "cyan", "lime", "pink", "yellow", "teal"]


def _random_room_id():
    return "".join(random.choices(string.ascii_uppercase, k=4))


class Room:
    def __init__(self, room_id):
        self.room_id = room_id
        self.game = None
        self.players = {}
        self.created_at = time.time()
        self.has_maze = False
        self.rows = 15
        self.cols = 15
        self.loop_factor = 0.15
        self.include_computer = False
        self.color_idx = 0

    def next_color(self):
        c = COLORS[self.color_idx % len(COLORS)]
        self.color_idx += 1
        return c


class RoomManager:
    def __init__(self):
        self.rooms = {}

    def create_room(self):
        while True:
            rid = _random_room_id()
            if rid not in self.rooms:
                break
        room = Room(rid)
        token = str(uuid.uuid4())[:8]
        self.rooms[rid] = room
        return rid, token

    def get_room(self, room_id):
        return self.rooms.get(room_id)

    def remove_room(self, room_id):
        self.rooms.pop(room_id, None)

    def cleanup_old(self, max_age=3600):
        now = time.time()
        to_remove = [rid for rid, r in self.rooms.items() if now - r.created_at > max_age]
        for rid in to_remove:
            self.remove_room(rid)
