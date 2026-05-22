class TankBot:
    def __init__(self, name="IronTank", color="gray", team="alpha"):
        self.name = "James"
        self.color = "red"
        self.team = "alpha"
        self._ammo = 10
        self._fuel = 100
        self._hp = 100

    @property
    def ammo(self): return self._ammo
    @property
    def fuel(self): return self._fuel
    @property
    def hp(self): return self._hp

    def next_action(self, state):
        px, py = state["position"]
        enemies = state["enemies"]
        supplies = state["supplies"]
        enemy_flags = state["enemy_flags"]
        terrain = state["terrain"]
        w, h = state["map_size"]
        ammo = state["ammo"]
        fuel = state["fuel"]
        hp = state["hp"]

        if ammo > 0:
            for enemy in enemies:
                ex, ey = enemy["position"]
                if ex == px:
                    dir = "DOWN" if ey > py else "UP"
                    if self._clear_shot(px, py, ex, ey, terrain):
                        self._ammo -= 1
                        return {"action": "SHOOT", "direction": dir}
                if ey == py:
                    dir = "RIGHT" if ex > px else "LEFT"
                    if self._clear_shot(px, py, ex, ey, terrain):
                        self._ammo -= 1
                        return {"action": "SHOOT", "direction": dir}
            for flag in enemy_flags:
                fx, fy = flag["position"]
                if fx == px:
                    dir = "DOWN" if fy > py else "UP"
                    if self._clear_shot(px, py, fx, fy, terrain):
                        self._ammo -= 1
                        return {"action": "SHOOT", "direction": dir}
                if fy == py:
                    dir = "RIGHT" if fx > px else "LEFT"
                    if self._clear_shot(px, py, fx, fy, terrain):
                        self._ammo -= 1
                        return {"action": "SHOOT", "direction": dir}

        if fuel < 20 or hp < 30:
            target = self._nearest(px, py, supplies, terrain, w, h)
            if target:
                dir = self._step_toward(px, py, target["position"][0], target["position"][1], terrain, w, h)
                if dir:
                    self._fuel -= 1
                    return {"action": "MOVE", "direction": dir}

        if enemy_flags:
            fx, fy = enemy_flags[0]["position"]
            dist = self._bfs_dist(px, py, fx, fy, terrain, w, h)
            if dist >= 0 and (fuel >= dist or fuel < 10):
                dir = self._step_toward(px, py, fx, fy, terrain, w, h)
                if dir:
                    self._fuel -= 1
                    return {"action": "MOVE", "direction": dir}

        if fuel < 60:
            target = self._nearest(px, py, [s for s in supplies if s["type"] == "fuel"], terrain, w, h)
            if not target:
                target = self._nearest(px, py, supplies, terrain, w, h)
            if target:
                dir = self._step_toward(px, py, target["position"][0], target["position"][1], terrain, w, h)
                if dir:
                    self._fuel -= 1
                    return {"action": "MOVE", "direction": dir}

        if ammo < 3:
            target = self._nearest(px, py, [s for s in supplies if s["type"] == "ammo"], terrain, w, h)
            if target:
                dir = self._step_toward(px, py, target["position"][0], target["position"][1], terrain, w, h)
                if dir:
                    self._fuel -= 1
                    return {"action": "MOVE", "direction": dir}

        for d in ["RIGHT", "DOWN", "LEFT", "UP"]:
            dx, dy = {"RIGHT": (1, 0), "LEFT": (-1, 0), "UP": (0, -1), "DOWN": (0, 1)}[d]
            nx, ny = px + dx, py + dy
            if 0 <= nx < w and 0 <= ny < h and terrain[ny][nx] in (0, 3, 4):
                self._fuel -= 1
                return {"action": "MOVE", "direction": d}

        return {"action": "WAIT", "direction": "UP"}

    def _clear_shot(self, px, py, tx, ty, terrain):
        if px == tx:
            step = 1 if ty > py else -1
            y = py + step
            while y != ty:
                if terrain[y][px] in (1, 4):
                    return False
                y += step
            return True
        if py == ty:
            step = 1 if tx > px else -1
            x = px + step
            while x != tx:
                if terrain[py][x] in (1, 4):
                    return False
                x += step
            return True
        return False

    def _bfs_dist(self, sx, sy, ex, ey, terrain, w, h):
        if sx == ex and sy == ey:
            return 0
        q = __import__("collections").deque()
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

    def _nearest(self, px, py, items, terrain, w, h):
        q = __import__("collections").deque()
        q.append((px, py, 0))
        visited = {(px, py)}
        item_set = {(it["position"][0], it["position"][1]): it for it in items}
        while q:
            x, y, d = q.popleft()
            if (x, y) in item_set:
                return item_set[(x, y)]
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < w and 0 <= ny < h and terrain[ny][nx] in (0, 3, 4)
                        and (nx, ny) not in visited):
                    visited.add((nx, ny))
                    q.append((nx, ny, d + 1))
        return None

    def _step_toward(self, px, py, tx, ty, terrain, w, h):
        q = __import__("collections").deque()
        q.append((px, py, []))
        visited = {(px, py)}
        while q:
            x, y, path = q.popleft()
            dirs = [("RIGHT", 1, 0), ("LEFT", -1, 0), ("DOWN", 0, 1), ("UP", 0, -1)]
            for dname, dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if nx == tx and ny == ty:
                    return (path + [dname])[0]
                if (0 <= nx < w and 0 <= ny < h and terrain[ny][nx] in (0, 3, 4)
                        and (nx, ny) not in visited):
                    visited.add((nx, ny))
                    q.append((nx, ny, path + [dname]))
        return None
