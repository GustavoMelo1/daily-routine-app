from datetime import datetime


def normalize_notebook_date(value):
    """Use the date written on the page, never the import date or an inferred year."""
    if not isinstance(value, str):
        return value
    text = value.strip()
    for pattern in ('%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y', '%d-%m-%Y'):
        try:
            return datetime.strptime(text, pattern).date().isoformat()
        except ValueError:
            continue
    return value
