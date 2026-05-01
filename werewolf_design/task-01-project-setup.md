# Task 01 — Project Setup & Skeleton

## 🎯 Goal
Create the project folder structure, install dependencies, and write a working `main.py` that shows a welcome screen and launches the game loop stub.

---

## 📋 Deliverables

- [ ] Folder structure as defined in `README.md`
- [ ] `requirements.txt` with all deps
- [ ] `config.py` with default settings
- [ ] `main.py` entry point with argument parsing
- [ ] Placeholder `__init__.py` files in each package

---

## 🔧 Implementation Details

### `requirements.txt`
```
requests>=2.31
colorama>=0.4.6
pyfiglet>=1.0
```

### `config.py`
```python
# Game configuration — kids can edit this file!
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3"           # Change to "qwen2" for better Chinese
DEFAULT_LANGUAGE = "en"           # "en" or "zh"
MIN_PLAYERS = 4
MAX_PLAYERS = 10
DEFAULT_PLAYER_COUNT = 6          # 1 human + 5 AI
AI_RESPONSE_TIMEOUT = 30          # seconds
SHOW_AI_THINKING = True           # Show "..." when AI is thinking
DEBUG_MODE = False                # Print extra info for learning
```

### `main.py` skeleton
```python
#!/usr/bin/env python3
"""
🐺 Werewolf Game — powered by Ollama AI
狼人杀游戏 — 由 Ollama AI 驱动

Entry point. Run: python main.py
"""
import argparse
import sys
import config
from ui.display import show_title_screen
from game.engine import GameEngine

def parse_args():
    parser = argparse.ArgumentParser(description="Werewolf Game / 狼人杀")
    parser.add_argument("--lang", choices=["en", "zh"], default=config.DEFAULT_LANGUAGE)
    parser.add_argument("--players", type=int, default=config.DEFAULT_PLAYER_COUNT)
    parser.add_argument("--model", default=config.OLLAMA_MODEL)
    parser.add_argument("--debug", action="store_true")
    return parser.parse_args()

def main():
    args = parse_args()
    config.DEFAULT_LANGUAGE = args.lang
    config.OLLAMA_MODEL = args.model
    config.DEBUG_MODE = args.debug

    show_title_screen(args.lang)

    engine = GameEngine(
        language=args.lang,
        num_players=args.players,
        model=args.model,
    )
    engine.run()

if __name__ == "__main__":
    main()
```

---

## ✅ Acceptance Criteria

1. Running `python main.py` shows a title screen without errors
2. Running `python main.py --lang zh` switches to Chinese title
3. Running `python main.py --help` shows usage info
4. All import paths resolve (even if modules are stubs)

---

## 📚 Kid Learning Moment 🐣
> **What is `if __name__ == "__main__"`?**
> Python runs this block only when you run the file directly (not when another file imports it).
> It's like the "Start" button for your program!
