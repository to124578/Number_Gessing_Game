#!/usr/bin/env python3
"""
Number Guessing Game — v2
Run:  python3 number_guessing_game_v2.py
Flags: --difficulty easy|medium|hard|custom  --range 200  --timed
"""

import argparse
import json
import os
import random
import threading
import time
from datetime import datetime

# ── Colorama ────────────────────────────────────────────────────────────────
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    # Graceful fallback — no colors
    class _Dummy:
        def __getattr__(self, _): return ""
    Fore = Style = _Dummy()

# ── Colour helpers ───────────────────────────────────────────────────────────
def red(s):    return f"{Fore.RED}{Style.BRIGHT}{s}{Style.RESET_ALL}"
def green(s):  return f"{Fore.GREEN}{Style.BRIGHT}{s}{Style.RESET_ALL}"
def yellow(s): return f"{Fore.YELLOW}{Style.BRIGHT}{s}{Style.RESET_ALL}"
def cyan(s):   return f"{Fore.CYAN}{Style.BRIGHT}{s}{Style.RESET_ALL}"
def magenta(s):return f"{Fore.MAGENTA}{Style.BRIGHT}{s}{Style.RESET_ALL}"
def dim(s):    return f"{Style.DIM}{s}{Style.RESET_ALL}"
def bold(s):   return f"{Style.BRIGHT}{s}{Style.RESET_ALL}"

def sep(char="─", width=62):
    return dim(char * width)

# ── Constants ────────────────────────────────────────────────────────────────
SCORE_FILE  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scores_v2.json")
TOP_N       = 5          # leaderboard size
GUESS_LIMIT = 10         # seconds per guess in timed mode

PRESETS = {
    "easy":   {"label": "Easy",   "attempts": 10, "range": 100},
    "medium": {"label": "Medium", "attempts": 5,  "range": 100},
    "hard":   {"label": "Hard",   "attempts": 3,  "range": 100},
}

BANNER = f"""
{Fore.CYAN}{Style.BRIGHT}
  ███╗   ██╗██╗   ██╗███╗   ███╗██████╗ ███████╗██████╗
  ████╗  ██║██║   ██║████╗ ████║██╔══██╗██╔════╝██╔══██╗
  ██╔██╗ ██║██║   ██║██╔████╔██║██████╔╝█████╗  ██████╔╝
  ██║╚██╗██║██║   ██║██║╚██╔╝██║██╔══██╗██╔══╝  ██╔══██╗
  ██║ ╚████║╚██████╔╝██║ ╚═╝ ██║██████╔╝███████╗██║  ██║
  ╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝
       ██████╗ ██╗   ██╗███████╗███████╗███████╗
      ██╔════╝ ██║   ██║██╔════╝██╔════╝██╔════╝
      ██║  ███╗██║   ██║█████╗  ███████╗███████╗
      ██║   ██║██║   ██║██╔══╝  ╚════██║╚════██║
      ╚██████╔╝╚██████╔╝███████╗███████║███████║
       ╚═════╝  ╚═════╝ ╚══════╝╚══════╝╚══════╝
         ██████╗  █████╗ ███╗   ███╗███████╗
        ██╔════╝ ██╔══██╗████╗ ████║██╔════╝
        ██║  ███╗███████║██╔████╔██║█████╗
        ██║   ██║██╔══██║██║╚██╔╝██║██╔══╝
        ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗
         ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝  v2
{Style.RESET_ALL}"""

# ── Leaderboard / score persistence ─────────────────────────────────────────
def load_data() -> dict:
    if os.path.exists(SCORE_FILE):
        with open(SCORE_FILE) as f:
            return json.load(f)
    return {
        "leaderboard": [],          # list of entry dicts
        "session_totals": {"rounds": 0, "wins": 0, "total_attempts": 0},
        "streaks": {"current": 0, "best": 0},
    }

def save_data(data: dict) -> None:
    with open(SCORE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_leaderboard_entry(data: dict, name: str, difficulty: str,
                          attempts: int, elapsed: float, num_range: int) -> bool:
    """Insert entry, keep top-N per difficulty. Returns True if it made the board."""
    entry = {
        "name": name,
        "difficulty": difficulty,
        "attempts": attempts,
        "time": round(elapsed, 1),
        "range": num_range,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    board: list = data["leaderboard"]
    board.append(entry)
    # Sort by attempts asc, then time asc
    board.sort(key=lambda e: (e["difficulty"], e["attempts"], e["time"]))

    # Prune: keep only TOP_N per difficulty label
    from collections import defaultdict
    counts: dict = defaultdict(int)
    pruned = []
    for e in board:
        if counts[e["difficulty"]] < TOP_N:
            pruned.append(e)
            counts[e["difficulty"]] += 1
    data["leaderboard"] = pruned
    save_data(data)
    return entry in pruned

def display_leaderboard(data: dict) -> None:
    board: list = data["leaderboard"]
    print(f"\n{sep()}")
    print(cyan("  🏆  LEADERBOARD  (top 5 per difficulty)"))
    print(sep())
    if not board:
        print(dim("  No scores yet. Be the first!"))
        print(sep())
        return

    from collections import defaultdict
    by_diff: dict = defaultdict(list)
    for e in board:
        by_diff[e["difficulty"]].append(e)

    for diff in ("Easy", "Medium", "Hard", "Custom"):
        entries = by_diff.get(diff, [])
        if not entries:
            continue
        print(bold(f"\n  {diff}"))
        print(f"  {'#':<3} {'Name':<10} {'Attempts':<10} {'Time':<10} {'Range':<10} {'Date'}")
        print(f"  {'─'*3} {'─'*10} {'─'*10} {'─'*10} {'─'*10} {'─'*16}")
        for i, e in enumerate(entries, 1):
            medal = ("🥇", "🥈", "🥉", "  ", "  ")[i - 1]
            print(f"  {medal}{i:<2} {e['name']:<10} {e['attempts']:<10} "
                  f"{e['time']:<9.1f}s 1-{e['range']:<8} {e['date']}")
    print(sep())

# ── Session stats ────────────────────────────────────────────────────────────
def display_session_stats(data: dict, session: dict) -> None:
    wins   = session["wins"]
    rounds = session["rounds"]
    if rounds == 0:
        return
    win_rate = (wins / rounds) * 100
    avg_att  = session["total_attempts"] / rounds if rounds else 0
    print(f"\n{sep()}")
    print(cyan("  📊  SESSION SUMMARY"))
    print(sep())
    print(f"  Rounds played  : {bold(str(rounds))}")
    print(f"  Wins           : {green(str(wins))}  |  Losses: {red(str(rounds - wins))}")
    print(f"  Win rate       : {yellow(f'{win_rate:.1f}%')}")
    print(f"  Avg attempts   : {bold(f'{avg_att:.1f}')}")
    streaks = data["streaks"]
    print(f"  Win streak     : current {cyan(str(streaks['current']))}  |  best {magenta(str(streaks['best']))}")
    print(sep())

# ── Hot / Cold feedback ──────────────────────────────────────────────────────
def hot_cold(diff: int, num_range: int) -> str:
    pct = diff / num_range
    if pct <= 0.03:  return green("🔥🔥 SCORCHING!  You're basically on it!")
    if pct <= 0.08:  return green("🔥  Burning hot!")
    if pct <= 0.15:  return yellow("☀️   Warm — getting closer.")
    if pct <= 0.30:  return yellow("🌤️   Lukewarm.")
    if pct <= 0.50:  return cyan("❄️   Cold.")
    return cyan("🧊  Freezing — way off!")

# ── Guess history ────────────────────────────────────────────────────────────
def show_history(guesses: list[int], secret: int) -> None:
    if not guesses:
        return
    sorted_g = sorted(guesses)
    print(dim(f"\n  Previous guesses (sorted): {sorted_g}"))
    lo = max((g for g in guesses if g < secret), default=None)
    hi = min((g for g in guesses if g > secret), default=None)
    bounds = []
    if lo: bounds.append(green(f"↑ above {lo}"))
    if hi: bounds.append(red(f"↓ below {hi}"))
    if bounds:
        print(dim(f"  Known range: {' and '.join(bounds)}"))

# ── Smart hint system (unlocks after 2 wrong guesses) ───────────────────────
def get_hint(secret: int, guesses: list[int], num_range: int) -> str:
    lines = []
    parity = "even" if secret % 2 == 0 else "odd"
    lines.append(f"The number is {bold(parity)}.")
    for d in (3, 5, 7):
        if secret % d == 0:
            lines.append(f"It is divisible by {bold(str(d))}.")
            break
    lo = max((g for g in guesses if g < secret), default=1)
    hi = min((g for g in guesses if g > secret), default=num_range)
    lines.append(f"It lies between {bold(str(lo))} and {bold(str(hi))}.")
    if guesses:
        diff = abs(guesses[-1] - secret)
        lines.append(hot_cold(diff, num_range))
    return yellow("  💡 Hint:\n") + "\n".join(f"     • {l}" for l in lines)

# ── Timed input (cross-platform via thread) ──────────────────────────────────
class TimedInput:
    """Prompt the user with a countdown; returns None on timeout."""
    def __init__(self, timeout: int):
        self.timeout = timeout
        self._answer = None
        self._done   = threading.Event()

    def _reader(self, prompt: str) -> None:
        try:
            self._answer = input(prompt)
        except EOFError:
            pass
        finally:
            self._done.set()

    def ask(self, prompt: str) -> str | None:
        t = threading.Thread(target=self._reader, args=(prompt,), daemon=True)
        t.start()
        self._done.wait(self.timeout)
        if not self._done.is_set():
            print(red(f"\n  ⏰ Time's up! You took longer than {self.timeout}s."))
            return None
        return self._answer

# ── Input helpers ─────────────────────────────────────────────────────────────
def ask_int(prompt: str, lo: int, hi: int, timed: bool = False,
            timeout: int = GUESS_LIMIT) -> int | None:
    ti = TimedInput(timeout) if timed else None
    while True:
        raw = (ti.ask(prompt) if timed else input(prompt))
        if raw is None:
            return None       # timeout
        raw = raw.strip()
        try:
            val = int(raw)
            if lo <= val <= hi:
                return val
            print(red(f"  ⚠️  Enter a number between {lo} and {hi}."))
        except ValueError:
            print(red("  ⚠️  Please type a whole number."))

def ask_yn(prompt: str) -> bool:
    while True:
        r = input(prompt).strip().lower()
        if r in ("y", "yes"): return True
        if r in ("n", "no"):  return False
        print(red("  ⚠️  Please type y or n."))

def ask_name() -> str:
    while True:
        name = input(cyan("  Enter your name/initials (max 10 chars): ")).strip()
        if 1 <= len(name) <= 10:
            return name
        print(red("  ⚠️  Name must be 1–10 characters."))

# ── Difficulty setup ─────────────────────────────────────────────────────────
def choose_difficulty(cli_diff: str | None, cli_range: int | None) -> tuple[str, int, int]:
    """Returns (label, max_attempts, num_range)."""
    if cli_diff and cli_diff != "custom":
        p = PRESETS[cli_diff]
        r = cli_range or p["range"]
        return p["label"], p["attempts"], r

    print(f"\n{sep()}")
    print(bold("  Select difficulty:"))
    print(f"  {cyan('1')}. Easy    — 10 attempts, range 1-100")
    print(f"  {cyan('2')}. Medium  —  5 attempts, range 1-100")
    print(f"  {cyan('3')}. Hard    —  3 attempts, range 1-100")
    print(f"  {cyan('4')}. Custom  — you choose the range & attempts")
    print(sep())

    choice_map = {"1": "easy", "2": "medium", "3": "hard"}
    while True:
        ch = input("  Your choice (1-4): ").strip()
        if ch in choice_map:
            p = PRESETS[choice_map[ch]]
            r = cli_range or p["range"]
            return p["label"], p["attempts"], r
        if ch == "4":
            break
        print(red("  ⚠️  Enter 1, 2, 3, or 4."))

    # Custom
    print(yellow("\n  Custom mode — define your own game."))
    num_range = ask_int("  Max number in range (10-1000): ", 10, 1000)
    attempts  = ask_int("  Number of attempts (1-20): ", 1, 20)
    return "Custom", attempts, num_range

# ── Core round ───────────────────────────────────────────────────────────────
def play_round(data: dict, session: dict,
               cli_diff: str | None, cli_range: int | None,
               timed: bool, progressive_offset: int) -> bool:
    """Plays one round. Returns True if the player won."""

    label, max_attempts, base_range = choose_difficulty(cli_diff, cli_range)
    num_range = base_range + progressive_offset
    secret    = random.randint(1, num_range)
    guesses: list[int] = []

    print(f"\n{sep('═')}")
    print(f"  {green('▶')} Difficulty : {bold(label)}")
    print(f"  {green('▶')} Range      : {bold(f'1 – {num_range}')}")
    print(f"  {green('▶')} Attempts   : {bold(str(max_attempts))}")
    if timed:
        print(f"  {green('▶')} Timed mode : {yellow(f'{GUESS_LIMIT}s per guess')}")
    print(sep('═'))

    start = time.time()
    won   = False

    for attempt in range(1, max_attempts + 1):
        remaining = max_attempts - attempt + 1
        elapsed   = time.time() - start

        print(f"\n  {cyan(f'Attempt {attempt}/{max_attempts}')}  "
              f"{dim(f'| remaining: {remaining} | elapsed: {elapsed:.1f}s')}")

        # Guess history
        show_history(guesses, secret)

        # Smart hint — only available after ≥ 2 wrong guesses
        if len(guesses) >= 2:
            if ask_yn(yellow("  Want a hint? (y/n): ")):
                print(get_hint(secret, guesses, num_range))

        # Get guess
        if timed:
            print(dim(f"  ⏱  You have {GUESS_LIMIT} seconds to answer!"))
        prompt = f"  {bold('Your guess')} (1-{num_range}): "
        guess  = ask_int(prompt, 1, num_range, timed=timed, timeout=GUESS_LIMIT)

        if guess is None:         # timed-out
            continue

        guesses.append(guess)
        diff = abs(guess - secret)

        if guess == secret:
            elapsed = time.time() - start
            print(f"\n  {green('🎉' * 22)}")
            print(green(f"  ✅  CORRECT! You nailed it in {attempt} attempt(s)!"))
            print(green(f"  🕒  Time: {elapsed:.1f}s"))
            print(f"  {green('🎉' * 22)}\n")
            won = True
            break

        direction = "greater" if secret > guess else "less"
        arrow     = "⬆" if secret > guess else "⬇"
        print(f"\n  {red('✗')}  Wrong — the number is {bold(direction)} than "
              f"{bold(str(guess))}  {arrow}")
        print(f"  {hot_cold(diff, num_range)}")

    if not won:
        elapsed = time.time() - start
        print(f"\n  {'😞' * 22}")
        print(red(f"  ✗  Out of chances! The number was {bold(str(secret))}."))
        print(f"  {'😞' * 22}\n")

    # Update session
    session["rounds"] += 1
    session["total_attempts"] += len(guesses)
    streaks = data["streaks"]
    if won:
        session["wins"] += 1
        streaks["current"] += 1
        streaks["best"] = max(streaks["best"], streaks["current"])
        print(f"  🔥 Win streak: {cyan(str(streaks['current']))}  "
              f"(best: {magenta(str(streaks['best']))})")

        # Leaderboard
        if ask_yn(cyan("  Add your score to the leaderboard? (y/n): ")):
            name = ask_name()
            made_it = add_leaderboard_entry(
                data, name, label, len(guesses), elapsed, num_range
            )
            if made_it:
                print(green(f"  🏆 You made the leaderboard, {name}!"))
            else:
                print(dim("  Good game — didn't crack the top 5 this time."))
    else:
        streaks["current"] = 0
        save_data(data)

    # Update overall session totals in data
    data["session_totals"]["rounds"] += 1
    data["session_totals"]["wins"]   += 1 if won else 0
    data["session_totals"]["total_attempts"] += len(guesses)
    save_data(data)

    return won

# ── Main ─────────────────────────────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Number Guessing Game v2")
    p.add_argument("--difficulty", choices=["easy", "medium", "hard", "custom"],
                   help="Skip the menu and start with this difficulty.")
    p.add_argument("--range", type=int, metavar="N",
                   help="Override the upper bound of the number range.")
    p.add_argument("--timed", action="store_true",
                   help=f"Enable timed mode ({GUESS_LIMIT}s per guess).")
    return p.parse_args()

def main() -> None:
    args     = parse_args()
    data     = load_data()
    session  = {"rounds": 0, "wins": 0, "total_attempts": 0}
    prog_offset = 0   # grows after each win for progressive difficulty

    print(BANNER)
    print(f"  {'─'*60}")
    print(f"  Welcome! Guess the secret number — beat the leaderboard.")
    if args.timed:
        print(yellow(f"  ⏱  Timed mode active — {GUESS_LIMIT}s per guess!"))
    print(f"  {'─'*60}")

    display_leaderboard(data)

    while True:
        won = play_round(
            data, session,
            cli_diff=args.difficulty,
            cli_range=getattr(args, "range"),
            timed=args.timed,
            progressive_offset=prog_offset,
        )

        # Progressive difficulty — bump range by 50 after each win
        if won:
            prog_offset += 50
            if prog_offset > 0:
                print(yellow(f"\n  📈 Progressive mode: next range will be "
                             f"1–{100 + prog_offset}!"))

        display_leaderboard(data)

        if not ask_yn(cyan("\n  Play again? (y/n): ")):
            break

    display_session_stats(data, session)
    print(green("\n  Thanks for playing — see you next time! 👋\n"))

if __name__ == "__main__":
    main()