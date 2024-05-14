curl -sSL https://install.python-poetry.org | python
~/.local/bin/poetry install --no-root
cd ~
~/.local/bin/poetry run alembic upgrade head
~/.local/bin/poetry run pytest -n auto
~/.local/bin/poetry run python -m src.scripts.start