from getpass import getpass
from pathlib import Path

from flashcard import create_deck
from member import get_member_data


def generate_deck(username: str, password: str, deck_name: str):
    member_data = get_member_data(username=username, password=password, use_lcr=False)
    print([member.name for member in member_data])
    create_deck(deck_name=deck_name, members=member_data, filepath=Path("members.apkg"))


def main():
    username = input("Username:")
    password = getpass("Password:")

    member_data = get_member_data(username=username, password=password, use_lcr=False)
    print([member.name for member in member_data])

    deck_name = input("Deck Name:")
    create_deck(deck_name=deck_name, members=member_data, filepath=Path("members.apkg"))

    continue_generating = True
    while continue_generating:
        prompt = input(
            f"Saved {len(member_data)} flashcards. Continue generating more? [Y/n]"
        )
        if prompt in ["y", "yes", "Y", "Yes", ""]:
            generate_deck(username=username, password=password, deck_name=deck_name)
        else:
            continue_generating = False


if __name__ == "__main__":
    main()
