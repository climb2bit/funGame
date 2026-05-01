# Task 05 — Game State

## 🎯 Goal
Define the `Player` class and `GameState` object that track everything happening in the game: who's alive, what roles they have, vote tallies, and game history.

---

## 📋 Deliverables

- [ ] `game/player.py` — Human and AI player classes
- [ ] `game/state.py` — GameState with all tracking logic

---

## 🔧 Implementation Details

### `game/player.py`
```python
from dataclasses import dataclass, field
from game.roles import Role, RoleName, Faction
from ai.agent import AIAgent

@dataclass
class Player:
    id: int                    # 1-based player number
    name: str
    role: Role
    is_human: bool = False
    is_alive: bool = True
    agent: AIAgent = None      # None for human player

    @property
    def is_werewolf(self) -> bool:
        return self.role.name == RoleName.WEREWOLF

    @property
    def faction(self) -> Faction:
        return self.role.faction

    def __str__(self):
        status = "" if self.is_alive else " (Dead)"
        tag = "[YOU]" if self.is_human else ""
        return f"Player {self.id}: {self.name} {tag}{status}"

def create_players(num_players: int, human_name: str, language: str) -> list[Player]:
    """
    Create the full player list: 1 human + (num_players-1) AI.
    Assigns roles and creates AIAgent for each AI player.
    """
    from game.roles import assign_roles

    AI_NAMES_EN = ["Alice", "Bob", "Carol", "Dave", "Eve", "Frank", "Grace", "Heidi", "Ivan"]
    AI_NAMES_ZH = ["小明", "小红", "小强", "小花", "大壮", "小芳", "阿龙", "小燕", "大海"]

    name_pool = AI_NAMES_ZH if language == "zh" else AI_NAMES_EN
    roles = assign_roles(num_players)

    players = []
    ai_name_idx = 0

    # Human is always player 1
    human_player = Player(
        id=1,
        name=human_name,
        role=roles[0],
        is_human=True,
    )
    players.append(human_player)

    # Rest are AI
    for i in range(1, num_players):
        ai_name = name_pool[ai_name_idx % len(name_pool)]
        ai_name_idx += 1
        agent = AIAgent(player_name=ai_name, role=roles[i], language=language)
        players.append(Player(
            id=i + 1,
            name=ai_name,
            role=roles[i],
            is_human=False,
            agent=agent,
        ))

    return players
```

### `game/state.py`
```python
from dataclasses import dataclass, field
from game.player import Player
from game.roles import Faction

@dataclass
class NightResult:
    """Records what happened during a night phase."""
    round_number: int
    killed_by_wolves: Player = None   # Wolf target
    saved_by_witch: bool = False
    poisoned_by_witch: Player = None
    actually_died: list = field(default_factory=list)  # Final deaths

@dataclass
class GameState:
    players: list[Player]
    language: str = "en"
    round_number: int = 0
    game_over: bool = False
    winner: Faction = None
    history: list[str] = field(default_factory=list)  # Log of events

    # --- Player queries ---

    def alive_players(self) -> list[Player]:
        return [p for p in self.players if p.is_alive]

    def dead_players(self) -> list[Player]:
        return [p for p in self.players if not p.is_alive]

    def get_player_by_id(self, pid: int) -> Player:
        return next((p for p in self.players if p.id == pid), None)

    def alive_wolves(self) -> list[Player]:
        return [p for p in self.alive_players() if p.is_werewolf]

    def alive_good(self) -> list[Player]:
        return [p for p in self.alive_players() if p.faction == Faction.GOOD]

    def human_player(self) -> Player:
        return next(p for p in self.players if p.is_human)

    def get_role(self, role_name) -> Player:
        """Find alive player with given role (returns first match or None)."""
        from game.roles import RoleName
        return next(
            (p for p in self.alive_players() if p.role.name == role_name),
            None
        )

    # --- Game actions ---

    def kill_player(self, player: Player, reason: str = ""):
        player.is_alive = False
        msg = f"Round {self.round_number}: {player.name} died. {reason}"
        self.history.append(msg)

    def log(self, event: str):
        self.history.append(f"[R{self.round_number}] {event}")

    # --- Win condition check ---

    def check_winner(self) -> Faction | None:
        wolves = self.alive_wolves()
        good = self.alive_good()

        if len(wolves) == 0:
            return Faction.GOOD     # All wolves dead → village wins
        if len(wolves) >= len(good):
            return Faction.EVIL     # Wolves ≥ good players → wolves win
        return None

    def update_winner(self):
        result = self.check_winner()
        if result:
            self.winner = result
            self.game_over = True

    # --- Vote tallying ---

    def tally_votes(self, votes: dict) -> Player | None:
        """
        votes: {voter_player: target_player}
        Returns the player with most votes (None if tie).
        """
        from collections import Counter
        if not votes:
            return None
        count = Counter(votes.values())
        top_target, top_count = count.most_common(1)[0]
        # Check for tie
        tied = [p for p, c in count.items() if c == top_count]
        if len(tied) > 1:
            return None   # Tie → no elimination
        return top_target
```

---

## ✅ Acceptance Criteria

1. `create_players(6, "Tim", "en")` returns 6 Players with correct roles
2. Player 1 is always the human
3. `state.alive_players()` correctly filters dead players
4. `state.check_winner()` returns `Faction.GOOD` when no wolves remain
5. `state.tally_votes({...})` returns `None` on a tie

---

## 📚 Kid Learning Moment 🐣
> **What is a dataclass?**
> `@dataclass` is a Python shortcut. Instead of writing `__init__` yourself, Python writes it for you
> based on the fields you list. It's like a blueprint that Python fills in automatically! 🏗️
