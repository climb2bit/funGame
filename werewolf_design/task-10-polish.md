# Task 10 — Polish, Config & Beginner Mode

## 🎯 Goal
Add the finishing touches: a language selector menu, a "beginner mode" that explains what's happening at each step, an interactive config wizard, and optional debug output for kids learning to code.

---

## 📋 Deliverables

- [ ] Interactive main menu (Start / Language / Help / Quit)
- [ ] Beginner mode: explains each game event as it happens
- [ ] Debug mode: prints AI prompts + responses for learning
- [ ] Graceful exit handling (Ctrl+C)
- [ ] Quick-start README for kids (`HOW_TO_PLAY.md`)

---

## 🔧 Implementation Details

### Interactive Main Menu
Add to `main.py` before starting game:

```python
def show_main_menu(language: str) -> str:
    """Show menu and return chosen action: 'start', 'lang', 'quit'."""
    from ui.display import clear, show_title_screen
    from ui.colors import cyan, bold, yellow

    while True:
        clear()
        show_title_screen(language)

        options = {
            "1": ("start", "▶  Start Game" if language == "en" else "▶  开始游戏"),
            "2": ("lang",  "🌐 Switch Language / 切换语言"),
            "3": ("help",  "❓ How to Play" if language == "en" else "❓ 游戏规则"),
            "4": ("quit",  "✖  Quit" if language == "en" else "✖  退出"),
        }

        for key, (_, label) in options.items():
            print(f"  {cyan(key)}.  {label}")

        print()
        choice = input(bold("  Choose / 选择: ")).strip()

        if choice in options:
            action, _ = options[choice]
            if action == "lang":
                language = "zh" if language == "en" else "en"
                continue
            if action == "help":
                show_how_to_play(language)
                continue
            return action, language
```

### Beginner Mode Hints
Add `BEGINNER_MODE = True` to `config.py`. When enabled, show an explanation box after key events:

```python
# ui/display.py addition
HINTS_EN = {
    "night_start": "🌙 NIGHT: Everyone closes their eyes. Special roles wake up secretly.",
    "wolf_kill":   "🐺 WOLVES: They secretly choose one person to eliminate.",
    "seer_check":  "👁️  SEER: The seer secretly checks if one player is a wolf.",
    "witch_save":  "🧪 WITCH: The witch can use a potion to save tonight's victim.",
    "day_start":   "☀️  DAY: Everyone wakes up! Discuss and vote out a suspect.",
    "vote_start":  "🗳️  VOTE: Everyone votes. The player with most votes is eliminated.",
}

def show_hint(key: str, language: str):
    import config
    if not config.BEGINNER_MODE:
        return
    hints = HINTS_EN if language == "en" else HINTS_ZH
    msg = hints.get(key, "")
    if msg:
        print(f"\n  ╔{'─'*50}╗")
        print(f"  ║  💡 {msg:<47}║")
        print(f"  ╚{'─'*50}╝\n")
```

### Debug Mode Output
When `config.DEBUG_MODE = True`:

```python
# In ai/ollama_client.py chat() method, wrap with:
if config.DEBUG_MODE:
    print(f"\n[DEBUG] Prompt to {self.model}:")
    print(f"  SYSTEM: {system_prompt[:100]}...")
    print(f"  USER: {user_message[:200]}")
    print(f"[DEBUG] Response: {response[:200]}\n")
```

### Graceful Ctrl+C Handling
In `main.py`:
```python
try:
    main()
except KeyboardInterrupt:
    print("\n\n  Goodbye! / 再见! 👋\n")
    sys.exit(0)
```

---

## 📄 `HOW_TO_PLAY.md` — Kid's Guide

```markdown
# 🐺 How to Play Werewolf / 如何游戏

## Quick Start
1. Make sure Ollama is running: open a terminal, type `ollama serve`
2. Run the game: `python main.py`
3. Type your name and press Enter
4. Read your SECRET ROLE card carefully!

## The Goal
- 🐺 **Werewolves**: secretly kill all villagers before being caught
- 🏘️ **Villagers**: find and vote out all werewolves

## Each Round

### Night 🌙
- Everyone closes their eyes (pretend!)
- Wolves choose who to kill
- Seer secretly checks one player
- Witch decides to save or poison

### Day ☀️
- Deaths are announced
- Everyone discusses who the wolf might be
- Everyone votes — most votes = eliminated!

## Roles
| Role | What You Do |
|------|-------------|
| 🐺 Werewolf | Kill at night, lie during the day |
| 👨 Villager | Listen carefully, vote wisely |
| 👁️ Seer | Check identities at night |
| 🧙 Witch | Use potions to help the village |
| 🎯 Hunter | Shoot someone when you die |

## Tips for Kids
- Pay attention to who the AI players accuse!
- The Seer is the most powerful good role — protect them.
- Don't reveal your role unless you have to.
- Have fun! The AI might surprise you 😄
```

---

## ✅ Acceptance Criteria

1. Main menu appears on launch; language can be toggled before starting
2. Beginner mode shows hint boxes at each phase transition
3. Debug mode prints AI prompt/response (truncated to 200 chars)
4. Ctrl+C at any point exits cleanly with a goodbye message
5. `HOW_TO_PLAY.md` is accurate and understandable by a child
6. Game can be started with `python main.py --beginner` flag

---

## 📚 Kid Learning Moment 🐣
> **What is `try` / `except`?**
> Sometimes things go wrong in programs (like the player pressing Ctrl+C).
> `try` says "attempt this code" and `except` says "if something goes wrong, do THIS instead".
> It's like wearing a helmet — you hope you don't need it, but you're glad it's there! ⛑️
