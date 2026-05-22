# Tank Maze Battle 🏰

A competitive programming game platform where players write **Python code to control tanks** in a maze. Inspired by the [mouseBot](https://github.com/anomalyco/mouseBot) project.

Battle against AI or other players — navigate mazes, cross rivers, hide in forests, destroy brick walls, collect supplies, and blow up the enemy's flag to win!

---

## How to Run

```bash
pip install -r backend/requirements.txt
uvicorn backend.app:app --host 0.0.0.0 --port 8080
```

Or use the provided script:

```bash
./run.sh
```

Open `http://localhost:8080` in your browser.

---

## Game Rules

- **Two teams**: Alpha (🔴) and Beta (🔵)
- **Win conditions** (first to achieve either):
  1. Destroy the enemy's **flag** (flag HP → 0)
  2. Destroy all enemy **tanks** (all enemy tanks → 0 HP)
- Each team has **one flag** with 100 HP, placed near their starting area
- Bullets deal **25 damage** per hit to tanks and flags
- Brick walls are destroyed by a single bullet hit (costs 1 ammo)

---

## Terrain Types

| Type | Visual | Effect |
|------|--------|--------|
| **PATH** (0) | Sand/brown | Normal movement |
| **WALL** (1) | Dark gray | Impassable, blocks bullets |
| **RIVER** (2) | Blue | Impassable to tanks, bullets pass over |
| **FOREST** (3) | Dark green | Tanks inside are hidden from enemies (except adjacent tiles) |
| **BRICK** (4) | Red/brown | Destructible with 1 bullet, becomes PATH |

---

## Tank Resources

| Resource | Start | Max | Supply pickup |
|----------|-------|-----|---------------|
| **HP** | 100 | 100 | +30 HP |
| **Ammo** | 10 | 30 | +5 rounds |
| **Fuel** | 100 | 200 | +80 fuel |

- Each **MOVE** costs 1 fuel
- Each **SHOOT** costs 1 ammo
- Supplies respawn 30 ticks after collection

---

## TankBot API

Every player uploads a `.py` file containing a `TankBot` class:

```python
class TankBot:
    def __init__(self, name="IronTank", color="gray", team="alpha"):
        self.name = name
        self.color = color
        self.team = team
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
        # Your strategy here
        return {"action": "MOVE", "direction": "RIGHT"}
```

### `next_action(state)` → `{action, direction}`

**Actions:**
- `"MOVE"` — move 1 cell in `direction` (costs 1 fuel)
- `"SHOOT"` — fire a bullet in `direction` (costs 1 ammo)
- `"WAIT"` — do nothing

**Directions:** `"UP"`, `"DOWN"`, `"LEFT"`, `"RIGHT"`

### State dictionary

```python
{
    "position": [x, y],           # Current coordinates
    "map_size": [width, height],  # Grid dimensions
    "terrain": [[...]],           # 2D grid of terrain values (0-4)
    "tanks": [...],               # Visible enemy/allied tanks
    "enemies": [...],             # Tanks on other teams
    "allies": [...],              # Tanks on your team (not including self)
    "supplies": [...],            # Visible supply depots (type, position)
    "flags": [...],               # All flags (team, position, hp, alive)
    "enemy_flags": [...],         # Enemy flags only
    "bullets": [...],             # Active bullets (x, y, dx, dy, team)
    "ammo": int,                  # Your current ammo
    "fuel": int,                  # Your current fuel
    "hp": int,                    # Your current HP
    "tick": int,                  # Current game tick
    "max_steps": int,             # Max ticks before draw
    "team": str,                  # "alpha" or "beta"
}
```

---

## Project Structure

```
tankMaze/
├── run.sh                        # Start script
├── sample_bot.py                 # Example tank bot
├── demo_bot.py                   # Advanced bot (BFS pathfinding)
├── .gitignore
├── backend/
│   ├── app.py                    # FastAPI server, all API routes
│   ├── game.py                   # Game engine core
│   ├── map_generator.py          # Map generation (maze, rivers, forests, bricks)
│   ├── bot_runner.py             # Dynamic TankBot loader
│   ├── ai_bot.py                 # Computer AI (BFS pathfinding, supply management)
│   ├── room_manager.py           # Room & player management
│   └── requirements.txt
├── frontend/
│   └── index.html                # Vue 3 + Canvas UI
└── uploads/                      # Uploaded bot files (gitignored)
```

---

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/room/create` | Create a new room |
| POST | `/api/room/join` | Join an existing room |
| GET | `/api/room/{id}` | Room info (players, has_maze, game_running) |
| POST | `/api/room/{id}/map/generate` | Generate a maze map |
| POST | `/api/room/{id}/bot/upload` | Upload a TankBot `.py` file |
| GET | `/api/room/{id}/bots` | List registered bots |
| POST | `/api/room/{id}/game/start` | Start the game |
| GET | `/api/room/{id}/game/state` | Get full game state |
| POST | `/api/room/{id}/game/step` | Advance game by N ticks |

---

## How to Play

1. **Create or join a room**
2. **Generate a map** — maze with rivers, forests, and brick walls
3. **Upload your bot** — a `.py` file with a `TankBot` class
4. **Add a computer opponent** (optional) — AI with BFS pathfinding
5. **Start the game** — watch the battle unfold on the canvas
6. **Refine your strategy** — tweak your bot's `next_action()` and try again

---

## Sample Strategies

- **Aggressive**: Hunt enemies and shoot on sight
- **Resourceful**: Prioritize supply depots, then push the flag
- **Stealthy**: Use forests for cover, ambush passing enemies
- **Sapper**: Clear brick walls to open new paths toward the enemy flag

See `sample_bot.py` and `demo_bot.py` for working examples.
