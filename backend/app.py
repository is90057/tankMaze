import os
import uuid
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path

from .room_manager import RoomManager
from .game import GameManager
from .map_generator import generate_map
from .bot_runner import load_bot_from_file
from .ai_bot import AITankBot

app = FastAPI(title="Tank Maze Battle")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOM_MANAGER = RoomManager()
UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


def _get_room(room_id):
    room = ROOM_MANAGER.get_room(room_id)
    if not room:
        raise HTTPException(404, "Room not found")
    return room


def _verify_token(room, token):
    if token not in room.players:
        raise HTTPException(403, "Invalid player token")


@app.get("/")
async def index():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.post("/api/room/create")
async def create_room():
    rid, token = ROOM_MANAGER.create_room()
    room = ROOM_MANAGER.get_room(rid)
    room.players[token] = {"name": "Player", "color": room.next_color(), "bot_id": None}
    return {"room_id": rid, "player_token": token}


@app.post("/api/room/join")
async def join_room(room_id: str = Form(...), name: str = Form("Player")):
    room = _get_room(room_id)
    token = str(uuid.uuid4())[:8]
    room.players[token] = {"name": name, "color": room.next_color(), "bot_id": None}
    return {"room_id": room_id, "player_token": token}


@app.get("/api/room/{room_id}")
async def get_room_info(room_id: str):
    room = _get_room(room_id)
    players = []
    for token, p in room.players.items():
        players.append({
            "name": p["name"],
            "color": p["color"],
            "has_bot": p["bot_id"] is not None,
        })
    return {
        "room_id": room_id,
        "players": players,
        "has_maze": room.has_maze,
        "game_running": room.game is not None and room.game.game_running if room.game else False,
    }


@app.post("/api/room/{room_id}/map/generate")
async def generate_game_map(
    room_id: str,
    player_token: str = Form(...),
    rows: int = Form(15),
    cols: int = Form(15),
    loop_factor: float = Form(0.15),
):
    room = _get_room(room_id)
    _verify_token(room, player_token)

    rows = max(5, min(30, rows))
    cols = max(5, min(30, cols))
    loop_factor = max(0.0, min(0.5, loop_factor))

    map_data = generate_map(rows, cols, loop_factor)
    room.game = GameManager(map_data)
    room.has_maze = True
    room.rows = rows
    room.cols = cols
    room.loop_factor = loop_factor

    return {
        "width": map_data["width"],
        "height": map_data["height"],
        "rows": rows,
        "cols": cols,
    }


@app.post("/api/room/{room_id}/bot/upload")
async def upload_bot(
    room_id: str,
    player_token: str = Form(...),
    file: UploadFile = File(...),
    team: str = Form("alpha"),
):
    room = _get_room(room_id)
    _verify_token(room, player_token)

    if not file.filename.endswith(".py"):
        raise HTTPException(400, "Only .py files are allowed")

    safe_name = f"{player_token}_{file.filename}"
    filepath = UPLOAD_DIR / safe_name
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    instance, cls = load_bot_from_file(str(filepath))
    instance.team = team
    bot_id = f"bot_{player_token}"

    room.players[player_token]["bot_id"] = bot_id
    room.players[player_token]["name"] = instance.name

    if room.game:
        room.game.register_tank(bot_id, instance.name, instance.color, team, instance)

    return {"bot_id": bot_id, "name": instance.name, "team": team}


@app.get("/api/room/{room_id}/bots")
async def list_bots(room_id: str):
    room = _get_room(room_id)
    bots = []
    if room.game:
        for bot_id, tank in room.game.tanks.items():
            bots.append({
                "id": bot_id,
                "name": tank["name"],
                "color": tank["color"],
                "team": tank["team"],
            })
    return {"bots": bots}


@app.post("/api/room/{room_id}/game/start")
async def start_game(
    room_id: str,
    player_token: str = Form(...),
    include_computer: bool = Form(False),
):
    room = _get_room(room_id)
    _verify_token(room, player_token)

    if not room.game:
        raise HTTPException(400, "No map generated yet")

    has_alpha = any(p["bot_id"] and p["bot_id"].startswith("bot_") and room.game.tanks.get(p["bot_id"], {}).get("team") == "alpha" for p in room.players.values())
    has_beta = any(p["bot_id"] and p["bot_id"].startswith("bot_") and room.game.tanks.get(p["bot_id"], {}).get("team") == "beta" for p in room.players.values())

    if not has_alpha and not has_beta:
        raise HTTPException(400, "No bots uploaded")

    if include_computer or not has_beta:
        ai_instance = AITankBot(name="AI Tank", color="red", team="beta")
        ai_bot_id = "ai_computer"
        room.game.register_tank(ai_bot_id, ai_instance.name, ai_instance.color, "beta", ai_instance)

    room.game.start_game()
    return {"status": "started", "game_running": True}


@app.get("/api/room/{room_id}/game/state")
async def get_game_state(room_id: str):
    room = _get_room(room_id)
    if not room.game:
        raise HTTPException(400, "No game started")
    state = room.game.get_state()
    return state


@app.post("/api/room/{room_id}/game/step")
async def game_step(room_id: str, steps: int = Form(1)):
    room = _get_room(room_id)
    if not room.game:
        raise HTTPException(400, "No game started")
    for _ in range(steps):
        room.game.step()
    state = room.game.get_state()
    return state
