curl -sSL https://install.python-poetry.org | python
# poetry init
# apt-get install libpq-dev
poetry install
poetry run python3 -m src.scripts.start