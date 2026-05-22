class TankBot:
    def __init__(self, name="Aggressor", color="orange", team="alpha"):
        self.name = name
        self.color = color
        self.team = team
        self._ammo = 10
        self._fuel = 100
        self._hp = 100
        self._mode = "attack"

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

        enemy_in_sight = any(
            (e["position"][0] == px or e["position"][1] == py)
            for e in enemies
        )
        flag_in_sight = any(
            (f["position"][0] == px or f["position"][1] == py)
            for f in enemy_flags
        )

        if enemy_in_sight and ammo > 0:
            for enemy in enemies:
                ex, ey = enemy["position"]
                if ex == px and self._clear(px, py, ex, ey, terrain):
                    self._ammo -= 1
                    return {"action": "SHOOT", "direction": "DOWN" if ey > py else "UP"}
                if ey == py and self._clear(px, py, ex, ey, terrain):
                    self._ammo -= 1
                    return {"action": "SHOOT", "direction": "RIGHT" if ex > px else "LEFT"}

        if flag_in_sight and ammo > 0:
            for flag in enemy_flags:
                fx, fy = flag["position"]
                if fx == px and self._clear(px, py, fx, fy, terrain):
                    self._ammo -= 1
                    return {"action": "SHOOT", "direction": "DOWN" if fy > py else "UP"}
                if fy == py and self._clear(px, py, fx, fy, terrain):
                    self._ammo -= 1
                    return {"action": "SHOOT", "direction": "RIGHT" if fx > px else "LEFT"}

        if fuel < 30 or ammo < 2 or hp < 30:
            target = self._find_nearest(px, py, supplies, terrain, w, h)
            if target:
                dir = self._step(px, py, target["position"][0], target["position"][1], terrain, w, h)
                if dir:
                    return {"action": "MOVE", "direction": dir}

        if enemy_flags:
            fx, fy = enemy_flags[0]["position"]
            d = self._bfs_dist(px, py, fx, fy, terrain, w, h)
            if d >= 0 and (fuel >= d or fuel > 50):
                dir = self._step(px, py, fx, fy, terrain, w, h)
                if dir:
                    return {"action": "MOVE", "direction": dir}

        if fuel < 60:
            target = self._find_nearest(px, py, [s for s in supplies if s["type"] == "fuel"], terrain, w, h)
            if not target:
                target = self._find_nearest(px, py, supplies, terrain, w, h)
            if target:
                dir = self._step(px, py, target["position"][0], target["position"][1], terrain, w, h)
                if dir:
                    return {"action": "MOVE", "direction": dir}

        for d in ["RIGHT", "DOWN", "LEFT", "UP"]:
            dx, dy = {"RIGHT": (1, 0), "LEFT": (-1, 0), "UP": (0, -1), "DOWN": (0, 1)}[d]
            nx, ny = px + dx, py + dy
            if 0 <= nx < w and 0 <= ny < h and terrain[ny][nx] in (0, 3, 4):
                return {"action": "MOVE", "direction": d}

        return {"action": "WAIT", "direction": "UP"}

    def _clear(self, px, py, tx, ty, terrain):
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
        from collections import deque
        q = deque([(sx, sy, 0)])
        visited = {(sx, sy)}
        while q:
            x, y, d = q.popleft()
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = x + dx, y + dy
                if nx == ex and ny == ey:
                    return d + 1
                if 0 <= nx < w and 0 <= ny < h and terrain[ny][nx] in (0, 3, 4) and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    q.append((nx, ny, d + 1))
        return -1

    def _find_nearest(self, px, py, items, terrain, w, h):
        from collections import deque
        q = deque([(px, py, 0)])
        visited = {(px, py)}
        item_map = {(it["position"][0], it["position"][1]): it for it in items}
        while q:
            x, y, _ = q.popleft()
            if (x, y) in item_map:
                return item_map[(x, y)]
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and terrain[ny][nx] in (0, 3, 4) and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    q.append((nx, ny, 0))
        return None

    def _step(self, px, py, tx, ty, terrain, w, h):
        from collections import deque
        q = deque([(px, py, [])])
        visited = {(px, py)}
        while q:
            x, y, path = q.popleft()
            for dname, dx, dy in [("RIGHT", 1, 0), ("LEFT", -1, 0), ("DOWN", 0, 1), ("UP", 0, -1)]:
                nx, ny = x + dx, y + dy
                if nx == tx and ny == ty:
                    return (path + [dname])[0]
                if 0 <= nx < w and 0 <= ny < h and terrain[ny][nx] in (0, 3, 4) and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    q.append((nx, ny, path + [dname]))
        return None
