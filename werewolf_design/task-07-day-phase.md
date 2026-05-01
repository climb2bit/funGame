# Task 07 — Day Phase

## 🎯 Goal
Implement the day phase: announce deaths, run player speeches (AI generates dialogue, human types), then hold a vote to eliminate a suspect.

---

## 📋 Deliverables

- [ ] `game/phases/day.py` — `run_day_phase(state, night_result)` function
- [ ] Death announcements (respecting Hunter's shoot ability)
- [ ] AI speech generation (role-appropriate, memory-informed)
- [ ] Human speech input
- [ ] Voting logic with tie handling

---

## 🔧 Day Phase Sequence

```
1. 🌅 Dawn announcement
2. 💀 Announce who died in the night
3. 🔫 Hunter shoots (if hunter died)
4. 🗣️  Discussion round (all alive players speak, human last)
5. 🗳️  Voting (all alive players vote)
6. ❌  Elimination (or no-kill on tie)
7. 🔫  Hunter shoots again (if hunter eliminated by vote)
```

---

## 🔧 Implementation Details

### `game/phases/day.py`
```python
from game.state import GameState, NightResult
from game.roles import RoleName
from game.player import Player
from i18n import t
from ui.display import (
    show_phase_banner, show_player_list, show_speech_bubble,
    print_info, print_warning, prompt_player_choice, pause
)

def run_day_phase(state: GameState, night_result: NightResult):
    """Full day phase: announce deaths, discuss, vote, eliminate."""

    show_phase_banner("day", state.language)

    # Step 1: Announce deaths
    _announce_deaths(state, night_result)

    # Step 2: Hunter may shoot if they died
    for dead in night_result.actually_died:
        if dead.role.name == RoleName.HUNTER:
            _hunter_shoot(state, dead)

    state.update_winner()
    if state.game_over:
        return

    # Step 3: Discussion round
    _discussion_round(state, night_result)

    # Step 4: Vote
    eliminated = _voting_round(state)

    # Step 5: Hunter may shoot if eliminated by vote
    if eliminated and eliminated.role.name == RoleName.HUNTER:
        _hunter_shoot(state, eliminated)

    state.update_winner()


def _announce_deaths(state: GameState, night_result: NightResult):
    """Kill the dead, announce to everyone."""
    if not night_result.actually_died:
        print_info(t("day_announce_nobody"))
    else:
        for victim in night_result.actually_died:
            state.kill_player(victim, "night death")
            print_info(t("day_announce_death", name=victim.name))
            # Inform all AI agents
            for p in state.players:
                if p.agent:
                    p.agent.add_memory(f"{victim.name} died during the night.")
    pause()


def _discussion_round(state: GameState, night_result: NightResult):
    """Each alive player speaks in order. Human speaks last."""
    alive = state.alive_players()
    human = state.human_player()

    # Build context string for AI agents
    deaths_context = ""
    if night_result.actually_died:
        names = ", ".join(p.name for p in night_result.actually_died)
        deaths_context = f"People who died last night: {names}."
    else:
        deaths_context = "Nobody died last night."

    # AI players speak first
    for player in alive:
        if player.is_human:
            continue
        context = (
            f"{deaths_context} It is now the discussion phase. "
            f"Give your thoughts on who might be the werewolf. "
            f"Remember: you are {player.name}."
        )
        speech = player.agent.generate_speech(context)
        show_speech_bubble(player.name, speech)
        # Let other AI agents "hear" this
        for other in alive:
            if other.agent and other != player:
                other.agent.add_memory(f"{player.name} said: \"{speech}\"")
        pause(short=True)

    # Human speaks last
    if human in alive:
        print_info(t("your_turn"))
        print_info(t("enter_speech"))
        human_speech = input("> ").strip()
        if human_speech:
            show_speech_bubble(human.name, human_speech)
            for p in alive:
                if p.agent:
                    p.agent.add_memory(f"{human.name} (human) said: \"{human_speech}\"")
    pause()


def _voting_round(state: GameState) -> Player | None:
    """
    All alive players vote to eliminate someone.
    Returns eliminated player or None (on tie).
    """
    alive = state.alive_players()
    human = state.human_player()
    votes = {}

    print_info(t("phase_vote"))

    # AI players vote
    for player in alive:
        if player.is_human:
            continue
        others = [p for p in alive if p != player]
        target = player.agent.choose_target(others)
        votes[player] = target
        print_info(f"  {player.name} → voted for {target.name}")

    # Human votes
    if human in alive:
        print_info(t("day_vote_prompt"))
        others = [p for p in alive if p != human]
        show_player_list(others)
        target = prompt_player_choice(others)
        votes[human] = target

    pause()

    # Tally
    eliminated = state.tally_votes(votes)

    if eliminated is None:
        print_info(t("day_no_consensus"))
        state.log("Vote tied — no elimination")
    else:
        state.kill_player(eliminated, "voted out")
        print_warning(t("day_vote_result", name=eliminated.name))
        # Reveal role after elimination
        role_name = t(f"role_{eliminated.role.name.value}")
        print_info(f"  → {eliminated.name} was a {role_name}!")
        for p in state.players:
            if p.agent:
                p.agent.add_memory(
                    f"{eliminated.name} was eliminated by vote. "
                    f"Their role was {eliminated.role.name.value}."
                )

    pause()
    return eliminated


def _hunter_shoot(state: GameState, hunter: Player):
    """Hunter takes one shot when dying."""
    alive_others = [p for p in state.alive_players() if p != hunter]
    if not alive_others:
        return

    print_warning(t("hunter_shoot", name=hunter.name))

    if hunter.is_human:
        show_player_list(alive_others)
        target = prompt_player_choice(alive_others)
    else:
        target = hunter.agent.choose_target(alive_others)

    state.kill_player(target, "shot by hunter")
    print_warning(f"💥 {hunter.name} shot {target.name}!")
    for p in state.players:
        if p.agent:
            p.agent.add_memory(f"Hunter {hunter.name} shot {target.name} when dying.")
    pause()
```

---

## ✅ Acceptance Criteria

1. Deaths are announced before discussion starts
2. AI generates unique speech each round (not identical for all players)
3. Human speech input is shown back in the same speech bubble format
4. Vote tally correctly identifies the most-voted player
5. Tie vote results in no elimination
6. Eliminated player's role is revealed after vote
7. Hunter shoot triggers correctly in both night-death and vote-death scenarios

---

## 📚 Kid Learning Moment 🐣
> **What is a `for` loop?**
> A `for` loop repeats code for each item in a list.
> `for player in alive:` means "do this once for Alice, once for Bob, once for Carol..."
> It's like handing out cards to each person at a table, one by one! 🃏
