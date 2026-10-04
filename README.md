# ward-flashcards

Generate an Anki deck of your ward members' photos and names from the church directory.

## Setup

```sh
uv sync
uv run playwright install chromium
```

## Usage

```sh
uv run main.py
```

It asks for a deck name, then opens a browser window. Sign in to your church account there
(two-factor works too; your password never touches this script). The sign-in is remembered
in `data/sign_in.json`, so later runs usually skip it; delete that file to sign out. It then scrapes every
household, pausing for a minute after every 50 to avoid rate limits, and writes
`members.apkg` for you to import into Anki.

Progress is saved to `data/` after every household. Press Ctrl-C at any time to stop: it
still writes the deck with what it has, and the next run picks up where it left off.
Run it again whenever the ward changes: it adds people who moved in and drops those who left
(and their photos). Households already saved aren't re-scraped, so to pick up new photos or
name changes, delete `data/households.json` and `data/photos/` and run it again.

## Files

- `main.py`: the run: sync saved households with the directory, then write the deck
- `directory.py`: opens the browser for sign-in and scrapes names and photos (the site's CSS selectors are at the top)
- `members.py`: the `Member` type and the on-disk cache in `data/`
- `deck.py`: card layout and writing the `.apkg`
