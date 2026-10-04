generate an anki deck from your ward directory 

just clone the repo and run `uv sync` 
then activate the venv with `source .venv/bin/activate`
then run `playwright install chromium`
and finally you can run the flashcard generator with
`python main.py`

it will prompt for your church account username and password and a name for the generated deck.

It defaults to generating 50 cards at a time in hope of avoiding rate limits. It will prompt you to conitnue, just continue hitting enter until you've got cards generated for the whole ward.





