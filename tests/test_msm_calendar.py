import pytest
from my_school_menus.msm_calendar import Calendar


def menu_data():
    return {'data': [
        {'day': '2022-01-01T00:00:00.000-05:00', 'setting': '{"current_display":[{"type":"recipe","name":"Chicken Nuggets"}]}'}
    ]}


def test_events_missing_menu_data():
    cal = Calendar()
    with pytest.raises(ValueError):
        cal.events({'data': []})


def test_events():
    cal = Calendar()
    cal.events(menu_data())


def test_ical():
    cal = Calendar()
    event_data = cal.events(menu_data())
    cal.ical(event_data)
