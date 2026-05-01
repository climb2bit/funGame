# Task 02 — Internationalization (i18n) System

## 🎯 Goal
Build a language system so ALL text in the game (menus, prompts, announcements) can switch between English 🇬🇧 and Chinese 🇨🇳 with a single setting.

---

## 📋 Deliverables

- [ ] `i18n/en.json` — all English strings
- [ ] `i18n/zh.json` — all Chinese strings
- [ ] `i18n/__init__.py` — `t()` translation function
- [ ] Language selector in the main menu

---

## 🔧 Implementation Details

### String file structure: `i18n/en.json`
```json
{
  "title": "WEREWOLF",
  "subtitle": "Powered by Ollama AI",
  "menu_start": "Start Game",
  "menu_language": "Switch Language",
  "menu_quit": "Quit",

  "phase_night": "Night falls... everyone close your eyes.",
  "phase_day": "Dawn breaks. The village wakes.",
  "phase_vote": "It's time to vote. Who is the werewolf?",

  "role_werewolf": "Werewolf",
  "role_villager": "Villager",
  "role_seer": "Seer",
  "role_witch": "Witch",
  "role_hunter": "Hunter",

  "role_desc_werewolf": "You are a Werewolf! Work with other wolves to eliminate villagers.",
  "role_desc_villager": "You are a Villager! Find and eliminate the werewolves.",
  "role_desc_seer": "You are the Seer! Each night, you can check one player's identity.",
  "role_desc_witch": "You are the Witch! You have one healing potion and one poison potion.",
  "role_desc_hunter": "You are the Hunter! If you die, you can shoot one player.",

  "night_werewolf_choose": "Werewolves, choose your victim (enter player number):",
  "night_seer_choose": "Seer, choose a player to check:",
  "night_seer_result_wolf": "{name} IS a Werewolf!",
  "night_seer_result_good": "{name} is NOT a Werewolf.",
  "night_witch_save": "Someone was killed tonight. Use healing potion to save them? (y/n):",
  "night_witch_poison": "Use poison potion on someone? (y/n):",
  "night_witch_choose_target": "Choose who to poison:",

  "day_announce_death": "{name} was found dead.",
  "day_announce_nobody": "Nobody died last night. The village is safe... for now.",
  "day_discuss": "{name} says:",
  "day_vote_prompt": "Who do you vote to eliminate? (enter number):",
  "day_vote_result": "{name} has been eliminated by the village vote.",
  "day_no_consensus": "The village could not reach a consensus. Nobody is eliminated.",

  "hunter_shoot": "Hunter {name} is dying! They may shoot one player:",
  "win_werewolf": "🐺 The Werewolves win! They have taken over the village.",
  "win_village": "🎉 The Village wins! All werewolves have been eliminated.",
  "player_you": "YOU",
  "player_ai": "AI",
  "dead": "(Dead)",
  "press_enter": "Press Enter to continue...",
  "your_turn": "It's your turn to speak.",
  "enter_speech": "Your speech (press Enter when done):"
}
```

### `i18n/zh.json` (Chinese version)
```json
{
  "title": "狼人杀",
  "subtitle": "由 Ollama AI 驱动",
  "menu_start": "开始游戏",
  "menu_language": "切换语言",
  "menu_quit": "退出",

  "phase_night": "天黑请闭眼...",
  "phase_day": "天亮了。村民们醒来。",
  "phase_vote": "是时候投票了。谁是狼人？",

  "role_werewolf": "狼人",
  "role_villager": "平民",
  "role_seer": "预言家",
  "role_witch": "女巫",
  "role_hunter": "猎人",

  "role_desc_werewolf": "你是狼人！与其他狼人合作消灭平民。",
  "role_desc_villager": "你是平民！找出并消灭狼人。",
  "role_desc_seer": "你是预言家！每晚可以查验一名玩家的身份。",
  "role_desc_witch": "你是女巫！你有一瓶解药和一瓶毒药。",
  "role_desc_hunter": "你是猎人！如果你死了，你可以开枪带走一名玩家。",

  "night_werewolf_choose": "狼人请选择你们的目标（输入玩家编号）：",
  "night_seer_choose": "预言家请选择一名玩家查验：",
  "night_seer_result_wolf": "{name} 是狼人！",
  "night_seer_result_good": "{name} 不是狼人。",
  "night_witch_save": "今晚有人被杀。使用解药救人吗？(y/n)：",
  "night_witch_poison": "使用毒药毒杀某人吗？(y/n)：",
  "night_witch_choose_target": "选择毒杀目标：",

  "day_announce_death": "{name} 昨晚死亡了。",
  "day_announce_nobody": "昨晚平安无事。村子暂时安全了...",
  "day_discuss": "{name} 说：",
  "day_vote_prompt": "你投票淘汰谁？（输入编号）：",
  "day_vote_result": "{name} 被村民投票淘汰。",
  "day_no_consensus": "村民们无法达成共识。今天没有人被淘汰。",

  "hunter_shoot": "猎人 {name} 中枪倒下！他们可以开枪带走一名玩家：",
  "win_werewolf": "🐺 狼人获胜！他们已经占领了村庄。",
  "win_village": "🎉 村民获胜！所有狼人都被消灭了。",
  "player_you": "你",
  "player_ai": "AI",
  "dead": "（已死亡）",
  "press_enter": "按回车键继续...",
  "your_turn": "轮到你发言了。",
  "enter_speech": "你的发言（完成后按回车键）："
}
```

### `i18n/__init__.py`
```python
import json
import os
import config

_strings = {}

def load_language(lang: str):
    """Load the string file for the given language code."""
    global _strings
    path = os.path.join(os.path.dirname(__file__), f"{lang}.json")
    with open(path, encoding="utf-8") as f:
        _strings = json.load(f)

def t(key: str, **kwargs) -> str:
    """
    Translate a key to the current language.
    Supports {variable} substitution.

    Example:
        t("day_announce_death", name="Alice")
        → "Alice was found dead."
    """
    text = _strings.get(key, f"[MISSING: {key}]")
    if kwargs:
        text = text.format(**kwargs)
    return text

# Load default on import
load_language(config.DEFAULT_LANGUAGE)
```

---

## ✅ Acceptance Criteria

1. `t("title")` returns `"WEREWOLF"` in English, `"狼人杀"` in Chinese
2. `t("day_announce_death", name="Bob")` returns `"Bob was found dead."`
3. Calling `load_language("zh")` then `t("title")` returns Chinese
4. Missing keys return `[MISSING: key_name]` not a crash

---

## 📚 Kid Learning Moment 🐣
> **What is a dictionary in Python?**
> JSON files are just dictionaries saved as files! A dictionary maps a "key" to a "value",
> like a real dictionary maps a word to its definition.
> `{"name": "Alice"}` → the key is `"name"`, the value is `"Alice"`.
