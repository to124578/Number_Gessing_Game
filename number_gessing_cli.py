#!/usr/bin/env python3

import random
import time
import json
import os

# ── High-score persistence ──────────────────────────────────────────────────
SCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "high_scores.json")

def load_scores() -> dict:
    if os.path.exists(SCORE_FILE):
        with open(SCORE_FILE) as f:
            return json.load(f)
    return {"Easy": None, "Medium": None, "Hard": None}

def save_scores(scores: dict) -> None:
    with open(SCORE_FILE, "w") as f:
        json.dump(scores, f, indent=2)

def update_score(scores: dict, difficulty: str, attempts: int) -> bool:
    """Returns True if a new high score was set."""
    current = scores.get(difficulty)
    if current is None or attempts < current:
        scores[difficulty] = attempts
        save_scores(scores)
        return True
    return False

def display_scores(scores: dict) -> None:
    print("\n┌─────────────────────────────────┐")
    print("│          🏆 HIGH SCORES          │")
    print("├──────────────┬──────────────────┤")
    print("│  Difficulty  │  Fewest Attempts │")
    print("├──────────────┼──────────────────┤")
    for level in ("Easy", "Medium", "Hard"):
        val = scores[level]
        score_str = str(val) if val is not None else "—"
        print(f"│  {level:<12}│  {score_str:<16}│")
    print("└──────────────┴──────────────────┘")

# ── Hint system ─────────────────────────────────────────────────────────────
def get_hint(secret: int, guesses: list[int]) -> str:
    hints = []

    # Parity hint
    parity = "even" if secret % 2 == 0 else "odd"
    hints.append(f"The number is {parity}.")

    # Divisibility hint
    for divisor in (3, 5, 7):
        if secret % divisor == 0:
            hints.append(f"The number is divisible by {divisor}.")
            break

    # Range narrowing based on previous guesses
    low  = max((g for g in guesses if g < secret), default=1)
    high = min((g for g in guesses if g > secret), default=100)
    hints.append(f"The number is between {low} and {high}.")

    # Proximity hint based on the most recent guess
    if guesses:
        diff = abs(guesses[-1] - secret)
        if diff <= 5:
            proximity = "very close 🔥"
        elif diff <= 15:
            proximity = "close 🌡️"
        else:
            proximity = "far away ❄️"
        hints.append(f"Your last guess was {proximity}.")

    return "\n  • ".join(["💡 Hint:"] + hints)

# ── Display helpers ──────────────────────────────────────────────────────────
BANNER = r"""
  _   _                 _                   ____
 | \ | |_   _ _ __ ___ | |__   ___ _ __   / ___|_   _  ___  ___ ___
 |  \| | | | | '_ ` _ \| '_ \ / _ \ '__| | |  _| | | |/ _ \/ __/ __|
 | |\  | |_| | | | | | | |_) |  __/ |    | |_| | |_| |  __/\__ \__ \
 |_| \_|\__,_|_| |_| |_|_.__/ \___|_|     \____|\__,_|\___||___/___/
"""

DIFFICULTY = {
    "1": ("Easy",   10),
    "2": ("Medium",  5),
    "3": ("Hard",    3),
}

def separator(char="─", width=60) -> str:
    return char * width

def fmt_time(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    m, s = divmod(int(seconds), 60)
    return f"{m}m {s}s"

# ── Core game loop ───────────────────────────────────────────────────────────
def play_round(scores: dict) -> None:
    secret = random.randint(1, 100)
    guesses: list[int] = []

    # Difficulty selection
    print(f"\n{separator()}")
    print("Please select the difficulty level:")
    print("  1. Easy   (10 chances)")
    print("  2. Medium  (5 chances)")
    print("  3. Hard    (3 chances)")
    print(f"{separator()}")

    while True:
        choice = input("Enter your choice (1/2/3): ").strip()
        if choice in DIFFICULTY:
            level, max_attempts = DIFFICULTY[choice]
            break
        print("  ⚠️  Invalid choice. Please enter 1, 2, or 3.")

    print(f"\n✅ Great! You selected {level} difficulty.")
    print(f"   You have {max_attempts} chances. Let's go!\n")
    print(separator())

    start_time = time.time()

    for attempt in range(1, max_attempts + 1):
        remaining = max_attempts - attempt + 1
        print(f"\n[Attempt {attempt}/{max_attempts}  |  Remaining: {remaining}]")

        # Optional hint after the first wrong guess
        if attempt > 1:
            want_hint = input("Would you like a hint? (y/n): ").strip().lower()
            if want_hint == "y":
                print(f"\n  {get_hint(secret, guesses)}\n")

        # Get a valid integer guess
        while True:
            raw = input("Enter your guess (1-100): ").strip()
            try:
                guess = int(raw)
                if 1 <= guess <= 100:
                    break
                print("  ⚠️  Please enter a number between 1 and 100.")
            except ValueError:
                print("  ⚠️  That doesn't look like a number. Try again.")

        guesses.append(guess)
        elapsed = time.time() - start_time

        if guess == secret:
            print(f"\n{'🎉' * 20}")
            print(f"  Congratulations! You guessed it in {attempt} attempt(s)!")
            print(f"  The number was {secret}.")
            print(f"  Time taken: {fmt_time(elapsed)}")
            if update_score(scores, level, attempt):
                print(f"  🏆 New high score for {level} difficulty!")
            print(f"{'🎉' * 20}\n")
            return

        direction = "greater" if secret > guess else "less"
        print(f"  ❌ Incorrect! The number is {direction} than {guess}.")
        print(f"     Time elapsed: {fmt_time(elapsed)}")

    # Out of chances
    print(f"\n{'😢' * 20}")
    print(f"  You've run out of chances! The number was {secret}.")
    print(f"{'😢' * 20}\n")

# ── Entry point ──────────────────────────────────────────────────────────────
def main() -> None:
    print(BANNER)
    print("  Welcome to the Number Guessing Game!")
    print("  I'm thinking of a number between 1 and 100.")
    print("  Pick a difficulty, make your guesses, and good luck!\n")

    scores = load_scores()
    display_scores(scores)

    while True:
        play_round(scores)
        display_scores(scores)

        again = input("\nWould you like to play again? (y/n): ").strip().lower()
        if again != "y":
            print("\nThanks for playing! See you next time. 👋\n")
            break

if __name__ == "__main__":
    main()