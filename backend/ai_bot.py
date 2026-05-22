from collections import deque

MOVE_DELTA = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}


class AITankBot:
    def __init__(self, name="AI Tank", color="red", team="beta"):
        self.name = name
        self.color = color
        self.team = team
        self._target = None
        self._path = []

    @property
    def ammo(self): return 10
    @property
    def fuel(self): return 100
    @property
    def hp(self): return 100

    def next_action(self, state):
        tx, ty = state["position"]
        terrain = state["terrain"]
        w, h = state["map_size"]
        enemies = state["enemies"]
        enemy_flags = state["enemy_flags"]
        supplies = state["supplies"]
        ammo = state["ammo"]
        fuel = state["fuel"]
        hp = state["hp"]

        if ammo > 0:
            shoot_dir = self._find_shoot_target(tx, ty, enemies, terrain)
            if shoot_dir:
                return {"action": "SHOOT", "direction": shoot_dir}
            flag_shoot_dir = self._find_shoot_flag(tx, ty, enemy_flags, terrain)
            if flag_shoot_dir:
                return {"action": "SHOOT", "direction": flag_shoot_dir}

        if hp < 30 or ammo < 3 or fuel < 40:
            need_hp = hp < 30
            need_ammo = ammo < 3
            need_fuel = fuel < 40
            best = None
            best_score = float("inf")
            for s in supplies:
                sx, sy = s["position"]
                dist = self._bfs_dist(tx, ty, sx, sy, terrain, w, h)
                if dist < 0:
                    continue
                score = dist
                if need_hp and s["type"] == "hp":
                    score -= 50
                if need_ammo and s["type"] == "ammo":
                    score -= 50
                if need_fuel and s["type"] == "fuel":
                    score -= 50
                if score < best_score:
                    best_score = score
                    best = s
            if best:
                dir = self._bfs_step(tx, ty, best["position"][0], best["position"][1], terrain, w, h)
                if dir:
                    return {"action": "MOVE", "direction": dir}

        if enemy_flags:
            fx, fy = enemy_flags[0]["position"]
            flag_dir = self._bfs_step(tx, ty, fx, fy, terrain, w, h)
            if flag_dir:
                flag_dist = self._bfs_dist(tx, ty, fx, fy, terrain, w, h)
                if fuel >= flag_dist or fuel >= 30:
                    return {"action": "MOVE", "direction": flag_dir}

        if fuel < 40:
            best_fuel = None
            best_fd = float("inf")
            for s in supplies:
                if s["type"] == "fuel":
                    fd = self._bfs_dist(tx, ty, s["position"][0], s["position"][1], terrain, w, h)
                    if 0 < fd < best_fd:
                        best_fd = fd
                        best_fuel = s
            if best_fuel:
                dir = self._bfs_step(tx, ty, best_fuel["position"][0], best_fuel["position"][1], terrain, w, h)
                if dir:
                    return {"action": "MOVE", "direction": dir}

        if enemy_flags:
            fx, fy = enemy_flags[0]["position"]
            dir = self._bfs_step(tx, ty, fx, fy, terrain, w, h)
            if dir:
                return {"action": "MOVE", "direction": dir}

        for dir_name in ["RIGHT", "DOWN", "LEFT", "UP"]:
            dx, dy = MOVE_DELTA[dir_name]
            nx, ny = tx + dx, ty + dy
            if 0 <= nx < w and 0 <= ny < h and terrain[ny][nx] in (0, 3, 4):
                return {"action": "MOVE", "direction": dir_name}

        return {"action": "WAIT", "direction": "UP"}

    def _bfs_dist(self, sx, sy, ex, ey, terrain, w, h):
        if sx == ex and sy == ey:
            return 0
        q = deque()
        q.append((sx, sy, 0))
        visited = {(sx, sy)}
        while q:
            x, y, d = q.popleft()
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = x + dx, y + dy
                if nx == ex and ny == ey:
                    return d + 1
                if (0 <= nx < w and 0 <= ny < h and terrain[ny][nx] in (0, 3, 4)
                        and (nx, ny) not in visited):
                    visited.add((nx, ny))
                    q.append((nx, ny, d + 1))
        return -1

    def _bfs_step(self, sx, sy, ex, ey, terrain, w, h):
        if sx == ex and sy == ey:
            return None
        q = deque()
        q.append((sx, sy, []))
        visited = {(sx, sy)}
        while q:
            x, y, path = q.popleft()
            for dir_name, (dx, dy) in MOVE_DELTA.items():
                nx, ny = x + dx, y + dy
                if nx == ex and ny == ey:
                    full_path = path + [dir_name]
                    return full_path[0]
                if (0 <= nx < w and 0 <= ny < h and terrain[ny][nx] in (0, 3, 4)
                        and (nx, ny) not in visited):
                    visited.add((nx, ny))
                    q.append((nx, ny, path + [dir_name]))
        return None

    def _find_shoot_target(self, tx, ty, enemies, terrain):
        for enemy in enemies:
            ex, ey = enemy["position"]
            if ex == tx:
                step = 1 if ey > ty else -1
                y = ty + step
                blocked = False
                while 0 <= y < len(terrain) and y != ey:
                    cell = terrain[y][tx]
                    if cell in (1, 4):
                        blocked = True
                        break
                    y += step
                if not blocked:
                    return "DOWN" if ey > ty else "UP"
            if ey == ty:
                step = 1 if ex > tx else -1
                x = tx + step
                blocked = False
                while 0 <= x < len(terrain[0]) and x != ex:
                    cell = terrain[ey][x]
                    if cell in (1, 4):
                        blocked = True
                        break
                    x += step
                if not blocked:
                    return "RIGHT" if ex > tx else "LEFT"
        return None

    def _find_shoot_flag(self, tx, ty, flags, terrain):
        for flag in flags:
            fx, fy = flag["position"]
            if fx == tx:
                step = 1 if fy > ty else -1
                y = ty + step
                blocked = False
                while 0 <= y < len(terrain) and y != fy:
                    cell = terrain[y][tx]
                    if cell in (1, 4):
                        blocked = True
                        break
                    y += step
                if not blocked:
                    return "DOWN" if fy > ty else "UP"
            if fy == ty:
                step = 1 if fx > tx else -1
                x = tx + step
                blocked = False
                while 0 <= x < len(terrain[0]) and x != fx:
                    cell = terrain[fy][x]
                    if cell in (1, 4):
                        blocked = True
                        break
                    x += step
                if not blocked:
                    return "RIGHT" if fx > tx else "LEFT"
        return None
