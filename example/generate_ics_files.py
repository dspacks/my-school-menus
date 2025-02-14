import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.pardir)

from my_school_menus.msm_api import Menus
from my_school_menus.msm_calendar import Calendar

# Constants for Breakfast and Lunch
DISTRICT_ID = 2230
SITE_ID = 14066
BREAKFAST_MENU_ID = 90143  # Replace with actual breakfast menu ID
LUNCH_MENU_ID = 65638  # Replace with actual lunch menu ID
FILE_SUFFIX = 'school-menus-calendar.ics'

BREAKFAST_PREFIX = "Breakfast:"
LUNCH_PREFIX = "Lunch:"

BREAKFAST_TIME = (8, 45)  # 8:45 AM
LUNCH_TIME = (12, 0)  # 12:00 PM
EVENT_DURATION = 30  # Minutes

def fetch_menu(menus, menu_id, label, start_hour, start_minute):
    menu = menus.get(district_id=DISTRICT_ID, menu_id=menu_id)
    available_dates = menus.menu_months(menu)
    events = []
    for date in available_dates:
        daily_menu = menus.get(district_id=DISTRICT_ID, menu_id=menu_id, date=date)
        cal = Calendar()
        meal_events = cal.events(daily_menu, label, start_hour, start_minute, EVENT_DURATION)
        events.extend(meal_events)
    return events

def main():
    menus = Menus()
    
    # Fetch events for breakfast and lunch
    breakfast_events = fetch_menu(menus, BREAKFAST_MENU_ID, BREAKFAST_PREFIX, *BREAKFAST_TIME)
    lunch_events = fetch_menu(menus, LUNCH_MENU_ID, LUNCH_PREFIX, *LUNCH_TIME)
    
    # Combine all events into a single calendar
    all_events = breakfast_events + lunch_events
    cal = Calendar()
    calendar = cal.calendar(all_events)
    ical = cal.ical(calendar)
    
    # Save to a single file
    filepath = f"{os.path.dirname(os.path.realpath(__file__))}/{FILE_SUFFIX}"
    print(f"Writing calendar file to {filepath}")
    with open(filepath, 'w') as f:
        f.write(ical)
    print('Calendar file written successfully!')

if __name__ == '__main__':
    main()
