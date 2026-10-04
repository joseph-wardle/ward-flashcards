"""Build an Anki deck of your ward members' photos and names from the church directory."""

from getpass import getpass
from pathlib import Path

from deck import write_deck
from directory import scrape_households
from members import load_households, save_households

DECK_FILE = Path("members.apkg")
HOUSEHOLDS_PER_BATCH = 50  # Scrape in batches to avoid hitting rate limits.


def main() -> None:
    username = input("Username: ")
    password = getpass("Password: ")
    deck_name = input("Deck name [Ward Members]: ").strip() or "Ward Members"
    households = load_households()

    while True:
        scraped = 0
        batch = scrape_households(
            username, password, skip=set(households), limit=HOUSEHOLDS_PER_BATCH
        )
        for household_id, household_members in batch:
            households[household_id] = household_members
            save_households(households)  # After every household, so a crash loses little.
            scraped += 1

        members = [member for household in households.values() for member in household]
        write_deck(deck_name, members, DECK_FILE)
        print(f"Saved {len(members)} cards from {len(households)} households to {DECK_FILE}.")

        if scraped < HOUSEHOLDS_PER_BATCH:
            print("Every household in the directory has been scraped.")
            return
        if input("Scrape the next batch? [Y/n] ").strip().lower() not in ("", "y", "yes"):
            return


if __name__ == "__main__":
    main()
