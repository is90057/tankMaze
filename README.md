# Tank Maze Battle / 坦克迷宮大戰 🏰

**English** · [**中文**](#chinese)

---

<a name="english"></a>

## Overview

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

---

<a name="chinese"></a>

# 坦克迷宮大戰 🏰

## 概述

這是一個程式競技型遊戲平台。玩家不是直接操作坦克，而是**自己撰寫 Python 程式來控制坦克車**，在迷宮中探索、閃避敵人、管理資源，並嘗試摧毀敵方軍旗或殲滅所有敵方坦克。

可以選擇跟**電腦 AI** 比賽，也可以跟**其他玩家**對戰。

---

## 如何啟動

```bash
pip install -r backend/requirements.txt
uvicorn backend.app:app --host 0.0.0.0 --port 8080
```

或使用腳本：

```bash
./run.sh
```

開啟瀏覽器前往 `http://localhost:8080`。

---

## 遊戲規則

- **兩隊對戰**：Alpha (🔴) 和 Beta (🔵)
- **勝利條件**（先達成任一者獲勝）：
  1. 摧毀敵方**軍旗**（軍旗 HP 歸零）
  2. 殲滅所有敵方**坦克**（所有敵方坦克 HP 歸零）
- 每隊有 **1 面軍旗**（100 HP），位於起始點附近
- 子彈每次造成 **25 點傷害**（對坦克或軍旗）
- 磚牆被子彈擊中即摧毀（消耗 1 發彈藥）

---

## 地形類型

| 類型 | 視覺 | 效果 |
|------|------|------|
| **道路** (0) | 沙色 | 可通行 |
| **牆壁** (1) | 深灰 | 不可通行，阻擋子彈 |
| **河流** (2) | 藍色 | 坦克無法通行，子彈可越過 |
| **森林** (3) | 深綠 | 坦克隱藏（敵人需相鄰才能看見） |
| **磚牆** (4) | 紅棕 | 可被子彈摧毀，變成道路 |

---

## 坦克資源

| 資源 | 初始 | 上限 | 補給量 |
|------|------|------|--------|
| **血量** | 100 | 100 | +30 HP |
| **彈藥** | 10 | 30 | +5 發 |
| **燃料** | 100 | 200 | +80 燃料 |

- 每次 **MOVE** 消耗 1 燃料
- 每次 **SHOOT** 消耗 1 彈藥
- 補給站被拾取後 30 回合重生

---

## TankBot API

每個玩家上傳一個 `.py` 檔案，裡面包含 `TankBot` 類別：

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
        # 你的策略
        return {"action": "MOVE", "direction": "RIGHT"}
```

### `next_action(state)` → `{action, direction}`

**動作：**
- `"MOVE"` — 往 `direction` 移動 1 格（消耗 1 燃料）
- `"SHOOT"` — 往 `direction` 開火（消耗 1 彈藥）
- `"WAIT"` — 不動

**方向：** `"UP"`, `"DOWN"`, `"LEFT"`, `"RIGHT"`

### state 字典

```python
{
    "position": [x, y],           # 當前座標
    "map_size": [width, height],  # 地圖大小
    "terrain": [[...]],           # 二維地形陣列 (0-4)
    "tanks": [...],               # 可見的敵方/友方坦克
    "enemies": [...],             # 敵方坦克列表
    "allies": [...],              # 友方坦克列表（不含自己）
    "supplies": [...],            # 可見補給站（type, position）
    "flags": [...],               # 所有軍旗（team, position, hp, alive）
    "enemy_flags": [...],         # 敵方軍旗
    "bullets": [...],             # 飛行中的子彈（x, y, dx, dy, team）
    "ammo": int,                  # 當前彈藥
    "fuel": int,                  # 當前燃料
    "hp": int,                    # 當前血量
    "tick": int,                  # 當前回合數
    "max_steps": int,             # 最大回合數（超過則平手）
    "team": str,                  # "alpha" 或 "beta"
}
```

---

## 遊玩流程

1. **建立或加入房間**
2. **生成地圖** — 包含迷宮、河流、森林、磚牆
3. **上傳你的坦克腳本** — 含有 `TankBot` 類別的 `.py` 檔案
4. **加入電腦對手**（可選）— 內建 BFS 尋路 AI
5. **開始遊戲** — 在 Canvas 上觀看戰鬥過程
6. **調整策略** — 修改 `next_action()` 後再戰

---

## 策略範例

- **強攻型**：見到敵人就開火
- **補給型**：優先收集補給，再推進軍旗
- **隱蔽型**：利用森林隱藏，伏擊路過的敵人
- **工兵型**：清除磚牆，開闢通往敵方軍旗的新路線

參考 `sample_bot.py` 和 `demo_bot.py` 取得完整範例。
