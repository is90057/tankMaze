import random
from .map_generator import PATH, WALL, RIVER, FOREST, BRICK, generate_map
from .bot_runner import get_bot_action, load_bot_from_file

MOVE_DELTA = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}

SHOOT_DAMAGE = 25
BULLET_RANGE = 15
MAX_STEPS = 1000

SUPPLY_VALUES = {"ammo": 5, "fuel": 80, "hp": 30}
SUPPLY_RESPAWN = 30
MAX_AMMO = 30
MAX_FUEL = 200
MAX_HP = 100


class GameManager:
    def __init__(self, map_data):
        self.map = map_data
        self.grid = [row[:] for row in map_data["grid"]]
        self.width = map_data["width"]
        self.height = map_data["height"]

        self.tanks = {}
        self.bullets = []
        self.flags = {f["team"]: dict(f) for f in map_data["flags"]}
        self.supplies = [dict(s) | {"collected_tick": -1} for s in map_data["supplies"]]

        self.game_running = False
        self.game_finished = False
        self.winner = None
        self.tick = 0
        self.bot_instances = {}
        self._stuck_counters = {}

    def register_tank(self, bot_id, name, color, team, bot_instance):
        self.tanks[bot_id] = {
            "id": bot_id,
            "name": name,
            "color": color,
            "team": team,
            "position": None,
            "hp": 100,
            "ammo": 10,
            "fuel": 100,
            "alive": True,
            "hidden": False,
        }
        self.bot_instances[bot_id] = bot_instance

    def start_game(self):
        for bot_id, tank in self.tanks.items():
            tank["position"] = self.map["start_positions"][tank["team"]]
            tank["hp"] = 100
            tank["ammo"] = 10
            tank["fuel"] = 100
            tank["alive"] = True

        for flag in self.flags.values():
            flag["hp"] = 100

        for s in self.supplies:
            s["collected_tick"] = -1

        self.bullets = []
        self.game_running = True
        self.game_finished = False
        self.winner = None
        self.tick = 0

    def step(self):
        if not self.game_running or self.game_finished:
            return

        self.tick += 1

        actions = {}
        for bot_id, tank in list(self.tanks.items()):
            if not tank["alive"]:
                continue
            state = self._build_state(bot_id)
            try:
                bot = self.bot_instances[bot_id]
                action = get_bot_action(bot, state)
                if action is None:
                    action = {"action": "WAIT", "direction": "UP"}
                actions[bot_id] = action
            except Exception:
                actions[bot_id] = {"action": "WAIT", "direction": "UP"}

        new_positions = {}
        for bot_id, action in actions.items():
            if action.get("action") == "MOVE":
                tank = self.tanks[bot_id]
                if tank["fuel"] <= 0:
                    continue
                direction = action.get("direction", "UP")
                dx, dy = MOVE_DELTA.get(direction, (0, 0))
                nx, ny = tank["position"][0] + dx, tank["position"][1] + dy
                if self._is_valid_move(nx, ny, bot_id):
                    new_positions[bot_id] = (nx, ny)
                    tank["fuel"] = max(0, tank["fuel"] - 1)
                    self._stuck_counters[bot_id] = 0
                else:
                    cnt = self._stuck_counters.get(bot_id, 0) + 1
                    self._stuck_counters[bot_id] = cnt
                    if cnt >= 3:
                        fallback = self._find_any_valid_move(tank["position"], bot_id)
                        if fallback:
                            new_positions[bot_id] = fallback
                            tank["fuel"] = max(0, tank["fuel"] - 1)
                            self._stuck_counters[bot_id] = 0

        for bot_id, action in actions.items():
            if action.get("action") == "SHOOT":
                tank = self.tanks[bot_id]
                if tank["ammo"] <= 0:
                    continue
                direction = action.get("direction", "UP")
                dx, dy = MOVE_DELTA.get(direction, (0, 0))
                bx, by = tank["position"][0] + dx, tank["position"][1] + dy
                if 0 <= bx < self.width and 0 <= by < self.height:
                    self.bullets.append({
                        "x": bx, "y": by,
                        "dx": dx, "dy": dy,
                        "team": tank["team"],
                        "bot_id": bot_id,
                        "range_used": 0,
                    })
                    tank["ammo"] -= 1

        for bot_id, pos in new_positions.items():
            self.tanks[bot_id]["position"] = pos

        surviving = []
        for b in self.bullets:
            b["x"] += b["dx"]
            b["y"] += b["dy"]
            b["range_used"] += 1

            if b["range_used"] > BULLET_RANGE:
                continue
            if not (0 <= b["x"] < self.width and 0 <= b["y"] < self.height):
                continue

            cell = self.grid[b["y"]][b["x"]]

            if cell == WALL:
                continue

            if cell == BRICK:
                self.grid[b["y"]][b["x"]] = PATH
                continue

            hit_tank = None
            for tid, t in self.tanks.items():
                if (t["alive"]
                    and t["position"][0] == b["x"]
                    and t["position"][1] == b["y"]
                    and t["team"] != b["team"]):
                    hit_tank = tid
                    break
            if hit_tank:
                self.tanks[hit_tank]["hp"] -= SHOOT_DAMAGE
                if self.tanks[hit_tank]["hp"] <= 0:
                    self.tanks[hit_tank]["alive"] = False
                continue

            hit_flag = None
            for team, flag in self.flags.items():
                if (flag["position"][0] == b["x"]
                    and flag["position"][1] == b["y"]
                    and team != b["team"]):
                    hit_flag = team
                    break
            if hit_flag:
                self.flags[hit_flag]["hp"] -= SHOOT_DAMAGE
                continue

            removed = False
            for other in self.bullets:
                if (other is not b
                    and other["x"] == b["x"]
                    and other["y"] == b["y"]
                    and other["team"] != b["team"]):
                    other.pop("_rm", None)
                    b["_rm"] = True
                    removed = True
                    break
            if removed:
                continue

            surviving.append(b)

        self.bullets = [b for b in surviving if not b.pop("_rm", False)]

        for bot_id, tank in self.tanks.items():
            if not tank["alive"]:
                continue
            for supply in self.supplies:
                if (supply["collected_tick"] < 0
                    and supply["position"][0] == tank["position"][0]
                    and supply["position"][1] == tank["position"][1]):
                    self._collect_supply(tank, supply)

        for supply in self.supplies:
            if supply["collected_tick"] >= 0 and self.tick - supply["collected_tick"] >= SUPPLY_RESPAWN:
                supply["collected_tick"] = -1

        for bot_id, tank in self.tanks.items():
            if tank["alive"]:
                tank["hidden"] = (self.grid[tank["position"][1]][tank["position"][0]] == FOREST)

        alive_flags = [team for team, flag in self.flags.items() if flag["hp"] > 0]
        if len(alive_flags) < 2:
            self.game_running = False
            self.game_finished = True
            self.winner = alive_flags[0] if len(alive_flags) == 1 else "draw"

        alive_teams = set()
        for tank in self.tanks.values():
            if tank["alive"]:
                alive_teams.add(tank["team"])
        if len(alive_teams) < 2 and len(self.tanks) >= 2:
            self.game_running = False
            self.game_finished = True
            remaining = list(alive_teams)
            self.winner = remaining[0] if remaining else "draw"

        if self.tick >= MAX_STEPS:
            self.game_running = False
            self.game_finished = True
            self.winner = "draw"

    def _build_state(self, bot_id):
        tank = self.tanks[bot_id]

        visible_tanks = []
        for bid, t in self.tanks.items():
            if bid == bot_id or not t["alive"]:
                continue
            if t.get("hidden"):
                dist = abs(t["position"][0] - tank["position"][0]) + abs(t["position"][1] - tank["position"][1])
                if dist <= 1:
                    visible_tanks.append({
                        "id": bid, "position": list(t["position"]),
                        "team": t["team"], "hp": t["hp"],
                        "name": t["name"], "color": t["color"],
                        "hidden": True,
                    })
            else:
                visible_tanks.append({
                    "id": bid, "position": list(t["position"]),
                    "team": t["team"], "hp": t["hp"],
                    "name": t["name"], "color": t["color"],
                    "hidden": False,
                })

        enemies = [t for t in visible_tanks if t["team"] != tank["team"]]
        allies = [t for t in visible_tanks if t["team"] == tank["team"]]

        visible_flags = []
        for team, flag in self.flags.items():
            visible_flags.append({
                "team": team, "position": list(flag["position"]),
                "hp": flag["hp"], "alive": flag["hp"] > 0,
            })
        enemy_flags = [f for f in visible_flags if f["team"] != tank["team"]]

        visible_supplies = []
        for s in self.supplies:
            if s["collected_tick"] < 0:
                visible_supplies.append({
                    "type": s["type"], "position": list(s["position"]),
                })

        bullets_info = [
            {"x": b["x"], "y": b["y"], "dx": b["dx"], "dy": b["dy"], "team": b["team"]}
            for b in self.bullets
        ]

        return {
            "position": list(tank["position"]),
            "map_size": [self.width, self.height],
            "terrain": self.grid,
            "tanks": visible_tanks,
            "enemies": enemies,
            "allies": allies,
            "supplies": visible_supplies,
            "flags": visible_flags,
            "enemy_flags": enemy_flags,
            "bullets": bullets_info,
            "ammo": tank["ammo"],
            "fuel": tank["fuel"],
            "hp": tank["hp"],
            "tick": self.tick,
            "max_steps": MAX_STEPS,
            "team": tank["team"],
        }

    def _is_valid_move(self, x, y, bot_id):
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        cell = self.grid[y][x]
        if cell in (WALL, RIVER):
            return False
        for bid, tank in self.tanks.items():
            if bid != bot_id and tank["alive"] and tank["position"] == (x, y):
                return False
        return True

    def _find_any_valid_move(self, pos, bot_id):
        for dx, dy, d in [(0, -1, "UP"), (0, 1, "DOWN"), (-1, 0, "LEFT"), (1, 0, "RIGHT")]:
            nx, ny = pos[0] + dx, pos[1] + dy
            if self._is_valid_move(nx, ny, bot_id):
                return (nx, ny)
        return None

    def _collect_supply(self, tank, supply):
        if supply["type"] == "ammo":
            tank["ammo"] = min(MAX_AMMO, tank["ammo"] + SUPPLY_VALUES["ammo"])
        elif supply["type"] == "fuel":
            tank["fuel"] = min(MAX_FUEL, tank["fuel"] + SUPPLY_VALUES["fuel"])
        elif supply["type"] == "hp":
            tank["hp"] = min(MAX_HP, tank["hp"] + SUPPLY_VALUES["hp"])
        supply["collected_tick"] = self.tick

    def get_state(self):
        tanks_info = []
        for bid, t in self.tanks.items():
            tanks_info.append({
                "id": bid,
                "name": t["name"],
                "color": t["color"],
                "team": t["team"],
                "position": list(t["position"]) if t["position"] else None,
                "hp": t["hp"],
                "ammo": t["ammo"],
                "fuel": t["fuel"],
                "alive": t["alive"],
                "hidden": t.get("hidden", False),
            })

        flags_info = []
        for team, f in self.flags.items():
            flags_info.append({
                "team": team,
                "position": list(f["position"]),
                "hp": f["hp"],
                "alive": f["hp"] > 0,
            })

        supplies_info = []
        for s in self.supplies:
            supplies_info.append({
                "type": s["type"],
                "position": list(s["position"]),
                "active": s["collected_tick"] < 0,
            })

        bullets_info = [
            {"x": b["x"], "y": b["y"], "team": b["team"]}
            for b in self.bullets
        ]

        return {
            "map": {
                "grid": self.grid,
                "width": self.width,
                "height": self.height,
                "start_positions": self.map["start_positions"],
            },
            "tanks": tanks_info,
            "flags": flags_info,
            "supplies": supplies_info,
            "bullets": bullets_info,
            "tick": self.tick,
            "game_running": self.game_running,
            "game_finished": self.game_finished,
            "winner": self.winner,
        }
