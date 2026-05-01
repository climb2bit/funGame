# Task 08 — Win Conditions & Game Engine

## 🎯 Goal
Build the main game loop in `GameEngine` that orchestrates night/day phases, checks win conditions after each action, and shows the final game-over screen.

---

## 📋 Deliverables

- [ ] `game/engine.py` — `GameEngine` class with `run()` loop
- [ ] Win detection after every kill (not just end of round)
- [ ] Game-over screen showing winner and role reveal

---

## 🏆 Win Conditions

| Condition | Winner |
|-----------|--------|
| All werewolves eliminated | 🎉 Village (Good) |
| Werewolves ≥ surviving good players | 🐺 Werewolves (Evil) |

Check after: each night death, each hunter shot, each vote elimination.

---

## 🔧 Implementation Details

### `game/engine.py`
```python
import time
from game.state import GameState
from game.player import create_players
from game.phases.night import run_night_phase
from game.phases.day import run_day_phase
from game.roles import Faction
from ai.ollama_client import OllamaClient
from i18n import t, load_language
from ui.display import (
    show_title_screen, show_role_card, show_player_roster,
    show_game_over, print_info, print_warning, pause
)

class GameEngine:
    """Orchestrates the full Werewolf game."""

    def __init__(self, language: str, num_players: int, model: str):
        self.language = language
        self.num_players = num_players
        self.model = model
        self.state = None

    def run(self):
        """Entry point — runs pre-game setup then main loop."""
        load_language(self.language)

        # Check Ollama is available
        if not self._check_ollama():
            return

        # Setup
        human_name = self._get_player_name()
        players = create_players(self.num_players, human_name, self.language)
        self.state = GameState(players=players, language=self.language)

        # Show roster (no roles revealed yet)
        show_player_roster(players, self.language)
        pause()

        # Reveal human's role privately
        human = self.state.human_player()
        show_role_card(human.role, self.language)
        pause()

        # Main loop
        self._main_loop()

    def _main_loop(self):
        """Alternate night/day until someone wins."""
        while not self.state.game_over:
            self.state.round_number += 1

            # --- Night ---
            night_result = run_night_phase(self.state)

            if self.state.game_over:
                break

            # --- Day ---
            run_day_phase(self.state, night_result)

        # Game over!
        self._show_end_screen()

    def _check_ollama(self) -> bool:
        """Verify Ollama is running before the game starts."""
        client = OllamaClient()
        print_info("Checking Ollama connection...")
        if not client.check_connection():
            print_warning(
                "❌ Cannot connect to Ollama at http://localhost:11434\n"
                "   Please start Ollama and try again.\n"
                "   Install: https://ollama.com"
            )
            return False
        print_info("✅ Ollama connected!")
        return True

    def _get_player_name(self) -> str:
        """Ask the human player for their name."""
        print_info("What is your name? / 你叫什么名字？")
        name = input("> ").strip()
        return name if name else "Player"

    def _show_end_screen(self):
        """Show the winner and reveal all roles."""
        winner_faction = self.state.winner
        show_game_over(winner_faction, self.state.players, self.language)
```

### Win condition flow diagram

```
Night ends
    │
    ├─► any deaths? → check_winner() → game_over? → END
    │
    ▼
Day starts
    │
    ├─► hunter shoots? → check_winner() → game_over? → END
    │
    ├─► vote eliminates? → check_winner() → game_over? → END
    │
    ├─► hunter shoots? → check_winner() → game_over? → END
    │
    ▼
Next night round
```

---

## ✅ Acceptance Criteria

1. Game loops correctly: round 1 night → day → round 2 night → day...
2. Game ends immediately when win condition is met (mid-round if needed)
3. Game-over screen shows all players' true roles (the big reveal!)
4. Ollama connection failure shows a friendly error, doesn't crash
5. Human name input accepts Chinese characters
6. Round counter increments each loop

---

## 📚 Kid Learning Moment 🐣
> **What is a `while` loop?**
> A `while` loop keeps running as long as a condition is True.
> `while not self.state.game_over:` means "keep playing until someone wins!"
> If nobody ever wins, it would loop forever — so we must always update `game_over`. ♾️→🛑
