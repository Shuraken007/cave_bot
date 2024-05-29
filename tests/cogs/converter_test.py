import pytest

from cave_bot.bot.converter import ColorConverter, INVALID_COLOR_ERR_BOUND
from cave_bot.const import CellType as ct, UserRole as ur
from cave_bot.report import Report

converter = ColorConverter()

@pytest.fixture()
def report():
   report = Report()

def test_validate_color(report):
   pass