curl -sSL https://install.python-poetry.org | python
~/.local/bin/poetry install --no-root
cd ~
~/.local/bin/poetry run python -m src.scripts.start