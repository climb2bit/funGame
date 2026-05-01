# 🐺 Werewolf Game — Project Design Doc

A single-player terminal Werewolf (狼人杀) game in Python where AI opponents are powered by **Ollama** LLMs.
Built for kids to play AND to learn coding.

---

## 🎯 Project Goals

| Goal | Details |
|------|---------|
| 🌐 Bilingual | English & Chinese (切换语言) |
| 🤖 AI players | LLM agents via Ollama (local, private) |
| 🎨 Fun UI | ASCII art, colors, animations in terminal |
| 🐍 Python | Clean, readable code for kids to explore |
| 🎮 Roles | Werewolf, Villager, Seer, Witch, Hunter |
| 🔧 Flexible | 4–10 configurable player slots |

---

## 📁 Repository Structure (Target)

```
werewolf/
├── main.py                  # Entry point
├── config.py                # Settings (language, Ollama URL, players)
├── game/
│   ├── engine.py            # Game loop & phase controller
│   ├── roles.py             # Role definitions & abilities
│   ├── player.py            # Human and AI player classes
│   ├── state.py             # Game state (who's alive, votes, etc.)
│   └── phases/
│       ├── night.py         # Night phase logic
│       └── day.py           # Day phase logic (discussion + vote)
├── ai/
│   ├── ollama_client.py     # Ollama API wrapper
│   ├── agent.py             # AI decision-making logic
│   └── prompts/
│       ├── en/              # English prompts per role
│       └── zh/              # Chinese prompts per role
├── ui/
│   ├── display.py           # ASCII art renderer
│   ├── colors.py            # ANSI color helpers
│   ├── art.py               # Static ASCII art assets
│   └── animations.py        # Terminal animation effects
├── i18n/
│   ├── en.json              # English strings
│   └── zh.json              # Chinese strings
└── tests/
    ├── test_roles.py
    └── test_engine.py
```

---

## 🗺️ Task Sequence (implement in this order)

```
Task 01 → Task 02 → Task 03 → Task 04 → Task 05
  ↓           ↓         ↓         ↓         ↓
Setup      i18n      Roles    Ollama    Game State
                                ↓
                           Task 06 → Task 07 → Task 08
                             ↓         ↓         ↓
                           Night     Day      Win Cond.
                                                 ↓
                                           Task 09 → Task 10
                                             ↓         ↓
                                            UI      Polish
```

| # | Task File | What Gets Built |
|---|-----------|-----------------|
| 01 | `task-01-project-setup.md` | Folder structure, deps, `main.py` skeleton |
| 02 | `task-02-i18n-system.md` | Language switching, string loader |
| 03 | `task-03-roles-system.md` | All 5 roles with abilities |
| 04 | `task-04-ollama-client.md` | Ollama API client & AI agent |
| 05 | `task-05-game-state.md` | Player list, alive/dead, vote tracking |
| 06 | `task-06-night-phase.md` | Night actions (kill, check, save, shoot) |
| 07 | `task-07-day-phase.md` | AI discussion + human + voting |
| 08 | `task-08-win-conditions.md` | Victory checks, game-over screen |
| 09 | `task-09-ascii-ui.md` | Full ASCII art UI system |
| 10 | `task-10-polish.md` | Animations, config file, beginner mode |

---

## 🧩 Dependencies

```txt
# requirements.txt
requests>=2.31       # Ollama HTTP calls
colorama>=0.4.6      # Cross-platform ANSI colors
rich>=13.7           # Optional: pretty terminal panels
pyfiglet>=1.0        # ASCII title art
```

Ollama must be running locally: https://ollama.com
Recommended model: `llama3` or `qwen2` (good Chinese support)
