import datetime as dt
from typing import Any


def year(requests: Any) -> dict[str, int]:
    """Добавляет переменную с текущим годом."""
    return {
        'year': int(dt.datetime.now().year),
    }
