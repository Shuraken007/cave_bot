curl -sSL https://install.python-poetry.org | python
p=~/.local/bin/poetry
$p install --no-root
cd ~
$p run alembic upgrade head
$p run pytest -n auto
$p run python -m src.scripts.start