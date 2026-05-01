# Falling Sand — CLI Edition

A terminal-based falling-sand simulator. Drop sand, water, fire, and more — watch them interact in real time.

## Requirements
- Python 3.8+
- Windows: requires `windows-curses`

## Install

**Linux / macOS:**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

> Tip: Use Windows Terminal or PowerShell for best results. Avoid the old cmd.exe — color support is limited.

## Controls

| Input           | Action                     |
|-----------------|----------------------------|
| Mouse drag      | Draw element               |
| Right drag      | Erase                      |
| 1–7             | Select element             |
| E / Shift+E     | Cycle elements             |
| `[` / `]`       | Decrease / increase brush  |
| P               | Pause / Resume             |
| R               | Reset canvas               |
| Q               | Quit                       |
| Arrow + Space   | Keyboard cursor (no mouse) |

## Elements

| Key | Element | Behaviour                        |
|-----|---------|----------------------------------|
| 1   | Sand    | Falls, piles, sinks in water     |
| 2   | Water   | Flows sideways, fills containers |
| 3   | Fire    | Spreads, burns wood, boils water |
| 4   | Wood    | Solid, flammable                 |
| 5   | Stone   | Inert wall                       |
| 6   | Smoke   | Rises, dissipates                |
| 7   | Steam   | Rises from water + fire          |

## Troubleshooting

**Colors not showing on Windows:** Use Windows Terminal (not cmd.exe).  
**Mouse not working:** Use keyboard mode — arrow keys + Space to draw.  
**UnicodeDecodeError on startup:** Run `chcp 65001` in cmd.exe before launching.  
**Small terminal:** Maximize your window — the grid fills available space automatically.
