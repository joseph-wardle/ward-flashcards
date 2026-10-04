"""Build an Anki deck of your ward members' photos and names from the church directory."""

import time
from pathlib import Path

from deck import write_deck
from directory import list_households, open_directory, scrape_household
from members import Member, delete_unused_photos, load_households, save_households

DECK_FILE = Path("members.apkg")
BATCH_SIZE = 50  # Pause after this many households to avoid hitting rate limits.
PAUSE_SECONDS = 60


def main() -> None:
    deck_name = input("Deck name [Ward Members]: ").strip() or "Ward Members"
    households = load_households()
    try:
        update_households(households)
    except KeyboardInterrupt:
        print("\nStopped early. Progress is saved; run again to pick up where you left off.")

    members = [member for household in households.values() for member in household]
    write_deck(deck_name, members, DECK_FILE)
    print(f"Saved {len(members)} cards from {len(households)} households to {DECK_FILE}.")


def update_households(households: dict[str, list[Member]]) -> None:
    """Match the saved households to the directory: drop ones that left, scrape new ones."""
    with open_directory() as page:
        household_links = list_households(page)

        moved_out = households.keys() - household_links.keys()
        for household_id in moved_out:
            del households[household_id]
        save_households(households)
        delete_unused_photos(households)

        new_ids = [h for h in household_links if h not in households]
        print(f"Found {len(household_links)} households; {len(new_ids)} new to scrape.")
        if moved_out:
            print(f"Removed {len(moved_out)} saved households no longer in the directory.")
        for done, household_id in enumerate(new_ids):
            if done and done % BATCH_SIZE == 0:
                print(f"Scraped {done}/{len(new_ids)}. Pausing {PAUSE_SECONDS}s (Ctrl-C to stop).")
                time.sleep(PAUSE_SECONDS)
            households[household_id] = scrape_household(page, household_links[household_id])
            save_households(households)  # After every household, so a crash loses little.


if __name__ == "__main__":
    main()
