import pytest
from my_school_menus.msm_calendar import Calendar


def menu_data():
    return {'data': [
        {'setting': '{"current_display":[{"type":"recipe","name":"Chicken Nuggets","recipe_id":1}]}', 'day': '2025-11-05T00:00:00.000-05:00'}
    ]}


def test_events_missing_menu_data():
    cal = Calendar()
    with pytest.raises(ValueError):
        cal.events({'data': []})


def test_events():
    cal = Calendar()
    cal.events(menu_data())


def test_calendar():
    cal = Calendar()
    event_data = cal.events(menu_data())
    cal.calendar(event_data)


def test_ical():
    cal = Calendar()
    event_data = cal.events(menu_data())
    icalendar_calendar = cal.calendar(event_data)
    cal.ical(icalendar_calendar)
