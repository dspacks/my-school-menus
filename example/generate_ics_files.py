import sys
import os
import argparse
from datetime import time
sys.path.append(os.path.pardir)

from my_school_menus.msm_api import Menus
# We import the calendar class with 'as MSMCalendar' to avoid conflicts
from my_school_menus.msm_calendar import Calendar as MSMCalendar
from my_school_menus.msm_ui import Application
import tkinter as tk

# School Configuration
# ===========================================
# Change these values to match your school district
DISTRICT_ID = 2230
SITE_ID = 14066

# Menu Configuration
# ===========================================
# Set to None if you only want one menu type
LUNCH_MENU_ID = 65638  # Set to your lunch menu ID
BREAKFAST_MENU_ID = 90143  # Set to your breakfast menu ID or None if not needed

# Time Configuration
# ===========================================
INCLUDE_TIME = True  # Set to False if you don't want times on your calendar events
BREAKFAST_TIME = time(8, 0)  # 8:00 AM
LUNCH_TIME = time(12, 0)  # 12:00 PM

# Output Configuration
# ===========================================
FILE_SUFFIX = 'school-menu-calendar.ics'
# Set this to True to create a raw debug file
DEBUG = False
# Set to True to create separate breakfast and lunch files (in addition to combined)
CREATE_SEPARATE_FILES = False


def main():
    parser = argparse.ArgumentParser(description="Generate iCalendar files for school menus.")
    parser.add_argument('--ui', action='store_true', help='Launch the graphical user interface.')
    args = parser.parse_args()

    if args.ui:
        root = tk.Tk()
        root.title("My School Menus ICS Generator")
        app = Application(master=root)
        app.mainloop()
        return

    menus = Menus()
    cal = MSMCalendar(
        default_breakfast_time=BREAKFAST_TIME,
        default_lunch_time=LUNCH_TIME
    )
    
    # Process lunch menu if specified
    lunch_available_dates = []
    if LUNCH_MENU_ID:
        print(f"Fetching lunch menu information for district {DISTRICT_ID}, menu {LUNCH_MENU_ID}...")
        try:
            lunch_menu = menus.get(district_id=DISTRICT_ID, menu_id=LUNCH_MENU_ID)
            lunch_available_dates = menus.menu_months(lunch_menu)
            print(f"Found {len(lunch_available_dates)} months with lunch menus: {', '.join(d.strftime('%Y-%m') for d in lunch_available_dates)}")
        except Exception as e:
            print(f"Error getting lunch menu: {e}")
    
    # Process breakfast menu if specified
    breakfast_available_dates = []
    if BREAKFAST_MENU_ID:
        print(f"Fetching breakfast menu information for district {DISTRICT_ID}, menu {BREAKFAST_MENU_ID}...")
        try:
            breakfast_menu = menus.get(district_id=DISTRICT_ID, menu_id=BREAKFAST_MENU_ID)
            breakfast_available_dates = menus.menu_months(breakfast_menu)
            print(f"Found {len(breakfast_available_dates)} months with breakfast menus: {', '.join(d.strftime('%Y-%m') for d in breakfast_available_dates)}")
        except Exception as e:
            print(f"Error getting breakfast menu: {e}")
    
    # Get unique dates from both menus
    all_dates = set(lunch_available_dates + breakfast_available_dates)
    print(f"Processing {len(all_dates)} total months")
    
    for date in all_dates:
        print(f"\nProcessing date: {date.year}-{date.month}")
        
        all_events = []  # Will hold all events for the month (breakfast and lunch)
        
        # Process lunch menu for this date if available
        if LUNCH_MENU_ID and date in lunch_available_dates:
            print(f"Processing lunch menu for {date.year}-{date.month}")
            try:
                lunch_calendar_menu = menus.get(
                    district_id=DISTRICT_ID, menu_id=LUNCH_MENU_ID, date=date
                )
                lunch_events = cal.events(
                    lunch_calendar_menu, 
                    menu_type="lunch", 
                    include_time=INCLUDE_TIME
                )
                print(f"  Found {len(lunch_events)} lunch events")
                
                # Add lunch events to all events list
                all_events.extend(lunch_events)
                
                # Write separate lunch file if requested
                if CREATE_SEPARATE_FILES and lunch_events:
                    lunch_calendar = cal.calendar(lunch_events)
                    lunch_filepath = f"{os.path.dirname(os.path.realpath(__file__))}/{date.year}-{date.month:02}-lunch-{FILE_SUFFIX}"
                    lunch_ical = cal.ical(lunch_calendar)
                    with open(lunch_filepath, 'w', newline='') as f:
                        f.write(lunch_ical)
                    print(f"  Wrote separate lunch calendar to {lunch_filepath}")
            except Exception as e:
                print(f"Error processing lunch menu: {e}")
        
        # Process breakfast menu for this date if available
        if BREAKFAST_MENU_ID and date in breakfast_available_dates:
            print(f"Processing breakfast menu for {date.year}-{date.month}")
            try:
                breakfast_calendar_menu = menus.get(
                    district_id=DISTRICT_ID, menu_id=BREAKFAST_MENU_ID, date=date
                )
                breakfast_events = cal.events(
                    breakfast_calendar_menu, 
                    menu_type="breakfast", 
                    include_time=INCLUDE_TIME
                )
                print(f"  Found {len(breakfast_events)} breakfast events")
                
                # Add breakfast events to all events list
                all_events.extend(breakfast_events)
                
                # Write separate breakfast file if requested
                if CREATE_SEPARATE_FILES and breakfast_events:
                    breakfast_calendar = cal.calendar(breakfast_events)
                    breakfast_filepath = f"{os.path.dirname(os.path.realpath(__file__))}/{date.year}-{date.month:02}-breakfast-{FILE_SUFFIX}"
                    breakfast_ical = cal.ical(breakfast_calendar)
                    with open(breakfast_filepath, 'w', newline='') as f:
                        f.write(breakfast_ical)
                    print(f"  Wrote separate breakfast calendar to {breakfast_filepath}")
            except Exception as e:
                print(f"Error processing breakfast menu: {e}")
        
        # Create combined calendar file for this month
        if all_events:
            # Create the combined calendar
            combined_calendar = cal.calendar(all_events)
            filepath = f"{os.path.dirname(os.path.realpath(__file__))}/{date.year}-{date.month:02}-{FILE_SUFFIX}"
            
            print(f"Creating combined calendar with {len(all_events)} total events")
            ical = cal.ical(combined_calendar)
            
            # Write the calendar file
            print(f"Writing combined calendar file to {filepath}")
            with open(filepath, 'w', newline='') as f:
                f.write(ical)
            print(f"Calendar file written successfully!")
            
            # Write a debug copy if requested
            if DEBUG:
                debug_filepath = f"{os.path.dirname(os.path.realpath(__file__))}/{date.year}-{date.month:02}-debug-{FILE_SUFFIX}"
                with open(debug_filepath, 'w') as f:
                    visible_crlf = ical.replace('\r\n', '\\r\\n\n')
                    f.write(visible_crlf)
                print(f"Debug file written to {debug_filepath}")
        else:
            print(f"No menu data available for {date.year}-{date.month}, skipping file creation.")


if __name__ == '__main__':
    main()
