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

It asks for your church account username, password, and a name for the deck, then opens a
browser, logs in, and scrapes the directory 50 households at a time to avoid rate limits.
After each batch it writes `members.apkg` and asks whether to continue. Press enter until
every household is done, then import `members.apkg` into Anki.

Progress is saved to `data/` after every household, so if a run stops, the next run picks up
where it left off. Running again later also adds anyone who has moved in. To start over
(for example, to drop people who moved out), delete the `data/` folder.

## Files

- `main.py`: prompts, batching, and the run loop
- `directory.py`: logs in and scrapes names and photos (the site's CSS selectors are at the top)
- `members.py`: the `Member` type and the on-disk cache in `data/`
- `deck.py`: card layout and writing the `.apkg`
