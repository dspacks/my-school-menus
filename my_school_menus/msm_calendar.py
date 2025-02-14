import icalendar
import json
from datetime import datetime, timedelta

class Calendar:
    @staticmethod
    def events(menu: json, label: str, start_hour: int, start_minute: int, duration: int, all_day: bool) -> list:
        """
        Generate a list of events from a menu with specified start times, durations, or as all-day events.

        :param menu: json menu.
        :param label: Event label prefix (e.g., "Breakfast:" or "Lunch:").
        :param start_hour: Hour for event start time.
        :param start_minute: Minute for event start time.
        :param duration: Event duration in minutes.
        :param all_day: Boolean flag for all-day events.
        :return: List of events.
        """
        event_list = []
        menu_data = menu['data']
        if not menu_data:
            raise ValueError("Missing menu data.")

        for entry in menu_data:
            if entry is None:
                continue
            event = icalendar.Event()
            description = ''
            summary = ''
            recipe_count = 0
            category_count = 0
            try:
                for item in json.loads(entry['setting'])['current_display']:
                    if item['type'] == 'recipe' and recipe_count == 0:
                        recipe_count += 1
                        summary = f"{label} {item['name']}"
                    if item['type'] == 'category' and category_count == 0:
                        category_count += 1
                        description = f"{description}{item['name']}:\n"
                    elif item['type'] == 'category':
                        description = f"{description}\n{item['name']}:\n"
                    else:
                        description = f"{description}{item['name']}\n"
                if summary == '':
                    continue

                event_start = datetime.fromisoformat(entry['day'])

                if all_day:
                    event.add('dtstart', event_start.date())  # All-day event
                    event.add('dtend', event_start.date() + timedelta(days=1))  # End next day for all-day behavior
                else:
                    event_start = event_start.replace(hour=start_hour, minute=start_minute)
                    event_end = event_start + timedelta(minutes=duration)
                    event.add('dtstart', event_start)
                    event.add('dtend', event_end)

                event.add('summary', summary)
                event.add('description', description)
                event.add('alarms', [])
                event_list.append(event)
            except KeyError:
                continue

        return event_list

    @staticmethod
    def calendar(cal_events: list) -> icalendar.Calendar:
        """
        Generate a calendar from a menu.

        :param cal_events: list of events.
        :return: iCalendar calendar.
        """
        cal = icalendar.Calendar()
        for event in cal_events:
            cal.add_component(event)
        return cal

    @staticmethod
    def ical(icalendar_calendar: icalendar.Calendar) -> str:
        """
        Get the menu as an iCal bytes object.

        :param icalendar_calendar: iCalendar calendar.
        :return: Decoded iCal file.
        """
        return icalendar_calendar.to_ical().decode('utf-8')
