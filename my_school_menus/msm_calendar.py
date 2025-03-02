import json
import uuid
from datetime import datetime, time, timedelta

class Calendar:
    def __init__(self, default_breakfast_time=time(8, 0), default_lunch_time=time(12, 0)):
        """
        Initialize the Calendar with default times for meals.

        :param default_breakfast_time: Default time for breakfast events (default: 8:00 AM)
        :param default_lunch_time: Default time for lunch events (default: 12:00 PM)
        """
        self.default_breakfast_time = default_breakfast_time
        self.default_lunch_time = default_lunch_time

    def events(self, menu: json, menu_type: str = "lunch", include_time: bool = False) -> list:
        """
        Generate a list of events from a menu

        :param menu: json menu.
        :param menu_type: Type of menu ("breakfast" or "lunch").
        :param include_time: Whether to include time in events.

        :return: List of events.
        :rtype: list
        """
        event_list = []
        menu_data = menu['data']
        if not menu_data:
            raise ValueError(
                f"Missing menu data."
            )

        # Set the event time based on menu type
        event_time = None
        if include_time:
            if menu_type.lower() == "breakfast":
                event_time = self.default_breakfast_time
            else:  # Default to lunch time for any other menu type
                event_time = self.default_lunch_time

        for entry in menu_data:
            if entry is None:
                continue
            
            try:
                # Use menu_type from parameter to determine which prefix to use
                prefix = "L: " if menu_type.lower() == "lunch" else "B: "
                
                # Process each item in the menu
                recipe_count = 0
                category_count = 0
                summary = ""
                description_parts = []
                
                for item in json.loads(entry['setting'])['current_display']:
                    if item['type'] == 'recipe' and recipe_count == 0:
                        recipe_count += 1
                        summary = f"{prefix}{item['name']}"
                    
                    if item['type'] == 'category' and category_count == 0:
                        category_count += 1
                        description_parts.append(f"{item['name']}:")
                    elif item['type'] == 'category':
                        description_parts.append("")  # Empty line
                        description_parts.append(f"{item['name']}:")
                    else:
                        description_parts.append(item['name'])
                
                if summary == '':
                    continue
                
                # Create event dictionary instead of using icalendar library
                event = {
                    'summary': summary,
                    'description': description_parts,
                    'uid': str(uuid.uuid4()),
                    'dtstamp': datetime.now(),
                    'transp': 'OPAQUE'
                }
                
                entry_date = datetime.fromisoformat(entry['day']).date()
                
                # Add time to the event if requested
                if include_time and event_time:
                    event_datetime = datetime.combine(entry_date, event_time)
                    event['dtstart'] = event_datetime
                    
                    # Add event duration (30 minutes for breakfast, 45 minutes for lunch)
                    if menu_type.lower() == "breakfast":
                        duration = timedelta(minutes=30)
                    else:
                        duration = timedelta(minutes=45)
                    
                    end_time = event_datetime + duration
                    event['dtend'] = end_time
                else:
                    event['dtstart'] = entry_date
                
                event_list.append(event)
            except KeyError:
                continue

        return event_list

    def combine_calendars(self, calendar_list: list) -> list:
        """
        Combine multiple calendars into a single calendar

        :param calendar_list: List of calendars.

        :return: Combined calendar events.
        :rtype: list
        """
        combined_events = []
        for cal in calendar_list:
            combined_events.extend(cal)
        return combined_events

    def calendar(self, cal_events: list) -> list:
        """
        Generate a calendar from events

        :param cal_events: list of events.

        :return: Calendar events.
        :rtype: list
        """
        return cal_events

    def ical(self, events: list) -> str:
        """
        Get the menu as a properly formatted iCal string.

        :param events: List of event dictionaries.

        :return: Properly formatted iCal string.
        :rtype: str
        """
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//My School Menus//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH"
        ]
        
        for event in events:
            lines.append("BEGIN:VEVENT")
            
            # Add summary
            lines.append(f"SUMMARY:{event['summary']}")
            
            # Add start time/date
            if isinstance(event['dtstart'], datetime):
                dt_str = event['dtstart'].strftime("%Y%m%dT%H%M%S")
                lines.append(f"DTSTART:{dt_str}")
            else:
                dt_str = event['dtstart'].strftime("%Y%m%d")
                lines.append(f"DTSTART;VALUE=DATE:{dt_str}")
            
            # Add end time/date if present
            if 'dtend' in event:
                dt_str = event['dtend'].strftime("%Y%m%dT%H%M%S")
                lines.append(f"DTEND:{dt_str}")
            
            # Add timestamp
            dt_str = event['dtstamp'].strftime("%Y%m%dT%H%M%SZ")
            lines.append(f"DTSTAMP:{dt_str}")
            
            # Add UID
            lines.append(f"UID:{event['uid']}")
            
            # Add description with proper folding
            description = "\\n".join(event['description'])
            lines.extend(self._fold_content("DESCRIPTION", description))
            
            # Add transparency
            lines.append(f"TRANSP:{event['transp']}")
            
            lines.append("END:VEVENT")
        
        lines.append("END:VCALENDAR")
        
        # Join with proper line endings for iCalendar (CRLF)
        return "\r\n".join(lines)
    
    @staticmethod
    def _fold_content(property_name, content):
        """
        Properly fold long content according to iCalendar spec (75 chars)
        
        :param property_name: The property name
        :param content: The content to fold
        :return: List of properly folded lines
        """
        # First line includes property name
        first_line = f"{property_name}:{content}"
        if len(first_line) <= 75:
            return [first_line]
            
        # Need to fold
        result = []
        current_line = first_line
        
        while len(current_line) > 75:
            # Add the first 75 chars to the result
            result.append(current_line[:75])
            # The rest becomes the next line, with a space at the beginning
            current_line = " " + current_line[75:]
        
        # Don't forget the remainder
        if current_line:
            result.append(current_line)
            
        return result

    def set_breakfast_time(self, hour: int, minute: int = 0):
        """
        Set the default time for breakfast events.

        :param hour: Hour (0-23)
        :param minute: Minute (0-59)
        """
        self.default_breakfast_time = time(hour, minute)

    def set_lunch_time(self, hour: int, minute: int = 0):
        """
        Set the default time for lunch events.

        :param hour: Hour (0-23)
        :param minute: Minute (0-59)
        """
        self.default_lunch_time = time(hour, minute)