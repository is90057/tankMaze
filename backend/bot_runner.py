import importlib.util
import sys
import os

VALID_ACTIONS = {"MOVE", "SHOOT", "WAIT"}
VALID_DIRECTIONS = {"UP", "DOWN", "LEFT", "RIGHT"}


def load_bot_from_file(filepath):
    module_name = os.path.splitext(os.path.basename(filepath))[0]
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)

    cls = None
    for name in dir(mod):
        obj = getattr(mod, name)
        if isinstance(obj, type) and name == "TankBot":
            cls = obj
            break
    if cls is None:
        for name in dir(mod):
            obj = getattr(mod, name)
            if isinstance(obj, type) and issubclass(obj, object) and "TankBot" in name:
                cls = obj
                break
    if cls is None:
        raise ValueError("No TankBot class found in the uploaded file")

    instance = cls()
    return instance, cls


def get_bot_action(instance, state):
    result = instance.next_action(state)
    if result is None:
        return {"action": "WAIT", "direction": "UP"}
    action = result.get("action", "WAIT")
    direction = result.get("direction", "UP")
    if action not in VALID_ACTIONS:
        action = "WAIT"
    if direction not in VALID_DIRECTIONS:
        direction = "UP"
    return {"action": action, "direction": direction}
