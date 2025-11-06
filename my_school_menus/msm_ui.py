import tkinter as tk
from tkinter import ttk
import json
import os
from datetime import time, datetime

from .msm_api import Menus
from .msm_calendar import Calendar as MSMCalendar

CONFIG_FILE = 'config.json'

class ConfigDialog(tk.Toplevel):
    def __init__(self, parent, title=None, config=None):
        super().__init__(parent)
        self.transient(parent)
        if title:
            self.title(title)
        self.parent = parent
        self.result = None
        body = tk.Frame(self)
        self.initial_focus = self.body(body, config)
        body.pack(padx=5, pady=5)
        self.buttonbox()
        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))
        self.initial_focus.focus_set()
        self.wait_window(self)

    def body(self, master, config):
        self.entries = {}
        labels = ['District ID', 'Site ID', 'Lunch Menu ID', 'Breakfast Menu ID']
        for i, label in enumerate(labels):
            tk.Label(master, text=label).grid(row=i, column=0, sticky='w', padx=5, pady=5)
            entry = tk.Entry(master)
            entry.grid(row=i, column=1, padx=5, pady=5)
            if config:
                entry.insert(0, config[i])
            self.entries[label] = entry
        return self.entries[labels[0]]

    def buttonbox(self):
        box = tk.Frame(self)
        tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(box, text="Cancel", width=10, command=self.cancel).pack(side=tk.LEFT, padx=5, pady=5)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        box.pack()

    def ok(self, event=None):
        self.result = [self.entries[label].get() for label in ['District ID', 'Site ID', 'Lunch Menu ID', 'Breakfast Menu ID']]
        self.destroy()

    def cancel(self, event=None):
        self.destroy()

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack(fill="both", expand=True)
        self.create_widgets()
        self.load_config()

    def create_widgets(self):
        # School/Menu Configuration List
        self.tree = ttk.Treeview(self, columns=('District ID', 'Site ID', 'Lunch Menu ID', 'Breakfast Menu ID'), show='headings')
        self.tree.heading('District ID', text='District ID')
        self.tree.heading('Site ID', text='Site ID')
        self.tree.heading('Lunch Menu ID', text='Lunch Menu ID')
        self.tree.heading('Breakfast Menu ID', text='Breakfast Menu ID')
        self.tree.pack(side="top", fill="both", expand=True)

        # Buttons
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(side="top", fill="x")

        self.add_button = tk.Button(self.button_frame, text="Add", command=self.add_config)
        self.add_button.pack(side="left")

        self.edit_button = tk.Button(self.button_frame, text="Edit", command=self.edit_config)
        self.edit_button.pack(side="left")

        self.remove_button = tk.Button(self.button_frame, text="Remove", command=self.remove_config)
        self.remove_button.pack(side="left")

        # ICS Generation
        self.generate_frame = tk.Frame(self)
        self.generate_frame.pack(side="top", fill="x")

        self.combine_ics = tk.BooleanVar()
        self.combine_ics_checkbox = tk.Checkbutton(self.generate_frame, text="Combine ICS files", variable=self.combine_ics)
        self.combine_ics_checkbox.pack(side="left")

        self.generate_button = tk.Button(self.generate_frame, text="Generate ICS", command=self.generate_ics)
        self.generate_button.pack(side="left")

        # Status Bar
        self.status = tk.Label(self, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side="bottom", fill="x")

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side="bottom")

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                try:
                    configs = json.load(f)
                    for config in configs:
                        self.tree.insert('', 'end', values=list(config.values()))
                except json.JSONDecodeError:
                    self.status.config(text="Error: config.json is corrupted.")
        else:
            self.status.config(text="No config.json found. Please add a configuration.")

    def save_config(self):
        configs = []
        for child in self.tree.get_children():
            values = self.tree.item(child)['values']
            configs.append({
                'District ID': values[0],
                'Site ID': values[1],
                'Lunch Menu ID': values[2],
                'Breakfast Menu ID': values[3]
            })
        with open(CONFIG_FILE, 'w') as f:
            json.dump(configs, f, indent=4)

    def add_config(self):
        dialog = ConfigDialog(self, "Add Configuration")
        if dialog.result:
            self.tree.insert('', 'end', values=dialog.result)
            self.save_config()

    def edit_config(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        item = self.tree.item(selected_item[0])
        dialog = ConfigDialog(self, "Edit Configuration", item['values'])
        if dialog.result:
            self.tree.item(selected_item[0], values=dialog.result)
            self.save_config()

    def remove_config(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        for item in selected_item:
            self.tree.delete(item)
        self.save_config()

    def generate_ics(self):
        self.status.config(text="Generating ICS files...")
        self.update()

        menus = Menus()
        cal = MSMCalendar(
            default_breakfast_time=time(8, 0),
            default_lunch_time=time(12, 0)
        )

        all_events = []

        for i, child in enumerate(self.tree.get_children()):
            config = self.tree.item(child)['values']
            district_id = int(config[0])
            site_id = int(config[1])
            lunch_menu_id = int(config[2]) if config[2] else None
            breakfast_menu_id = int(config[3]) if config[3] else None

            school_events = []

            try:
                if lunch_menu_id:
                    lunch_menu = menus.get(district_id=district_id, menu_id=lunch_menu_id, date=datetime.now())
                    school_events.extend(cal.events(lunch_menu, menu_type="lunch", include_time=True))
                if breakfast_menu_id:
                    breakfast_menu = menus.get(district_id=district_id, menu_id=breakfast_menu_id, date=datetime.now())
                    school_events.extend(cal.events(breakfast_menu, menu_type="breakfast", include_time=True))

                if not self.combine_ics.get():
                    ical = cal.ical(school_events)
                    with open(f'school-{district_id}-{site_id}-menu-calendar.ics', 'w', newline='') as f:
                        f.write(ical)

                all_events.extend(school_events)
            except Exception as e:
                self.status.config(text=f"Error: {e}")
                return

        if self.combine_ics.get():
            ical = cal.ical(all_events)
            with open('school-menu-calendar.ics', 'w', newline='') as f:
                f.write(ical)
            self.status.config(text="Combined ICS file generated.")
        else:
            self.status.config(text="Individual ICS files generated.")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("My School Menus ICS Generator")
    app = Application(master=root)
    app.mainloop()
