# Task 06 — Night Phase

## 🎯 Goal
Implement the full night sequence: wolves kill, seer investigates, witch uses potions — with human prompts for human players and AI decisions for AI players.

---

## 📋 Deliverables

- [ ] `game/phases/night.py` — `run_night_phase(state)` function
- [ ] Correct action order: Wolves → Seer → Witch
- [ ] Human player gets text prompts; AI players call their agent
- [ ] Returns a `NightResult` object

---

## 🔧 Night Phase Action Order

```
1. 🐺 Werewolves wake → choose a victim (AI/human wolf selects)
2. 👁️ Seer wakes → checks one player's alignment
3. 🧪 Witch wakes → optionally save victim OR poison someone
4. All sleep → compute final deaths
```

---

## 🔧 Implementation Details

### `game/phases/night.py`
```python
from game.state import GameState, NightResult
from game.roles import RoleName, Faction
from game.player import Player
from i18n import t
from ui.display import (
    show_phase_banner, show_player_list, prompt_player_choice,
    print_info, print_secret, pause
)

def run_night_phase(state: GameState) -> NightResult:
    """Execute all night actions and return a NightResult."""
    result = NightResult(round_number=state.round_number)
    state.log("Night phase begins")

    show_phase_banner("night", state.language)
    pause()

    # Step 1: Werewolves choose a target
    result.killed_by_wolves = _wolf_action(state)

    # Step 2: Seer investigates
    _seer_action(state)

    # Step 3: Witch uses potions
    _witch_action(state, result)

    # Step 4: Compute actual deaths
    _resolve_deaths(state, result)

    return result


def _wolf_action(state: GameState) -> Player | None:
    """Wolves collectively choose a victim."""
    wolves = state.alive_wolves()
    good_players = state.alive_good()

    if not wolves or not good_players:
        return None

    human_wolf = next((w for w in wolves if w.is_human), None)

    if human_wolf:
        # Human wolf: show secret info, ask for input
        print_secret(f"[SECRET] You are a Werewolf. Your wolf partners: "
                     + ", ".join(w.name for w in wolves if not w.is_human))
        print_secret(t("night_werewolf_choose"))
        show_player_list(good_players)
        choice = prompt_player_choice(good_players)
        target = choice
    else:
        # AI wolves: let the lead wolf decide
        lead_wolf = wolves[0]
        # Give wolf agent memory of its allies
        lead_wolf.agent.add_memory(
            "Your wolf partners: " + ", ".join(w.name for w in wolves[1:])
        )
        target = lead_wolf.agent.choose_target(good_players)

    # Share the choice with all wolf agents
    for wolf in wolves:
        if wolf.agent:
            wolf.agent.add_memory(f"Tonight the wolves killed: {target.name}")

    state.log(f"Wolves targeted: {target.name}")
    return target


def _seer_action(state: GameState):
    """Seer investigates one player."""
    seer = state.get_role(RoleName.SEER)
    if not seer:
        return

    alive_others = [p for p in state.alive_players() if p != seer]

    if seer.is_human:
        print_secret(t("night_seer_choose"))
        show_player_list(alive_others)
        target = prompt_player_choice(alive_others)
    else:
        target = seer.agent.choose_target(alive_others)

    # Reveal result
    if target.is_werewolf:
        result_msg = t("night_seer_result_wolf", name=target.name)
    else:
        result_msg = t("night_seer_result_good", name=target.name)

    if seer.is_human:
        print_secret(f"[SEER RESULT] {result_msg}")
        pause()
    else:
        seer.agent.add_memory(f"Seer check: {result_msg}")

    state.log(f"Seer checked {target.name}: {'wolf' if target.is_werewolf else 'good'}")


def _witch_action(state: GameState, result: NightResult):
    """Witch decides to save / poison."""
    from game.roles import Witch as WitchRole
    witch_player = state.get_role(RoleName.WITCH)
    if not witch_player:
        return

    witch_role = witch_player.role  # type: WitchRole

    # --- Heal potion ---
    if witch_role.heal_potion and result.killed_by_wolves:
        victim = result.killed_by_wolves
        use_heal = False

        if witch_player.is_human:
            print_secret(f"[WITCH] Tonight's victim: {victim.name}")
            print_secret(t("night_witch_save"))
            use_heal = input("> ").strip().lower() in ("y", "yes", "是")
        else:
            context = f"Tonight's wolf victim is {victim.name}. Use heal potion?"
            use_heal = witch_player.agent.decide_yes_no(context)

        if use_heal:
            result.saved_by_witch = True
            witch_role.heal_potion = False
            state.log(f"Witch saved {victim.name}")
            if witch_player.agent:
                witch_player.agent.add_memory(f"I used my heal potion to save {victim.name}")

    # --- Poison potion ---
    if witch_role.poison_potion:
        use_poison = False
        alive_others = [p for p in state.alive_players() if p != witch_player]

        if witch_player.is_human:
            print_secret(t("night_witch_poison"))
            use_poison = input("> ").strip().lower() in ("y", "yes", "是")
        else:
            use_poison = witch_player.agent.decide_yes_no("Should I use my poison potion tonight?")

        if use_poison:
            if witch_player.is_human:
                print_secret(t("night_witch_choose_target"))
                show_player_list(alive_others)
                target = prompt_player_choice(alive_others)
            else:
                target = witch_player.agent.choose_target(alive_others)

            result.poisoned_by_witch = target
            witch_role.poison_potion = False
            state.log(f"Witch poisoned {target.name}")
            if witch_player.agent:
                witch_player.agent.add_memory(f"I used my poison potion on {target.name}")


def _resolve_deaths(state: GameState, result: NightResult):
    """Compute who actually dies after heals / poison."""
    deaths = []

    if result.killed_by_wolves and not result.saved_by_witch:
        deaths.append(result.killed_by_wolves)

    if result.poisoned_by_witch:
        deaths.append(result.poisoned_by_witch)

    result.actually_died = deaths
```

---

## ✅ Acceptance Criteria

1. Night phase runs in correct order: wolves → seer → witch
2. Human wolf gets secret prompt, AI wolf auto-decides
3. Seer reveal is only shown to the Seer (secret from others)
4. Healing a wolf victim prevents them dying
5. Witch can't use same potion twice
6. `result.actually_died` contains the correct final list

---

## 📚 Kid Learning Moment 🐣
> **What is `None` in Python?**
> `None` means "nothing" or "empty". If there's no Seer in the game, `state.get_role(SEER)` returns `None`.
> We always check `if seer:` before using it — just like checking if a box is empty before opening it! 📦
