import random

PATH = 0
WALL = 1
RIVER = 2
FOREST = 3
BRICK = 4


def generate_map(rows, cols, loop_factor=0.15):
    width = 2 * cols + 1
    height = 2 * rows + 1

    grid = [[WALL for _ in range(width)] for _ in range(height)]

    _carve_maze(grid, width, height, loop_factor)
    _place_rivers(grid, width, height)
    _place_forests(grid, width, height)
    _place_bricks(grid, width, height)
    supplies = _place_supplies(grid, width, height)

    alpha_start = (1, 1)
    beta_start = (width - 2, height - 2)

    alpha_flag_pos = _find_adjacent_path(grid, (1, 1), width, height)
    beta_flag_pos = _find_adjacent_path(grid, (width - 2, height - 2), width, height)

    flags = [
        {"team": "alpha", "position": alpha_flag_pos, "hp": 100},
        {"team": "beta", "position": beta_flag_pos, "hp": 100},
    ]

    # ensure flag cells are path
    grid[alpha_flag_pos[1]][alpha_flag_pos[0]] = PATH
    grid[beta_flag_pos[1]][beta_flag_pos[0]] = PATH

    return {
        "grid": grid,
        "width": width,
        "height": height,
        "start_positions": {"alpha": alpha_start, "beta": beta_start},
        "flags": flags,
        "supplies": supplies,
    }


def _carve_maze(grid, width, height, loop_factor):
    stack = [(1, 1)]
    visited = {(1, 1)}
    grid[1][1] = PATH

    while stack:
        x, y = stack[-1]
        neighbors = []
        for dx, dy, wx, wy in [(0, -2, 0, -1), (0, 2, 0, 1), (-2, 0, -1, 0), (2, 0, 1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 < nx < width - 1 and 0 < ny < height - 1 and (nx, ny) not in visited:
                neighbors.append((nx, ny, wx, wy))
        if neighbors:
            nx, ny, wx, wy = random.choice(neighbors)
            visited.add((nx, ny))
            grid[ny][nx] = PATH
            grid[y + wy][x + wx] = PATH
            stack.append((nx, ny))
        else:
            stack.pop()

    if loop_factor > 0:
        removable = []
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                if grid[y][x] == WALL:
                    removable.append((x, y))
        random.shuffle(removable)
        for i in range(int(len(removable) * loop_factor)):
            x, y = removable[i]
            grid[y][x] = PATH


def _place_rivers(grid, width, height):
    for _ in range(random.randint(1, 2)):
        for _ in range(30):
            if random.choice([True, False]):
                y = random.randrange(2, height - 2, 2)
                x_start = random.randrange(1, width - 2)
                x_end = min(x_start + random.randint(4, 10), width - 2)
                cells = [(x, y) for x in range(x_start, x_end + 1) if grid[y][x] in (PATH, WALL)]
                if len(cells) >= 4:
                    for x, y in cells:
                        grid[y][x] = RIVER
                    break
            else:
                x = random.randrange(2, width - 2, 2)
                y_start = random.randrange(1, height - 2)
                y_end = min(y_start + random.randint(4, 10), height - 2)
                cells = [(x, y) for y in range(y_start, y_end + 1) if grid[y][x] in (PATH, WALL)]
                if len(cells) >= 4:
                    for x, y in cells:
                        grid[y][x] = RIVER
                    break


def _place_forests(grid, width, height):
    for _ in range(random.randint(3, 5)):
        for _ in range(20):
            fx = random.randrange(1, width - 1)
            fy = random.randrange(1, height - 1)
            if grid[fy][fx] == PATH:
                size = random.randint(3, 7)
                cells = [(fx, fy)]
                for _ in range(size - 1):
                    px, py = random.choice(cells)
                    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nx, ny = px + dx, py + dy
                        if 0 < nx < width - 1 and 0 < ny < height - 1 and grid[ny][nx] == PATH and (nx, ny) not in cells:
                            cells.append((nx, ny))
                            break
                for cx, cy in cells:
                    grid[cy][cx] = FOREST
                break


def _place_bricks(grid, width, height):
    for _ in range(random.randint(5, 10)):
        for _ in range(30):
            bx = random.randrange(1, width - 1)
            by = random.randrange(1, height - 1)
            if grid[by][bx] == PATH:
                grid[by][bx] = BRICK
                break


def _place_supplies(grid, width, height):
    supplies = []
    # Ensure at least 2 of each type
    types_pool = ["ammo", "ammo", "fuel", "fuel", "hp", "hp", "ammo", "fuel", "hp", "fuel"]
    for stype in types_pool:
        for _ in range(30):
            sx = random.randrange(1, width - 1)
            sy = random.randrange(1, height - 1)
            if grid[sy][sx] == PATH and not any(s["position"] == (sx, sy) for s in supplies):
                supplies.append({"type": stype, "position": (sx, sy)})
                break
    return supplies


def _find_adjacent_path(grid, pos, width, height):
    x, y = pos
    for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        nx, ny = x + dx, y + dy
        if 0 < ny < height - 1 and 0 < nx < width - 1 and grid[ny][nx] == PATH:
            return (nx, ny)
    return (x + 2, y)
