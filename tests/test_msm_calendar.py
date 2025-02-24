import pytest
from my_school_menus.msm_calendar import Calendar


def menu_data():
    return {'data': [
        {'setting': '{"current_display":[{"type":"recipe","recipe_name":"Chicken Nuggets"}]}'}
    ]}


def test_events_missing_menu_data():
    with pytest.raises(ValueError):
        Calendar.events({'data': []})


def test_events():
    Calendar.events(menu_data())


def test_calendar():
    event_data = Calendar.events(menu_data())
    Calendar.calendar(event_data)


def test_ical():
    event_data = Calendar.events(menu_data())
    icalendar_calendar = Calendar.calendar(event_data)
    Calendar.ical(icalendar_calendar)
