# Task 09 — ASCII Art UI System

## 🎯 Goal
Build the entire terminal UI: colorful ASCII art title, phase banners, role cards, player lists, speech bubbles, and a game-over screen. This makes the game look amazing in a terminal! 🎨

---

## 📋 Deliverables

- [ ] `ui/colors.py` — ANSI color helpers
- [ ] `ui/art.py` — static ASCII art assets
- [ ] `ui/display.py` — all display functions used by phases
- [ ] `ui/animations.py` — typing effect, spinner, suspense pause

---

## 🎨 Visual Design Language

| Element | Color |
|---------|-------|
| Night phase | Dark blue / purple |
| Day phase | Yellow / cyan |
| Werewolf reveals | Red |
| Good team | Green |
| System messages | White |
| Warnings / deaths | Bold Red |
| Secret info | Magenta (player eyes only) |

---

## 🔧 Implementation Details

### `ui/colors.py`
```python
"""ANSI color codes for terminal styling."""

class Color:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"

    # Foreground
    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"

    # Bright variants
    BRIGHT_RED    = "\033[91m"
    BRIGHT_GREEN  = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE   = "\033[94m"
    BRIGHT_CYAN   = "\033[96m"

def red(s):     return f"{Color.BRIGHT_RED}{s}{Color.RESET}"
def green(s):   return f"{Color.BRIGHT_GREEN}{s}{Color.RESET}"
def yellow(s):  return f"{Color.BRIGHT_YELLOW}{s}{Color.RESET}"
def cyan(s):    return f"{Color.BRIGHT_CYAN}{s}{Color.RESET}"
def blue(s):    return f"{Color.BLUE}{s}{Color.RESET}"
def magenta(s): return f"{Color.MAGENTA}{s}{Color.RESET}"
def bold(s):    return f"{Color.BOLD}{s}{Color.RESET}"
def dim(s):     return f"{Color.DIM}{s}{Color.RESET}"
```

### `ui/art.py` — ASCII Art Assets
```python
WOLF_ASCII = r"""
    / \__
   (    @\___
   /         O
  /   (_____/
 /_____/   U
"""

VILLAGE_ASCII = r"""
     /\   /\   /\
    /  \ /  \ /  \
   / /\ X /\ X /\ \
  /_/  \/_/  \/_/  \
  |  [=]  |  [=]  |
  |_______|_______| 
"""

MOON_ASCII = r"""
    *  .  *    .
  .   ___      *
    /     \  .
   |  ) (  |    *
    \ ___ /
  .   ---    .
    *  .  *
"""

SUN_ASCII = r"""
    \  |  /
  -- (   ) --
     _\_|_/_
    /  \|/  \
   |    *    |
    \__/|\__/
  -- (   ) --
    /  |  \
"""

ROLE_CARDS = {
    "werewolf": r"""
╔══════════════════╗
║   🐺  WEREWOLF   ║
║   狼  人         ║
╠══════════════════╣
║  Faction: EVIL   ║
╚══════════════════╝""",
    "villager": r"""
╔══════════════════╗
║   👨  VILLAGER   ║
║   平  民         ║
╠══════════════════╣
║  Faction: GOOD   ║
╚══════════════════╝""",
    "seer": r"""
╔══════════════════╗
║   👁️   SEER      ║
║   预  言  家     ║
╠══════════════════╣
║  Faction: GOOD   ║
╚══════════════════╝""",
    "witch": r"""
╔══════════════════╗
║   🧙  WITCH      ║
║   女  巫         ║
╠══════════════════╣
║  Faction: GOOD   ║
╚══════════════════╝""",
    "hunter": r"""
╔══════════════════╗
║   🎯  HUNTER     ║
║   猎  人         ║
╠══════════════════╣
║  Faction: GOOD   ║
╚══════════════════╝""",
}
```

### `ui/animations.py`
```python
import sys
import time
import config

def type_print(text: str, delay: float = 0.03):
    """Print text character by character (typewriter effect)."""
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def thinking_spinner(duration: float = 2.0, label: str = "Thinking"):
    """Show a spinner while AI is "thinking"."""
    if not config.SHOW_AI_THINKING:
        time.sleep(duration)
        return
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        sys.stdout.write(f"\r  {frames[i % len(frames)]} {label}...")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write("\r" + " " * 30 + "\r")
    sys.stdout.flush()

def suspense_pause(message: str = ""):
    """Dramatic pause with dots."""
    if message:
        print(message, end="", flush=True)
    for _ in range(3):
        time.sleep(0.7)
        print(".", end="", flush=True)
    print()
    time.sleep(0.5)
```

### `ui/display.py` — Key Functions
```python
import os
from ui.colors import *
from ui.art import WOLF_ASCII, SUN_ASCII, MOON_ASCII, ROLE_CARDS
from ui.animations import type_print, suspense_pause
from i18n import t

WIDTH = 60   # Terminal width to target

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def divider(char="─", color=Color.DIM):
    print(f"{color}{char * WIDTH}{Color.RESET}")

def show_title_screen(language: str = "en"):
    clear()
    print(red(WOLF_ASCII))
    title = "  W E R E W O L F  " if language == "en" else "  狼  人  杀  "
    print(bold(yellow(f"{'═' * WIDTH}")))
    print(bold(yellow(f"{title.center(WIDTH)}")))
    print(bold(yellow(f"{'═' * WIDTH}")))
    print(dim("  Powered by Ollama AI".center(WIDTH)))
    print()

def show_phase_banner(phase: str, language: str):
    clear()
    if phase == "night":
        art = MOON_ASCII
        color = blue
        title = t("phase_night")
    else:
        art = SUN_ASCII
        color = yellow
        title = t("phase_day")
    print(color(art))
    print(bold(color(f"\n  {title}\n")))
    divider()

def show_role_card(role, language: str):
    key = role.name.value
    card = ROLE_CARDS.get(key, "")
    print(magenta(card))
    desc = t(f"role_desc_{key}")
    print(bold(f"\n  {desc}\n"))
    divider()

def show_player_roster(players, language: str):
    print(bold(cyan("\n  PLAYERS / 玩家名单\n")))
    for p in players:
        tag = bold(yellow("  ★ YOU")) if p.is_human else "    "
        status = green("●") if p.is_alive else red("✖")
        print(f"  {status} {p.id}. {p.name} {tag}")
    print()

def show_player_list(players):
    """Show numbered list of players for selection."""
    for i, p in enumerate(players, 1):
        you = bold(yellow(" [YOU]")) if p.is_human else ""
        print(f"  {cyan(str(i))}. {p.name}{you}")

def prompt_player_choice(players) -> object:
    """Ask the human to pick a player by number."""
    while True:
        raw = input(cyan("  > ")).strip()
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(players):
                return players[idx]
        print(red("  Invalid choice. Try again."))

def show_speech_bubble(name: str, text: str):
    """Display a player's speech in an ASCII speech bubble."""
    divider("·")
    print(bold(f"  💬 {name}:"))
    for line in text.split("\n"):
        print(f"     {line}")
    print()

def print_info(msg: str):
    type_print(f"  {msg}")

def print_warning(msg: str):
    type_print(bold(red(f"  ⚠  {msg}")))

def print_secret(msg: str):
    """For the human player's eyes only (shown in magenta)."""
    type_print(magenta(f"  🔐 {msg}"))

def show_game_over(winner_faction, players, language: str):
    clear()
    from game.roles import Faction
    if winner_faction == Faction.GOOD:
        print(bold(green("\n" + "═" * WIDTH)))
        print(bold(green(t("win_village").center(WIDTH))))
        print(bold(green("═" * WIDTH + "\n")))
    else:
        print(bold(red("\n" + "═" * WIDTH)))
        print(bold(red(t("win_werewolf").center(WIDTH))))
        print(bold(red("═" * WIDTH + "\n")))

    print(bold("  Final Roles / 最终身份:\n"))
    for p in players:
        role_name = t(f"role_{p.role.name.value}")
        faction_color = red if p.role.faction.value == "evil" else green
        status = "" if p.is_alive else dim("  (dead)")
        print(f"  {faction_color('■')} {p.name:<12} → {bold(faction_color(role_name))}{status}")

def pause(short: bool = False):
    if short:
        import time; time.sleep(1.2)
    else:
        input(dim(f"\n  {t('press_enter')}"))
```

---

## ✅ Acceptance Criteria

1. Title screen shows ASCII wolf art with color on first launch
2. Night banner shows moon art in blue; Day banner shows sun in yellow
3. Role card is shown at game start (only human's role, styled in magenta)
4. Speech bubbles display AI names and dialogue clearly
5. Player list uses numbers for selection
6. Game-over screen reveals ALL players' roles in color
7. Typewriter effect plays on key announcements
8. Works on Windows (colorama) and Mac/Linux

---

## 📚 Kid Learning Moment 🐣
> **What are ANSI escape codes?**
> Your terminal understands secret codes hidden in text — like `\033[31m` means "turn text red".
> These codes go AROUND the text and reset at the end. It's like putting invisible color stickers
> in the middle of a sentence! 🎨 The `colorama` library makes these work on Windows too.
