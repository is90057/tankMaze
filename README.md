# tankMaze
坦克迷宮大戰是一個程式競技型遊戲平台。玩家不只是操作坦克，而是要 自己撰寫程式來控制坦克車，在迷宮中探索、閃避敵人、管理資源，並嘗試最快或最聰明地到達出口。這是一場結合 演算法挑戰 + 戰略對抗 的遊戲。

# API 規範 (Python 範例)
玩家必須依照統一規範撰寫程式：

```python
class TankBot:
    def __init__(self, name="IronTank", color="gray", team="alpha"):
        self.name = name
        self.color = color
        self.team = team
        # 系統固定值 (不可修改)
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
        # 範例策略：如果有敵人且有彈藥 → 射擊
        if self._ammo > 0 and state["enemies"]:
            self._ammo -= 1
            return {"action": "SHOOT", "direction": "RIGHT"}

        # 如果燃料不足 → 優先移動到補給點
        if self._fuel < 20 and state["fuel_supply"]:
            self._fuel -= 1
            return {"action": "MOVE", "direction": "UP"}

        # 否則 → 往出口移動
        self._fuel -= 1
        return {"action": "MOVE", "direction": "RIGHT"}

```
