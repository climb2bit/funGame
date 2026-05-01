# Task 03 — Roles System

## 🎯 Goal
Define all 5 game roles as Python classes with their abilities, faction membership, and night-action logic.

---

## 📋 Deliverables

- [ ] `game/roles.py` — base Role class + 5 role subclasses
- [ ] Role assignment logic (balanced for player count)
- [ ] Unit tests in `tests/test_roles.py`

---

## 🐺 Role Reference Table

| Role | Faction | Night Action | Special |
|------|---------|-------------|---------|
| Werewolf 狼人 | Evil | Kill one villager | Knows other wolves |
| Villager 平民 | Good | None | Votes in day phase |
| Seer 预言家 | Good | Reveal one player's alignment | None |
| Witch 女巫 | Good | Save OR poison (once each) | 2 single-use potions |
| Hunter 猎人 | Good | None at night | Shoot when eliminated |

---

## 🔧 Implementation Details

### `game/roles.py`
```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class Faction(Enum):
    GOOD = "good"
    EVIL = "evil"

class RoleName(Enum):
    WEREWOLF = "werewolf"
    VILLAGER = "villager"
    SEER = "seer"
    WITCH = "witch"
    HUNTER = "hunter"

@dataclass
class Role:
    name: RoleName
    faction: Faction
    has_night_action: bool = False
    description_key: str = ""   # i18n key for role description

    def night_action_key(self) -> str:
        """i18n key for night action prompt"""
        return f"night_{self.name.value}_choose"

class Werewolf(Role):
    def __init__(self):
        super().__init__(
            name=RoleName.WEREWOLF,
            faction=Faction.EVIL,
            has_night_action=True,
            description_key="role_desc_werewolf",
        )

class Villager(Role):
    def __init__(self):
        super().__init__(
            name=RoleName.VILLAGER,
            faction=Faction.GOOD,
            has_night_action=False,
            description_key="role_desc_villager",
        )

class Seer(Role):
    def __init__(self):
        super().__init__(
            name=RoleName.SEER,
            faction=Faction.GOOD,
            has_night_action=True,
            description_key="role_desc_seer",
        )

@dataclass
class Witch(Role):
    heal_potion: bool = True    # Can save tonight's victim (once)
    poison_potion: bool = True  # Can poison one player (once)

    def __init__(self):
        super().__init__(
            name=RoleName.WITCH,
            faction=Faction.GOOD,
            has_night_action=True,
            description_key="role_desc_witch",
        )

class Hunter(Role):
    def __init__(self):
        super().__init__(
            name=RoleName.HUNTER,
            faction=Faction.GOOD,
            has_night_action=False,
            description_key="role_desc_hunter",
        )
    # Hunter's shoot ability is triggered on death, not at night

# ---------------------------------------------------------------------------
# Role assignment: balanced by player count
# ---------------------------------------------------------------------------

ROLE_CONFIGS = {
    #  count: (werewolves, [special roles], rest=villagers)
    4:  (1, [Seer]),
    5:  (1, [Seer, Witch]),
    6:  (2, [Seer, Witch]),
    7:  (2, [Seer, Witch, Hunter]),
    8:  (2, [Seer, Witch, Hunter]),
    9:  (3, [Seer, Witch, Hunter]),
    10: (3, [Seer, Witch, Hunter]),
}

def assign_roles(num_players: int) -> list[Role]:
    """
    Return a shuffled list of Role objects for the given player count.
    Raises ValueError if num_players is out of range.
    """
    import random
    if num_players not in ROLE_CONFIGS:
        raise ValueError(f"Player count {num_players} not supported (4–10).")

    wolf_count, specials = ROLE_CONFIGS[num_players]
    roles = []
    roles += [Werewolf() for _ in range(wolf_count)]
    roles += [cls() for cls in specials]
    villager_count = num_players - len(roles)
    roles += [Villager() for _ in range(villager_count)]
    random.shuffle(roles)
    return roles
```

---

## ✅ Acceptance Criteria

1. `assign_roles(6)` returns exactly 6 Role objects
2. For 6 players: 2 Werewolves, 1 Seer, 1 Witch, 2 Villagers
3. Each role has correct `.faction` attribute
4. `assign_roles(3)` raises `ValueError`
5. Calling `assign_roles()` twice gives different orderings

---

## 📚 Kid Learning Moment 🐣
> **What is inheritance in Python?**
> `Werewolf(Role)` means Werewolf *inherits* from Role — it gets all of Role's features
> for free, and can add its own. It's like: a Werewolf IS a Role, but with extra wolf powers! 🐺
