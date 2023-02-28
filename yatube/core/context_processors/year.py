import datetime as dt


def year(requests):
    """Добавляет переменную с текущим годом."""
    return {
        'year': int(dt.datetime.now().year),
    }
