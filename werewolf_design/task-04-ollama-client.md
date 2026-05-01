# Task 04 — Ollama Client & AI Agent

## 🎯 Goal
Build the bridge between the game and Ollama. Each AI player uses an LLM to decide night actions and generate in-character dialogue during the day phase.

---

## 📋 Deliverables

- [ ] `ai/ollama_client.py` — HTTP client for Ollama `/api/chat`
- [ ] `ai/agent.py` — AI decision logic per role
- [ ] `ai/prompts/en/` — English prompt templates per role
- [ ] `ai/prompts/zh/` — Chinese prompt templates per role
- [ ] Connectivity check on game start

---

## 🔧 Implementation Details

### `ai/ollama_client.py`
```python
import requests
import json
import config

class OllamaClient:
    """Wrapper for the Ollama local API."""

    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or config.OLLAMA_BASE_URL
        self.model = model or config.OLLAMA_MODEL

    def check_connection(self) -> bool:
        """Return True if Ollama is reachable."""
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return r.status_code == 200
        except requests.ConnectionError:
            return False

    def chat(self, system_prompt: str, user_message: str) -> str:
        """
        Send a chat message and return the model's text response.
        Uses streaming=False for simplicity.
        """
        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        }
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=config.AI_RESPONSE_TIMEOUT,
            )
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"].strip()
        except requests.Timeout:
            return "[AI timed out — no response]"
        except Exception as e:
            return f"[AI error: {e}]"
```

### `ai/prompts/en/` — Prompt Templates

**`system_werewolf.txt`**
```
You are playing Werewolf, a social deduction game. You are a WEREWOLF.
Your goal: eliminate all villagers without being detected.

Rules for your responses:
- During night: choose a player number to kill (respond with ONLY a number).
- During day discussion: speak naturally as if you're an innocent villager.
  Deflect suspicion. Cast doubt on others. Never reveal you're a wolf.
- During voting: vote to eliminate a non-wolf player.
- Keep responses SHORT (1-3 sentences for speech, single number for actions).
- Do NOT break character.
```

**`system_villager.txt`**
```
You are playing Werewolf, a social deduction game. You are a VILLAGER.
Your goal: find and vote out all werewolves.

Rules for your responses:
- During day discussion: share your suspicions, reason out loud, listen to others.
- During voting: vote for the player you find most suspicious.
- Keep responses SHORT (1-3 sentences).
- You do NOT know who the werewolves are — reason from clues.
```

**`system_seer.txt`**
```
You are playing Werewolf, a social deduction game. You are the SEER.
Your goal: secretly identify werewolves and guide the village without revealing yourself.

Rules for your responses:
- During night: choose a player number to investigate (respond with ONLY a number).
- During day: subtly guide villagers toward/away from suspects using your secret knowledge.
  Be careful — revealing you're the Seer makes you a wolf target.
- Keep responses SHORT (1-3 sentences for speech, single number for actions).
```

**`system_witch.txt`**
```
You are playing Werewolf, a social deduction game. You are the WITCH.
Your goal: support the village using your potions wisely.

Rules for your responses:
- Heal potion (once): decide y/n to save tonight's victim.
- Poison potion (once): decide y/n to use poison, then choose a player number.
- During day: contribute to discussion. Consider what you know from night.
- Respond with ONLY "y" or "n" for potion decisions, or a number for player selection.
```

**`system_hunter.txt`**
```
You are playing Werewolf, a social deduction game. You are the HUNTER.
Your goal: support the village. If eliminated, you get to shoot one player.

Rules for your responses:
- During day: reason about who the werewolves might be.
- If eliminated: choose a player number to shoot (respond with ONLY a number).
- Keep responses SHORT (1-3 sentences for speech).
```

### `ai/agent.py`
```python
import os
import random
from game.roles import RoleName
from ai.ollama_client import OllamaClient
import config

class AIAgent:
    """
    Wraps an OllamaClient with role-specific prompting.
    Each AI player has one AIAgent.
    """

    def __init__(self, player_name: str, role, language: str = "en"):
        self.player_name = player_name
        self.role = role
        self.language = language
        self.client = OllamaClient()
        self.system_prompt = self._load_system_prompt()
        self.memory: list[str] = []  # Remember key game events

    def _load_system_prompt(self) -> str:
        role_key = self.role.name.value  # e.g. "werewolf"
        prompt_path = os.path.join(
            os.path.dirname(__file__),
            "prompts", self.language, f"system_{role_key}.txt"
        )
        with open(prompt_path, encoding="utf-8") as f:
            return f.read()

    def add_memory(self, event: str):
        """Record a game event this agent witnessed."""
        self.memory.append(event)
        if len(self.memory) > 20:          # Keep memory bounded
            self.memory = self.memory[-20:]

    def _build_context(self, extra: str = "") -> str:
        context_lines = [f"You are player: {self.player_name}."]
        if self.memory:
            context_lines.append("What you know so far:")
            context_lines.extend(f"- {m}" for m in self.memory)
        if extra:
            context_lines.append(extra)
        return "\n".join(context_lines)

    def choose_target(self, alive_players: list, exclude: list = None) -> int:
        """
        Ask AI to pick a player index from alive_players.
        Returns a valid index (falls back to random if AI gives invalid answer).
        """
        candidates = [p for p in alive_players if p not in (exclude or [])]
        if not candidates:
            return None

        names_list = "\n".join(f"{i+1}. {p.name}" for i, p in enumerate(candidates))
        prompt = self._build_context(
            f"Living players:\n{names_list}\n\nChoose a player number:"
        )
        response = self.client.chat(self.system_prompt, prompt)

        # Parse a number from AI response
        for token in response.split():
            token = token.strip(".,!?")
            if token.isdigit():
                idx = int(token) - 1
                if 0 <= idx < len(candidates):
                    return candidates[idx]

        # Fallback: random choice
        return random.choice(candidates)

    def generate_speech(self, context: str) -> str:
        """Generate in-character day-phase speech."""
        prompt = self._build_context(context)
        return self.client.chat(self.system_prompt, prompt)

    def decide_yes_no(self, question: str) -> bool:
        """Ask AI a yes/no question. Returns True for yes."""
        prompt = self._build_context(question)
        response = self.client.chat(self.system_prompt, prompt).lower()
        return response.startswith("y") or "yes" in response or "是" in response
```

---

## ✅ Acceptance Criteria

1. `OllamaClient().check_connection()` returns True when Ollama is running
2. `OllamaClient().chat("You are a helper", "Say hello")` returns non-empty string
3. `AIAgent` loads the correct prompt file for each role
4. `agent.choose_target(players)` always returns a valid player (never crashes)
5. If Ollama is offline, game shows a clear error message on startup

---

## 📚 Kid Learning Moment 🐣
> **What is an API?**
> An API is like a restaurant menu — it lists what you can *ask for* and how to ask.
> Ollama has an API at `http://localhost:11434`. We send it a message, it sends back the AI's reply.
> Our code is like the waiter between us and the kitchen (the AI model)! 🍽️
