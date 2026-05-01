# 🎯 Number Guessing Game

> A feature-rich, colorized CLI number guessing game built in Python — with leaderboards, timed mode, smart hints, progressive difficulty, and full session statistics.

---

## 📖 Table of Contents

- [Project Description](#-project-description)
- [Versions](#-versions)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [How to Run](#-how-to-run)
- [CLI Flags](#-cli-flags)
- [Gameplay Walkthrough](#-gameplay-walkthrough)
- [Difficulty Levels](#-difficulty-levels)
- [Hot / Cold Feedback System](#-hot--cold-feedback-system)
- [Hint System](#-hint-system)
- [Leaderboard](#-leaderboard)
- [Session Statistics](#-session-statistics)
- [Progressive Difficulty](#-progressive-difficulty)
- [Timed Mode](#-timed-mode)
- [Data Persistence](#-data-persistence)
- [Code Architecture](#-code-architecture)
- [Version Comparison](#-version-comparison)
- [Example Output](#-example-output)

---

## 📝 Project Description

**Number Guessing Game** is a terminal-based Python game where the computer secretly picks a random number and the player tries to guess it within a limited number of attempts. What starts as a simple concept is expanded into a fully featured CLI experience — with color-coded feedback, a 6-tier hot/cold proximity system, smart contextual hints, a persistent top-5 leaderboard per difficulty, win streaks, progressive difficulty scaling, optional per-guess countdown timers, and a full session summary at the end.

The project was built in two iterations:

- **v1** — Core gameplay: random number, three difficulty presets, basic hints, simple high score per difficulty, play-again loop.
- **v2** — Full-featured rewrite with colorama colors, hot/cold feedback, guess history display, top-5 leaderboard with player names, win streaks, session stats, custom difficulty, progressive difficulty, timed mode, and CLI flag support.

The game is ideal for learning Python CLI patterns, `argparse`, `threading` for timed input, `json` for data persistence, and terminal color output with `colorama`.

---

## 🗂 Versions

| File | Description |
|---|---|
| `number_guessing_game.py` | v1 — Core game, basic hints, simple best-score tracking |
| `number_guessing_game_v2.py` | v2 — Full-featured with colors, leaderboard, timed mode, streaks |

---

## ✨ Features

### Core (v1 & v2)
- Computer randomly selects a secret number within a configurable range
- Player selects a difficulty level that controls the number of allowed guesses
- After each wrong guess: told whether the secret is **greater** or **less** than the guess
- Win message shows the number of attempts taken
- Lose message reveals the secret number
- Play-again loop after each round

### v2 Exclusive Features
- **🎨 Colorized output** — green for wins, red for errors/losses, yellow for hints, cyan for prompts
- **🔥 Hot/Cold proximity system** — 6-tier feedback from `🔥🔥 SCORCHING` to `🧊 Freezing`
- **📋 Guess history** — all previous guesses shown sorted before each new attempt, along with the known valid range
- **💡 Smart hint system** — unlocks after 2 failed guesses; reveals parity, divisibility, narrowed range, and proximity
- **🏆 Top-5 leaderboard** — persisted to disk, ranked per difficulty by fewest attempts then fastest time, with player name, date, and medal icons
- **🔥 Win streaks** — tracks current streak and all-time best streak across sessions
- **📊 Session summary** — rounds played, wins, losses, win rate %, average attempts, streaks
- **📈 Progressive difficulty** — number range grows by 50 after each win, rewarding experienced players
- **⚙️ Custom difficulty** — define your own number range (10–1000) and attempt count (1–20)
- **⏱ Timed mode** — optional 10-second countdown per guess via `--timed` flag
- **🖥 CLI flags** — launch directly into a difficulty or enable timed mode without navigating menus

---

## 📁 Project Structure

```
number-guessing-game/
│
├── number_guessing_game.py       # v1 — original game
├── number_guessing_game_v2.py    # v2 — full-featured game
│
├── high_scores.json              # v1 score storage (auto-created on first win)
├── scores_v2.json                # v2 leaderboard + streaks storage (auto-created)
│
└── README.md                     # This file
```

> `high_scores.json` and `scores_v2.json` are created automatically the first time a score is recorded. You can safely delete them to reset all scores.

---

## ⚙️ Requirements

| Requirement | Version |
|---|---|
| Python | 3.10 or higher |
| colorama | 0.4.6 or higher |

> **Python 3.10+** is required for the `str | None` union type hint syntax used in v2. If you're on an older Python, replace `str | None` with `Optional[str]` from the `typing` module.

---

## 📦 Installation

**1. Clone or download the project**

```bash
git clone https://github.com/your-username/number-guessing-game.git
cd number-guessing-game
```

Or simply download the `.py` files directly.

**2. Install the dependency**

```bash
pip install colorama
```

> `colorama` is only required for **v2**. v1 has no external dependencies. If `colorama` is not installed, v2 will still run — it falls back to plain text output automatically.

---

## ▶️ How to Run

**Run v1 (original):**
```bash
python3 number_guessing_game.py
```

**Run v2 (full-featured):**
```bash
python3 number_guessing_game_v2.py
```

On Windows you can also use:
```bash
python number_guessing_game_v2.py
```

---

## 🚩 CLI Flags

v2 supports command-line arguments to skip menus and configure the game from the terminal:

| Flag | Values | Description |
|---|---|---|
| `--difficulty` | `easy` `medium` `hard` `custom` | Start directly at this difficulty, skipping the menu |
| `--range N` | Integer (10–1000) | Override the upper bound of the number range |
| `--timed` | *(boolean flag)* | Enable timed mode — 10 seconds per guess |

**Examples:**

```bash
# Jump straight into Hard mode
python3 number_guessing_game_v2.py --difficulty hard

# Medium difficulty with a larger range of 1–500
python3 number_guessing_game_v2.py --difficulty medium --range 500

# Easy mode with timed guesses (10s per guess)
python3 number_guessing_game_v2.py --difficulty easy --timed

# Custom difficulty (interactive) with timed guesses
python3 number_guessing_game_v2.py --difficulty custom --timed

# Hard + custom range + timed — the ultimate challenge
python3 number_guessing_game_v2.py --difficulty hard --range 200 --timed
```

---

## 🎮 Gameplay Walkthrough

1. **Launch the game** — the ASCII banner and leaderboard are displayed.
2. **Select difficulty** — choose Easy, Medium, Hard, or Custom (or pass `--difficulty` to skip).
3. **Start guessing** — type a number within the valid range and press Enter.
4. **Read the feedback:**
   - Told whether the secret is greater or less than your guess
   - A hot/cold proximity emoji tells you how close you are
   - All previous guesses are shown sorted before each attempt
5. **Request a hint** — available from attempt 3 onwards (after 2 wrong guesses).
6. **Win or lose:**
   - **Win** → congratulations message, time taken, option to add score to leaderboard
   - **Lose** → the secret number is revealed
7. **Play again** — prompted after every round.
8. **Session summary** — shown when you quit: win rate, average attempts, streaks.

---

## 🎚 Difficulty Levels

| Level | Attempts | Default Range | How to Select |
|---|---|---|---|
| Easy | 10 | 1 – 100 | Menu option 1 or `--difficulty easy` |
| Medium | 5 | 1 – 100 | Menu option 2 or `--difficulty medium` |
| Hard | 3 | 1 – 100 | Menu option 3 or `--difficulty hard` |
| Custom | 1–20 (your choice) | 10–1000 (your choice) | Menu option 4 or `--difficulty custom` |

> In **progressive mode**, the range increases by 50 after each win (e.g., Easy starts at 1–100, then 1–150, then 1–200, etc.) regardless of the base difficulty.

---

## 🔥 Hot / Cold Feedback System

After every wrong guess, a proximity indicator tells you how close you are relative to the total range:

| Indicator | Threshold (% of range) | Meaning |
|---|---|---|
| 🔥🔥 SCORCHING | ≤ 3% away | You're basically on it |
| 🔥 Burning hot | ≤ 8% away | Very close |
| ☀️ Warm | ≤ 15% away | Getting there |
| 🌤️ Lukewarm | ≤ 30% away | Middling |
| ❄️ Cold | ≤ 50% away | Far off |
| 🧊 Freezing | > 50% away | Way off |

The threshold is calculated as a **percentage of the current range**, so it adapts correctly to both 1–100 and 1–500 ranges.

---

## 💡 Hint System

Hints are **not available on the first two attempts** — this keeps the early game challenging. From attempt 3 onwards, you are offered a hint before each guess.

A hint reveals up to four pieces of information:

1. **Parity** — whether the secret number is even or odd
2. **Divisibility** — whether it is divisible by 3, 5, or 7 (whichever applies first)
3. **Narrowed range** — the tightest lower and upper bound derived from all previous guesses
4. **Proximity** — the hot/cold rating based on your most recent guess

---

## 🏆 Leaderboard

The leaderboard is stored in `scores_v2.json` and persists between sessions.

- **Top 5 entries** are kept per difficulty level (Easy, Medium, Hard, Custom)
- Entries are ranked by **fewest attempts first**, then **fastest time** as a tiebreaker
- Each entry records: player name/initials, attempts, time taken, number range, and date
- 🥇🥈🥉 medals are shown for the top 3 positions
- After every round — win or lose — the full leaderboard is displayed

**Leaderboard entry fields:**

| Field | Description |
|---|---|
| Name | Player name or initials (1–10 characters) |
| Attempts | Number of guesses made |
| Time | Total seconds from round start to correct guess |
| Range | The upper bound of the number range that round |
| Date | Timestamp the score was recorded |

---

## 📊 Session Statistics

Displayed at the end of each session (when you choose not to play again):

| Stat | Description |
|---|---|
| Rounds played | Total number of rounds in this session |
| Wins / Losses | Count of each |
| Win rate | Wins as a percentage of rounds played |
| Avg attempts | Average guesses per round (including losses) |
| Win streak | Current streak and all-time best streak |

> The **all-time best streak** persists across sessions via `scores_v2.json`.

---

## 📈 Progressive Difficulty

After **each win**, the number range automatically increases by **50** for the next round:

| Win # | Range |
|---|---|
| Starting range | 1 – 100 |
| After 1st win | 1 – 150 |
| After 2nd win | 1 – 200 |
| After 3rd win | 1 – 250 |
| … | … |

This keeps experienced players challenged without them having to manually bump the difficulty. The game announces the upcoming range after each win.

> Progressive offsets **reset to zero** when you quit and start a new session.

---

## ⏱ Timed Mode

Enable with the `--timed` flag. In timed mode:

- You have **10 seconds** per guess
- A warning is printed before each guess prompt reminding you of the countdown
- If you don't enter a valid number within 10 seconds, the attempt is **skipped** (counts as a used attempt)
- The timer is implemented using a **background thread** (`threading.Event`) so it works cross-platform without requiring Unix-only `signal.alarm`

```bash
python3 number_guessing_game_v2.py --timed
```

---

## 💾 Data Persistence

All scores and streaks are saved to JSON files in the **same directory as the script**.

**`scores_v2.json` structure:**
```json
{
  "leaderboard": [
    {
      "name": "Alice",
      "difficulty": "Hard",
      "attempts": 2,
      "time": 8.4,
      "range": 100,
      "date": "2025-05-01 14:32"
    }
  ],
  "session_totals": {
    "rounds": 12,
    "wins": 9,
    "total_attempts": 47
  },
  "streaks": {
    "current": 3,
    "best": 5
  }
}
```

To **reset all scores**, simply delete `scores_v2.json`. It will be recreated fresh on the next run.

---

## 🏗 Code Architecture

v2 is organized into clearly separated functional sections within a single file:

| Section | Functions | Responsibility |
|---|---|---|
| Color helpers | `red()`, `green()`, `yellow()`, `cyan()`, `magenta()`, `dim()`, `bold()` | Wrap strings in colorama escape codes |
| Data layer | `load_data()`, `save_data()`, `add_leaderboard_entry()` | JSON read/write for leaderboard and streaks |
| Display | `display_leaderboard()`, `display_session_stats()` | Render leaderboard table and session summary |
| Feedback | `hot_cold()` | Compute 6-tier proximity label |
| History | `show_history()` | Display sorted previous guesses and known bounds |
| Hints | `get_hint()` | Build multi-clue hint string |
| Timed input | `TimedInput` class | Background-thread countdown input wrapper |
| Input helpers | `ask_int()`, `ask_yn()`, `ask_name()` | Validated input with error messages |
| Difficulty | `choose_difficulty()` | Menu + CLI flag resolution |
| Game loop | `play_round()` | Single round lifecycle |
| Entry point | `parse_args()`, `main()` | CLI argument parsing and outer game loop |

---

## 📊 Version Comparison

| Feature | v1 | v2 |
|---|---|---|
| Random number generation | ✅ | ✅ |
| Greater / less feedback | ✅ | ✅ |
| Easy / Medium / Hard presets | ✅ | ✅ |
| Basic hint system | ✅ (every attempt) | ✅ (after 2 wrong guesses) |
| Play-again loop | ✅ | ✅ |
| Per-round elapsed timer | ✅ | ✅ |
| Colorized output | ❌ | ✅ colorama |
| Hot/cold proximity feedback | ❌ | ✅ 6-tier emoji scale |
| Guess history display | ❌ | ✅ sorted + known range |
| Top-5 leaderboard with names | ❌ | ✅ per difficulty, persisted |
| Win streaks | ❌ | ✅ current + all-time best |
| Session summary stats | ❌ | ✅ win rate, avg, streaks |
| Progressive difficulty | ❌ | ✅ +50 range per win |
| Custom difficulty mode | ❌ | ✅ custom range + attempts |
| Per-guess countdown timer | ❌ | ✅ `--timed` flag |
| CLI argument flags | ❌ | ✅ `--difficulty` `--range` `--timed` |
| Graceful colorama fallback | ❌ | ✅ plain text if not installed |

---

## 🖥 Example Output

```
  ███╗   ██╗██╗   ██╗███╗   ███╗██████╗ ███████╗██████╗
  ...
  NUMBER GUESS GAME v2

  ──────────────────────────────────────────────────────
  Welcome! Guess the secret number — beat the leaderboard.
  ──────────────────────────────────────────────────────

  🏆  LEADERBOARD  (top 5 per difficulty)
  ──────────────────────────────────────────────────────
  Hard
  #   Name       Attempts   Time       Range      Date
  --- ---------- ---------- ---------- ---------- ----------------
  🥇1  Alice      2          8.4s       1-100      2025-05-01 14:32
  🥈2  Bob        3          12.1s      1-100      2025-05-01 14:45

  ──────────────────────────────────────────────────────
  Select difficulty:
  1. Easy    — 10 attempts, range 1-100
  2. Medium  —  5 attempts, range 1-100
  3. Hard    —  3 attempts, range 1-100
  4. Custom  — you choose the range & attempts
  ──────────────────────────────────────────────────────
  Your choice (1-4): 2

  ══════════════════════════════════════════════════════
  ▶ Difficulty : Medium
  ▶ Range      : 1 – 100
  ▶ Attempts   : 5
  ══════════════════════════════════════════════════════

  Attempt 1/5  | remaining: 5 | elapsed: 0.0s
  Your guess (1-100): 50

  ✗  Wrong — the number is greater than 50  ⬆
  ☀️   Warm — getting closer.

  Attempt 2/5  | remaining: 4 | elapsed: 3.2s

  Previous guesses (sorted): [50]
  Known range: ↑ above 50
  Your guess (1-100): 75

  ✗  Wrong — the number is less than 75  ⬇
  🌤️   Lukewarm.

  Attempt 3/5  | remaining: 3 | elapsed: 6.8s

  Previous guesses (sorted): [50, 75]
  Known range: ↑ above 50 and ↓ below 75
  Want a hint? (y/n): y

  💡 Hint:
     • The number is odd.
     • It lies between 50 and 75.
     • 🌤️   Lukewarm.

  Your guess (1-100): 63

  🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉
  ✅  CORRECT! You nailed it in 3 attempt(s)!
  🕒  Time: 14.3s
  🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉

  🔥 Win streak: 1  (best: 1)
  Add your score to the leaderboard? (y/n): y
  Enter your name/initials (max 10 chars): Alice
  🏆 You made the leaderboard, Alice!

  Play again? (y/n): n

  ──────────────────────────────────────────────────────
  📊  SESSION SUMMARY
  ──────────────────────────────────────────────────────
  Rounds played  : 1
  Wins           : 1  |  Losses: 0
  Win rate       : 100.0%
  Avg attempts   : 3.0
  Win streak     : current 1  |  best 1
  ──────────────────────────────────────────────────────

  Thanks for playing — see you next time! 👋
```

---

## 📄 License

This project is open source and free to use, modify, and distribute.#   N u m b e r _ G e s s i n g _ G a m e 
 
https://roadmap.sh/projects/unit-converter
 
