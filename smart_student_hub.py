

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import json
import os
import time
import copy
import uuid


# ============================================================
# SETTINGS
# ============================================================

APP_NAME = "SMART STUDENT HUB"
STUDENT_NAME = "Lathika M"
DATA_FILE = "smart_student_hub_data.json"


# ============================================================
# COLORS
# ============================================================

DARK = {
    "BG": "#0B1020",
    "SIDEBAR": "#10172B",
    "CARD": "#161F36",
    "CARD2": "#1C2742",
    "PURPLE": "#8967F5",
    "CYAN": "#31C6D4",
    "GREEN": "#27C58B",
    "ORANGE": "#F4A64E",
    "RED": "#F16C7B",
    "WHITE": "#F4F5FF",
    "MUTED": "#98A5C4",
    "BORDER": "#283451"
}


# ============================================================
# DEFAULT DATA
# ============================================================

DEFAULT_DATA = {
    "todos": [],
    "timetable": [],
    "planner": [],
    "notes": [],
    "assignments": [],
    "exams": [],
    "attendance": [],
    "progress": [],
    "navigator": [],
    "faculty": [],
    "announcements": [],
    "events": [],
    "expenses": [],
    "documents": [],
    "reminders": [],
    "goals": [],
    "feedback": [],
    "history": [],
    "settings": {
        "theme": "dark"
    }
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def now_dt():
    return datetime.datetime.now()


def now_text():
    return now_dt().strftime("%d-%m-%Y %I:%M:%S %p")


def new_id():
    return uuid.uuid4().hex


def format_seconds(seconds):
    seconds = max(0, int(seconds))
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes} min {remaining_seconds:02d} sec"


def parse_datetime(date_text, time_text):

    date_text = date_text.strip()
    time_text = time_text.strip()

    formats = [
        ("%d-%m-%Y", "%I:%M:%S %p"),
        ("%d-%m-%Y", "%I:%M %p"),
        ("%d-%m-%Y", "%H:%M:%S"),
        ("%d-%m-%Y", "%H:%M"),

        ("%Y-%m-%d", "%I:%M:%S %p"),
        ("%Y-%m-%d", "%I:%M %p"),
        ("%Y-%m-%d", "%H:%M:%S"),
        ("%Y-%m-%d", "%H:%M"),
    ]

    for date_format, time_format in formats:

        try:

            return datetime.datetime.strptime(
                f"{date_text} {time_text}",
                f"{date_format} {time_format}"
            )

        except ValueError:
            pass

    raise ValueError(
        "Use date DD-MM-YYYY and time HH:MM AM/PM."
    )


# ============================================================
# MAIN APPLICATION
# ============================================================

class SmartStudentHub:

    def __init__(self, root):

        self.root = root

        self.root.title(APP_NAME)
        self.root.geometry("1200x780")
        self.root.minsize(950, 650)

        self.data = self.load_data()

        self.current_page = "Home"

        self.sidebar_widgets = []

        self.clock_job = None
        self.reminder_job = None
        self.todo_refresh_job = None

        self.build_ui()

        self.show_page("Home")

        self.update_clock()

        self.check_reminders()

        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_app
        )

    # ========================================================
    # DATA
    # ========================================================

    def load_data(self):

        if not os.path.exists(DATA_FILE):

            return copy.deepcopy(
                DEFAULT_DATA
            )

        try:

            with open(
                DATA_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                saved_data = json.load(file)

            data = copy.deepcopy(
                DEFAULT_DATA
            )

            for key, value in saved_data.items():

                data[key] = value

            return data

        except Exception:

            messagebox.showwarning(
                "Data Error",
                "Saved data could not be loaded.\n"
                "A new data file will be created."
            )

            return copy.deepcopy(
                DEFAULT_DATA
            )

    def save_data(self):

        try:

            with open(
                DATA_FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    self.data,
                    file,
                    indent=2,
                    ensure_ascii=False
                )

        except Exception as error:

            messagebox.showerror(
                "Save Error",
                f"Could not save data:\n{error}"
            )

    # ========================================================
    # HISTORY
    # ========================================================

    def log_history(
        self,
        action,
        item_type="System",
        item_name="",
        details=""
    ):

        history_item = {

            "id": new_id(),

            "action": action,

            "item_type": item_type,

            "item_name": item_name,

            "details": details,

            "timestamp": now_text()
        }

        self.data["history"].append(
            history_item
        )

        self.save_data()

    # ========================================================
    # BUILD UI
    # ========================================================

    def build_ui(self):

        self.root.configure(
            bg=DARK["BG"]
        )

        # ----------------------------------------------------
        # GLOBAL MOUSE WHEEL
        # ----------------------------------------------------

        self.root.bind_all(
            "<MouseWheel>",
            self.global_wheel,
            add="+"
        )

        self.root.bind_all(
            "<Button-4>",
            lambda event:
            self.scroll_delta(-1),
            add="+"
        )

        self.root.bind_all(
            "<Button-5>",
            lambda event:
            self.scroll_delta(1),
            add="+"
        )

        # ====================================================
        # SIDEBAR
        # ====================================================

        self.sidebar = tk.Frame(
            self.root,
            bg=DARK["SIDEBAR"],
            width=250
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        self.sidebar.pack_propagate(False)

        self.side_canvas = tk.Canvas(
            self.sidebar,
            bg=DARK["SIDEBAR"],
            highlightthickness=0
        )

        self.side_canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.side_inner = tk.Frame(
            self.side_canvas,
            bg=DARK["SIDEBAR"]
        )

        self.side_window = self.side_canvas.create_window(
            (0, 0),
            window=self.side_inner,
            anchor="nw"
        )

        self.side_inner.bind(
            "<Configure>",
            lambda event:
            self.side_canvas.configure(
                scrollregion=self.side_canvas.bbox("all")
            )
        )

        self.side_canvas.bind(
            "<Configure>",
            lambda event:
            self.side_canvas.itemconfigure(
                self.side_window,
                width=event.width
            )
        )

        # ----------------------------------------------------
        # LOGO
        # ----------------------------------------------------

        tk.Label(
            self.side_inner,
            text="SMART",
            font=("Segoe UI", 21, "bold"),
            bg=DARK["SIDEBAR"],
            fg=DARK["WHITE"]
        ).pack(
            anchor="w",
            padx=22,
            pady=(24, 0)
        )

        tk.Label(
            self.side_inner,
            text="STUDENT HUB",
            font=("Segoe UI", 11, "bold"),
            bg=DARK["SIDEBAR"],
            fg=DARK["PURPLE"]
        ).pack(
            anchor="w",
            padx=23,
            pady=(0, 22)
        )

        # ====================================================
        # MENU
        # ====================================================

        menus = [

            (
                "MAIN MENU",
                [
                    "Home",
                    "AI Assistant",
                    "Timetable",
                    "Smart To-Do",
                    "Study Planner"
                ]
            ),

            (
                "ACADEMICS",
                [
                    "Notes & Materials",
                    "AI Notes Summarizer",
                    "Assignments",
                    "Exams & Quizzes",
                    "Attendance",
                    "Academic Progress"
                ]
            ),

            (
                "STUDENT TOOLS",
                [
                    "College Navigator",
                    "Faculty & Mentors",
                    "Announcements",
                    "Events",
                    "Expense Tracker",
                    "Document Manager"
                ]
            ),

            (
                "PERSONAL & SETTINGS",
                [
                    "Reminders",
                    "Goals & Habits",
                    "Feedback & Help",
                    "Settings",
                    "History"
                ]
            )
        ]

        for section_name, items in menus:

            tk.Label(
                self.side_inner,
                text=section_name,
                font=("Segoe UI", 8, "bold"),
                bg=DARK["SIDEBAR"],
                fg=DARK["MUTED"]
            ).pack(
                anchor="w",
                padx=23,
                pady=(8, 6)
            )

            for item in items:

                self.add_sidebar_button(
                    item
                )

        tk.Label(
            self.side_inner,
            text="AI features are reserved\nfor the next version.",
            bg=DARK["SIDEBAR"],
            fg=DARK["MUTED"],
            font=("Segoe UI", 8),
            justify="left"
        ).pack(
            anchor="w",
            padx=23,
            pady=(25, 25)
        )

        # ====================================================
        # MAIN CONTENT
        # ====================================================

        self.content = tk.Frame(
            self.root,
            bg=DARK["BG"]
        )

        self.content.pack(
            side="right",
            fill="both",
            expand=True
        )

        # ====================================================
        # HEADER
        # ====================================================

        self.header = tk.Frame(
            self.content,
            bg=DARK["BG"],
            height=72
        )

        self.header.pack(
            fill="x"
        )

        self.header.pack_propagate(False)

        self.page_title = tk.Label(
            self.header,
            text="Home",
            bg=DARK["BG"],
            fg=DARK["WHITE"],
            font=("Segoe UI", 21, "bold")
        )

        self.page_title.pack(
            side="left",
            padx=25,
            pady=20
        )

        self.student_label = tk.Label(
            self.header,
            text=STUDENT_NAME,
            bg=DARK["BG"],
            fg=DARK["PURPLE"],
            font=("Segoe UI", 10, "bold")
        )

        self.student_label.pack(
            side="right",
            padx=(0, 25),
            pady=(12, 0)
        )

        self.clock_label = tk.Label(
            self.header,
            text="",
            bg=DARK["BG"],
            fg=DARK["MUTED"],
            font=("Segoe UI", 9)
        )

        self.clock_label.place(
            relx=1,
            x=-25,
            y=45,
            anchor="e"
        )

        # ====================================================
        # MAIN SCROLL
        # ====================================================

        self.main_canvas = tk.Canvas(
            self.content,
            bg=DARK["BG"],
            highlightthickness=0
        )

        self.main_scroll = ttk.Scrollbar(
            self.content,
            orient="vertical",
            command=self.main_canvas.yview
        )

        self.main_canvas.configure(
            yscrollcommand=self.main_scroll.set
        )

        self.main_scroll.pack(
            side="right",
            fill="y"
        )

        self.main_canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.main_inner = tk.Frame(
            self.main_canvas,
            bg=DARK["BG"]
        )

        self.main_window = self.main_canvas.create_window(
            (0, 0),
            window=self.main_inner,
            anchor="nw"
        )

        self.main_inner.bind(
            "<Configure>",
            lambda event:
            self.main_canvas.configure(
                scrollregion=self.main_canvas.bbox("all")
            )
        )

        self.main_canvas.bind(
            "<Configure>",
            lambda event:
            self.main_canvas.itemconfigure(
                self.main_window,
                width=event.width
            )
        )

    # ========================================================
    # SIDEBAR BUTTON
    # ========================================================

    def add_sidebar_button(
        self,
        name
    ):

        button = tk.Button(
            self.side_inner,
            text="  " + name,
            anchor="w",
            relief="flat",
            bd=0,
            bg=DARK["SIDEBAR"],
            fg=DARK["MUTED"],
            activebackground=DARK["CARD2"],
            activeforeground=DARK["WHITE"],
            font=("Segoe UI", 10),
            padx=12,
            pady=8,
            cursor="hand2",
            command=lambda n=name:
            self.show_page(n)
        )

        button.pack(
            fill="x",
            padx=12,
            pady=1
        )

        self.sidebar_widgets.append(
            (name, button)
        )

    # ========================================================
    # SCROLLING
    # ========================================================

    def global_wheel(
        self,
        event
    ):

        widget = self.root.winfo_containing(
            event.x_root,
            event.y_root
        )

        if widget is None:
            return

        try:

            in_sidebar = False

            parent = widget

            for _ in range(10):

                if parent in (
                    self.side_canvas,
                    self.side_inner
                ):

                    in_sidebar = True
                    break

                parent = getattr(
                    parent,
                    "master",
                    None
                )

                if parent is None:
                    break

            if in_sidebar:

                self.side_canvas.yview_scroll(
                    -1 if event.delta > 0 else 1,
                    "units"
                )

            else:

                self.main_canvas.yview_scroll(
                    -1 if event.delta > 0 else 1,
                    "units"
                )

        except Exception:
            pass

    def scroll_delta(
        self,
        direction
    ):

        self.main_canvas.yview_scroll(
            direction,
            "units"
        )

    # ========================================================
    # PAGE MANAGEMENT
    # ========================================================

    def clear_main(self):

        if self.todo_refresh_job:

            try:

                self.root.after_cancel(
                    self.todo_refresh_job
                )

            except Exception:
                pass

            self.todo_refresh_job = None

        for child in self.main_inner.winfo_children():

            child.destroy()

    def show_page(
        self,
        page
    ):

        self.current_page = page

        self.page_title.config(
            text=page
        )

        for name, button in self.sidebar_widgets:

            if name == page:

                button.config(
                    bg=DARK["CARD2"],
                    fg=DARK["WHITE"]
                )

            else:

                button.config(
                    bg=DARK["SIDEBAR"],
                    fg=DARK["MUTED"]
                )

        self.clear_main()

        handlers = {

            "Home":
                self.page_home,

            "AI Assistant":
                self.page_ai,

            "Timetable":
                lambda:
                self.page_records(
                    "timetable",
                    "Timetable"
                ),

            "Smart To-Do":
                self.page_todo,

            "Study Planner":
                lambda:
                self.page_records(
                    "planner",
                    "Study Planner"
                ),

            "Notes & Materials":
                lambda:
                self.page_notes(),

            "AI Notes Summarizer":
                self.page_ai_notes,

            "Assignments":
                lambda:
                self.page_records(
                    "assignments",
                    "Assignments"
                ),

            "Exams & Quizzes":
                lambda:
                self.page_records(
                    "exams",
                    "Exams & Quizzes"
                ),

            "Attendance":
                self.page_attendance,

            "Academic Progress":
                self.page_progress,

            "College Navigator":
                lambda:
                self.page_records(
                    "navigator",
                    "College Navigator"
                ),

            # =================================================
            # CHANGED
            # Faculty no longer uses date/time form
            # =================================================

            "Faculty & Mentors":
                self.page_faculty,

            "Announcements":
                lambda:
                self.page_records(
                    "announcements",
                    "Announcements"
                ),

            "Events":
                lambda:
                self.page_records(
                    "events",
                    "Events"
                ),

            "Expense Tracker":
                self.page_expenses,

            "Document Manager":
                self.page_documents,

            "Reminders":
                lambda:
                self.page_records(
                    "reminders",
                    "Reminders"
                ),

            # =================================================
            # CHANGED
            # Goals no longer uses date/time form
            # =================================================

            "Goals & Habits":
                self.page_goals,

            "Feedback & Help":
                self.page_feedback,

            "Settings":
                self.page_settings,

            "History":
                self.page_history
        }

        handlers.get(
            page,
            self.page_home
        )()

    # ========================================================
    # UI HELPERS
    # ========================================================

    def card(
        self,
        parent=None,
        **kwargs
    ):

        return tk.Frame(
            parent or self.main_inner,
            bg=DARK["CARD"],
            highlightbackground=DARK["BORDER"],
            highlightthickness=1,
            **kwargs
        )

    def label(
        self,
        parent,
        text,
        size=10,
        color=None,
        bold=False
    ):

        return tk.Label(
            parent,
            text=text,
            bg=parent.cget("bg"),
            fg=color or DARK["WHITE"],
            font=(
                "Segoe UI",
                size,
                "bold" if bold else "normal"
            )
        )

    def button(
        self,
        parent,
        text,
        command,
        color=None,
        width=14
    ):

        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color or DARK["PURPLE"],
            fg="white",
            activebackground=color or DARK["PURPLE"],
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=10,
            pady=7,
            cursor="hand2",
            font=("Segoe UI", 9, "bold"),
            width=width
        )

    def entry(
        self,
        parent,
        default=""
    ):

        entry = tk.Entry(
            parent,
            bg=DARK["CARD2"],
            fg=DARK["WHITE"],
            insertbackground=DARK["WHITE"],
            relief="flat",
            font=("Segoe UI", 10)
        )

        entry.insert(
            0,
            default
        )

        entry.pack(
            fill="x",
            padx=12,
            pady=(3, 8),
            ipady=5
        )

        return entry

    def field(
        self,
        parent,
        text,
        default=""
    ):

        self.label(
            parent,
            text,
            8,
            DARK["MUTED"],
            True
        ).pack(
            anchor="w",
            padx=12,
            pady=(7, 0)
        )

        return self.entry(
            parent,
            default
        )

    # ========================================================
    # HOME
    # ========================================================

    def page_home(self):

        frame = self.main_inner

        banner = self.card(
            frame
        )

        banner.pack(
            fill="x",
            padx=22,
            pady=10
        )

        tk.Label(
            banner,
            text=f"Welcome back, {STUDENT_NAME}!",
            bg=DARK["CARD"],
            fg=DARK["WHITE"],
            font=("Segoe UI", 23, "bold")
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 3)
        )

        tk.Label(
            banner,
            text=(
                "Your academic tasks, schedule, notes, "
                "reminders and progress in one place."
            ),
            bg=DARK["CARD"],
            fg=DARK["MUTED"],
            font=("Segoe UI", 10)
        ).pack(
            anchor="w",
            padx=20,
            pady=(0, 20)
        )

        # ----------------------------------------------------
        # STATISTICS
        # ----------------------------------------------------

        row = tk.Frame(
            frame,
            bg=DARK["BG"]
        )

        row.pack(
            fill="x",
            padx=22,
            pady=5
        )

        statistics = [

            (
                "Active Tasks",
                len([
                    x for x in self.data["todos"]
                    if x.get("status") != "Completed"
                ]),
                DARK["PURPLE"]
            ),

            (
                "Assignments",
                len(
                    self.data["assignments"]
                ),
                DARK["CYAN"]
            ),

            (
                "Exams",
                len(
                    self.data["exams"]
                ),
                DARK["ORANGE"]
            ),

            (
                "History",
                len(
                    self.data["history"]
                ),
                DARK["GREEN"]
            )
        ]

        for title, value, color in statistics:

            stat_card = self.card(
                row
            )

            stat_card.pack(
                side="left",
                fill="both",
                expand=True,
                padx=5
            )

            tk.Label(
                stat_card,
                text=str(value),
                bg=DARK["CARD"],
                fg=color,
                font=("Segoe UI", 22, "bold")
            ).pack(
                anchor="w",
                padx=15,
                pady=(14, 0)
            )

            tk.Label(
                stat_card,
                text=title,
                bg=DARK["CARD"],
                fg=DARK["MUTED"],
                font=("Segoe UI", 9)
            ).pack(
                anchor="w",
                padx=15,
                pady=(0, 14)
            )

        # ----------------------------------------------------
        # QUICK ACCESS
        # ----------------------------------------------------

        quick = self.card(
            frame
        )

        quick.pack(
            fill="x",
            padx=22,
            pady=12
        )

        tk.Label(
            quick,
            text="Quick Access",
            bg=DARK["CARD"],
            fg=DARK["WHITE"],
            font=("Segoe UI", 13, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=12
        )

        for name in [
            "Smart To-Do",
            "Timetable",
            "Assignments",
            "Exams & Quizzes",
            "Attendance",
            "History"
        ]:

            self.button(
                quick,
                name,
                lambda n=name:
                self.show_page(n),
                DARK["PURPLE"],
                16
            ).pack(
                side="left",
                padx=6,
                pady=(0, 15)
            )

        # ----------------------------------------------------
        # UPCOMING
        # ----------------------------------------------------

        upcoming = self.card(
            frame
        )

        upcoming.pack(
            fill="x",
            padx=22,
            pady=5
        )

        tk.Label(
            upcoming,
            text="Upcoming Activities",
            bg=DARK["CARD"],
            fg=DARK["WHITE"],
            font=("Segoe UI", 13, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=12
        )

        activities = []

        for key in DEFAULT_DATA:

            if key in (
                "history",
                "settings",
                "notes",
                "feedback",
                "expenses",
                "attendance",
                "progress",
                "navigator",
                "documents",
                "faculty",
                "announcements"
            ):
                continue

            for item in self.data.get(
                key,
                []
            ):

                if item.get(
                    "due_datetime"
                ):

                    try:

                        due = datetime.datetime.fromisoformat(
                            item["due_datetime"]
                        )

                        activities.append(
                            (
                                due,
                                item.get(
                                    "name",
                                    "Unnamed"
                                ),
                                key
                            )
                        )

                    except Exception:
                        pass

        activities.sort(
            key=lambda x: x[0]
        )

        if not activities:

            tk.Label(
                upcoming,
                text="No scheduled activities yet.",
                bg=DARK["CARD"],
                fg=DARK["MUTED"]
            ).pack(
                anchor="w",
                padx=15,
                pady=10
            )

        else:

            for due, name, key in activities[:6]:

                tk.Label(
                    upcoming,
                    text=(
                        f"• {name}  —  "
                        f"{due.strftime('%d-%m-%Y %I:%M %p')}"
                    ),
                    bg=DARK["CARD"],
                    fg=DARK["WHITE"],
                    font=("Segoe UI", 9)
                ).pack(
                    anchor="w",
                    padx=18,
                    pady=3
                )

        self.main_canvas.yview_moveto(0)

    # ========================================================
    # AI
    # ========================================================

    def page_ai(self):

        card = self.card()

        card.pack(
            fill="x",
            padx=22,
            pady=20
        )

        tk.Label(
            card,
            text="AI Assistant",
            bg=DARK["CARD"],
            fg=DARK["PURPLE"],
            font=("Segoe UI", 20, "bold")
        ).pack(
            pady=(25, 8)
        )

        tk.Label(
            card,
            text=(
                "AI Assistant is intentionally kept inactive "
                "for this version.\n\n"
                "The other Student Hub modules are active."
            ),
            bg=DARK["CARD"],
            fg=DARK["MUTED"],
            font=("Segoe UI", 11),
            justify="center"
        ).pack(
            pady=15
        )

        self.button(
            card,
            "Back to Home",
            lambda:
            self.show_page("Home")
        ).pack(
            pady=(0, 25)
        )

    # ========================================================
    # NOTES
    # ========================================================

    def page_ai_notes(self):

        self.page_notes(
            ai_mode=True
        )

    def page_notes(
        self,
        ai_mode=False
    ):

        title = (
            "AI Notes Summarizer"
            if ai_mode
            else
            "Notes & Materials"
        )

        top = self.card()

        top.pack(
            fill="x",
            padx=22,
            pady=12
        )

        tk.Label(
            top,
            text=title,
            bg=DARK["CARD"],
            fg=DARK["WHITE"],
            font=("Segoe UI", 16, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=12
        )

        tk.Label(
            top,
            text=(
                "AI summarization will be added later."
                if ai_mode
                else
                "Create and save your study notes."
            ),
            bg=DARK["CARD"],
            fg=DARK["MUTED"]
        ).pack(
            anchor="w",
            padx=15,
            pady=(0, 10)
        )

        title_entry = self.field(
            top,
            "Note Title"
        )

        body = tk.Text(
            top,
            height=7,
            bg=DARK["CARD2"],
            fg=DARK["WHITE"],
            insertbackground=DARK["WHITE"],
            relief="flat"
        )

        body.pack(
            fill="x",
            padx=12,
            pady=8
        )

        def save_note():

            note_title = title_entry.get().strip()

            note_text = body.get(
                "1.0",
                "end"
            ).strip()

            if not note_title or not note_text:

                messagebox.showwarning(
                    "Notes",
                    "Enter a title and note."
                )

                return

            item = {

                "id": new_id(),

                "name": note_title,

                "content": note_text,

                "timestamp": now_text()
            }

            self.data["notes"].append(
                item
            )

            self.log_history(
                "Added",
                "Note",
                note_title
            )

            self.save_data()

            messagebox.showinfo(
                "Saved",
                "Note saved successfully."
            )

            self.show_page(
                title
            )

        self.button(
            top,
            "Save Note",
            save_note,
            DARK["GREEN"]
        ).pack(
            pady=10
        )

        for item in reversed(
            self.data["notes"]
        ):

            note_card = self.card()

            note_card.pack(
                fill="x",
                padx=22,
                pady=5
            )

            tk.Label(
                note_card,
                text=item["name"],
                bg=DARK["CARD"],
                fg=DARK["WHITE"],
                font=("Segoe UI", 11, "bold")
            ).pack(
                anchor="w",
                padx=12,
                pady=(10, 2)
            )

            tk.Label(
                note_card,
                text=item.get(
                    "content",
                    ""
                ),
                bg=DARK["CARD"],
                fg=DARK["MUTED"],
                justify="left",
                wraplength=850
            ).pack(
                anchor="w",
                padx=12,
                pady=(0, 8)
            )

            self.button(
                note_card,
                "Delete",
                lambda i=item:
                self.delete_generic(
                    "notes",
                    i,
                    title
                ),
                DARK["RED"],
                9
            ).pack(
                anchor="e",
                padx=10,
                pady=(0, 10)
            )

    # ========================================================
    # SMART TO-DO
    # ========================================================

    def page_todo(self):

        frame = self.main_inner

        form = self.card()

        form.pack(
            fill="x",
            padx=22,
            pady=10
        )

        tk.Label(
            form,
            text="Add Smart To-Do",
            bg=DARK["CARD"],
            fg=DARK["WHITE"],
            font=("Segoe UI", 15, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=12
        )

        name = self.field(
            form,
            "Task Name"
        )

        grid = tk.Frame(
            form,
            bg=DARK["CARD"]
        )

        grid.pack(
            fill="x",
            padx=7
        )

        start_date = self.field(
            grid,
            "Start Date",
            now_dt().strftime(
                "%d-%m-%Y"
            )
        )

        start_time = self.field(
            grid,
            "Start Time",
            now_dt().strftime(
                "%I:%M:%S %p"
            )
        )

        due_date = self.field(
            grid,
            "Due Date",
            (
                now_dt()
                + datetime.timedelta(days=1)
            ).strftime(
                "%d-%m-%Y"
            )
        )

        due_time = self.field(
            grid,
            "Due Time",
            now_dt().strftime(
                "%I:%M:%S %p"
            )
        )

        for child in grid.winfo_children():

            if isinstance(
                child,
                tk.Entry
            ):

                child.pack(
                    side="left",
                    fill="x",
                    expand=True,
                    padx=5,
                    pady=(3, 8)
                )

        priority = self.field(
            form,
            "Priority",
            "Medium"
        )

        planned = self.field(
            form,
            "Planned Duration (minutes)",
            "30"
        )

        def add_task():

            task_name = name.get().strip()

            if not task_name:

                messagebox.showwarning(
                    "Task",
                    "Enter task name."
                )

                return

            try:

                start = parse_datetime(
                    start_date.get(),
                    start_time.get()
                )

                due = parse_datetime(
                    due_date.get(),
                    due_time.get()
                )

                if due <= start:

                    raise ValueError(
                        "Due date/time must be after "
                        "start date/time."
                    )

                planned_minutes = max(
                    1,
                    int(planned.get())
                )

            except Exception as error:

                messagebox.showerror(
                    "Invalid Details",
                    str(error)
                )

                return

            item = {

                "id": new_id(),

                "name": task_name,

                "start_date":
                    start_date.get().strip(),

                "start_time":
                    start_time.get().strip(),

                "due_date":
                    due_date.get().strip(),

                "due_time":
                    due_time.get().strip(),

                "due_datetime":
                    due.isoformat(),

                "priority":
                    priority.get().strip()
                    or "Medium",

                "planned_minutes":
                    planned_minutes,

                "actual_seconds":
                    0,

                "timer_running":
                    False,

                "timer_started_at":
                    None,

                "status":
                    "Pending",

                "reminder_24_sent":
                    False,

                "reminder_12_sent":
                    False
            }

            self.data["todos"].append(
                item
            )

            self.log_history(
                "Added",
                "To-Do",
                task_name,
                "Task created"
            )

            self.save_data()

            self.show_page(
                "Smart To-Do"
            )

        self.button(
            form,
            "Add Task",
            add_task,
            DARK["GREEN"]
        ).pack(
            anchor="e",
            padx=12,
            pady=10
        )

        tk.Label(
            frame,
            text="Active Tasks",
            bg=DARK["BG"],
            fg=DARK["WHITE"],
            font=("Segoe UI", 14, "bold")
        ).pack(
            anchor="w",
            padx=22,
            pady=(10, 5)
        )

        for item in self.data["todos"]:

            self.todo_card(
                item
            )

    # ========================================================
    # TODO CARD
    # ========================================================

    def todo_card(
        self,
        item
    ):

        card = self.card()

        card.pack(
            fill="x",
            padx=22,
            pady=6
        )

        top = tk.Frame(
            card,
            bg=DARK["CARD"]
        )

        top.pack(
            fill="x",
            padx=12,
            pady=(10, 2)
        )

        tk.Label(
            top,
            text=item["name"],
            bg=DARK["CARD"],
            fg=DARK["WHITE"],
            font=("Segoe UI", 12, "bold")
        ).pack(
            side="left"
        )

        if item.get(
            "status"
        ) == "Completed":

            status_color = DARK["GREEN"]

        elif item.get(
            "status"
        ) == "In Progress":

            status_color = DARK["CYAN"]

        else:

            status_color = DARK["MUTED"]

        status_label = tk.Label(
            top,
            text=item.get(
                "status",
                "Pending"
            ),
            bg=DARK["CARD"],
            fg=status_color,
            font=("Segoe UI", 9, "bold")
        )

        status_label.pack(
            side="right"
        )

        tk.Label(
            card,
            text=(
                f"Start: {item.get('start_date')} "
                f"{item.get('start_time')}   |   "
                f"Due: {item.get('due_date')} "
                f"{item.get('due_time')}   |   "
                f"Priority: {item.get('priority')}   |   "
                f"Planned: {item.get('planned_minutes')} min"
            ),
            bg=DARK["CARD"],
            fg=DARK["MUTED"],
            font=("Segoe UI", 8)
        ).pack(
            anchor="w",
            padx=12,
            pady=4
        )

        timer_label = tk.Label(
            card,
            text="Actual: 0 min 00 sec",
            bg=DARK["CARD"],
            fg=DARK["CYAN"],
            font=("Segoe UI", 13, "bold")
        )

        timer_label.pack(
            anchor="w",
            padx=12,
            pady=4
        )

        buttons = tk.Frame(
            card,
            bg=DARK["CARD"]
        )

        buttons.pack(
            anchor="e",
            padx=10,
            pady=(0, 10)
        )

        def start_timer():

            if item.get(
                "status"
            ) == "Completed":

                return

            if not item.get(
                "timer_running"
            ):

                item["timer_running"] = True

                item["timer_started_at"] = time.time()

                item["status"] = "In Progress"

                self.log_history(
                    "Started",
                    "To-Do",
                    item["name"]
                )

                self.save_data()

                status_label.config(
                    text="In Progress",
                    fg=DARK["CYAN"]
                )

        def pause_timer():

            self.accumulate_timer(
                item
            )

            item["timer_running"] = False

            item["timer_started_at"] = None

            if item.get(
                "status"
            ) != "Completed":

                item["status"] = "Pending"

            self.log_history(
                "Paused",
                "To-Do",
                item["name"],
                (
                    "Actual time: "
                    + format_seconds(
                        item.get(
                            "actual_seconds",
                            0
                        )
                    )
                )
            )

            self.save_data()

            status_label.config(
                text=item["status"],
                fg=DARK["MUTED"]
            )

        def complete_task():

            self.accumulate_timer(
                item
            )

            item["timer_running"] = False

            item["timer_started_at"] = None

            item["status"] = "Completed"

            self.log_history(
                "Completed",
                "To-Do",
                item["name"],
                (
                    "Actual time: "
                    + format_seconds(
                        item.get(
                            "actual_seconds",
                            0
                        )
                    )
                )
            )

            self.save_data()

            status_label.config(
                text="Completed",
                fg=DARK["GREEN"]
            )

        def delete_task():

            self.accumulate_timer(
                item
            )

            item["timer_running"] = False

            snapshot = json.dumps(
                item,
                ensure_ascii=False
            )

            self.log_history(
                "Deleted",
                "To-Do",
                item["name"],
                "Deleted task snapshot: "
                + snapshot
            )

            self.data["todos"] = [
                task
                for task in self.data["todos"]
                if task["id"] != item["id"]
            ]

            self.save_data()

            self.show_page(
                "Smart To-Do"
            )

        self.button(
            buttons,
            "Start",
            start_timer,
            DARK["GREEN"],
            8
        ).pack(
            side="left",
            padx=3
        )

        self.button(
            buttons,
            "Pause",
            pause_timer,
            DARK["ORANGE"],
            8
        ).pack(
            side="left",
            padx=3
        )

        self.button(
            buttons,
            "Completed",
            complete_task,
            DARK["PURPLE"],
            10
        ).pack(
            side="left",
            padx=3
        )

        self.button(
            buttons,
            "Delete",
            delete_task,
            DARK["RED"],
            8
        ).pack(
            side="left",
            padx=3
        )

        self.update_todo_timer(
            item,
            timer_label
        )

    # ========================================================
    # TODO TIMER
    # ========================================================

    def accumulate_timer(
        self,
        item
    ):

        if (
            item.get("timer_running")
            and
            item.get("timer_started_at")
        ):

            elapsed = (
                time.time()
                - item["timer_started_at"]
            )

            item["actual_seconds"] = (
                item.get(
                    "actual_seconds",
                    0
                )
                + max(
                    0,
                    elapsed
                )
            )

            item["timer_started_at"] = time.time()

    def update_todo_timer(
        self,
        item,
        label
    ):

        if not label.winfo_exists():

            return

        seconds = int(
            item.get(
                "actual_seconds",
                0
            )
        )

        if (
            item.get("timer_running")
            and
            item.get("timer_started_at")
        ):

            seconds += int(
                max(
                    0,
                    time.time()
                    - item["timer_started_at"]
                )
            )

        label.config(
            text=(
                "Actual: "
                + format_seconds(seconds)
            )
        )

        self.todo_refresh_job = self.root.after(
            1000,
            lambda:
            self.update_todo_timer(
                item,
                label
            )
        )

    # ========================================================
    # GENERIC DATE/TIME RECORD PAGES
    # ========================================================

    def page_records(
        self,
        key,
        title
    ):

        form = self.card()

        form.pack(
            fill="x",
            padx=22,
            pady=10
        )

        tk.Label(
            form,
            text=f"Add {title}",
            bg=DARK["CARD"],
            fg=DARK["WHITE"],
            font=("Segoe UI", 15, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=12
        )

        name = self.field(
            form,
            "Name / Title"
        )

        description = self.field(
            form,
            "Description"
        )

        row = tk.Frame(
            form,
            bg=DARK["CARD"]
        )

        row.pack(
            fill="x",
            padx=7
        )

        start_date = self.field(
            row,
            "Start Date",
            now_dt().strftime(
                "%d-%m-%Y"
            )
        )

        start_time = self.field(
            row,
            "Start Time",
            now_dt().strftime(
                "%I:%M:%S %p"
            )
        )

        end_date = self.field(
            row,
            "End / Due Date",
            (
                now_dt()
                + datetime.timedelta(days=1)
            ).strftime(
                "%d-%m-%Y"
            )
        )

        end_time = self.field(
            row,
            "End / Due Time",
            (
                now_dt()
                + datetime.timedelta(days=1)
            ).strftime(
                "%I:%M:%S %p"
            )
        )

        for widget in row.winfo_children():

            if isinstance(
                widget,
                tk.Entry
            ):

                widget.pack(
                    side="left",
                    fill="x",
                    expand=True,
                    padx=5
                )

        def add_record():

            try:

                start = parse_datetime(
                    start_date.get(),
                    start_time.get()
                )

                due = parse_datetime(
                    end_date.get(),
                    end_time.get()
                )

                if due <= start:

                    raise ValueError(
                        "End/Due date and time "
                        "must be after the "
                        "start date and time."
                    )

            except Exception as error:

                messagebox.showerror(
                    "Invalid Date/Time",
                    str(error)
                )

                return

            record_name = name.get().strip()

            if not record_name:

                messagebox.showwarning(
                    "Required",
                    "Enter a name/title."
                )

                return

            item = {

                "id": new_id(),

                "name":
                    record_name,

                "description":
                    description.get().strip(),

                "start_date":
                    start_date.get().strip(),

                "start_time":
                    start_time.get().strip(),

                "due_date":
                    end_date.get().strip(),

                "due_time":
                    end_time.get().strip(),

                "due_datetime":
                    due.isoformat(),

                "status":
                    "Pending",

                "reminder_24_sent":
                    False,

                "reminder_12_sent":
                    False,

                "created":
                    now_text()
            }

            self.data[key].append(
                item
            )

            self.log_history(
                "Added",
                title,
                record_name
            )

            self.save_data()

            self.show_page(
                title
            )

        self.button(
            form,
            "Save",
            add_record,
            DARK["GREEN"]
        ).pack(
            anchor="e",
            padx=12,
            pady=10
        )

        # ----------------------------------------------------
        # EXISTING RECORDS
        # ----------------------------------------------------

        for item in reversed(
            self.data.get(
                key,
                []
            )
        ):

            record_card = self.card()

            record_card.pack(
                fill="x",
                padx=22,
                pady=5
            )

            tk.Label(
                record_card,
                text=item.get(
                    "name",
                    ""
                ),
                bg=DARK["CARD"],
                fg=DARK["WHITE"],
                font=("Segoe UI", 11, "bold")
            ).pack(
                anchor="w",
                padx=12,
                pady=(10, 2)
            )

            tk.Label(
                record_card,
                text=(
                    f"{item.get('description', '')}\n"
                    f"Start: "
                    f"{item.get('start_date')} "
                    f"{item.get('start_time')}\n"
                    f"End/Due: "
                    f"{item.get('due_date')} "
                    f"{item.get('due_time')}\n"
                    f"Status: "
                    f"{item.get('status', 'Pending')}"
                ),
                bg=DARK["CARD"],
                fg=DARK["MUTED"],
                justify="left"
            ).pack(
                anchor="w",
                padx=12,
                pady=5
            )

            buttons = tk.Frame(
                record_card,
                bg=DARK["CARD"]
            )

            buttons.pack(
                anchor="e",
                padx=10,
                pady=(0, 10)
            )

            def complete_record(
                current_item=item
            ):

                current_item["status"] = "Completed"

                self.log_history(
                    "Completed",
                    title,
                    current_item["name"]
                )

                self.save_data()

                self.show_page(
                    title
                )

            self.button(
                buttons,
                "Completed",
                complete_record,
                DARK["GREEN"],
                10
            ).pack(
                side="left",
                padx=3
            )

            self.button(
                buttons,
                "Delete",
                lambda current_item=item:
                self.delete_generic(
                    key,
                    current_item,
                    title
                ),
                DARK["RED"],
                8
            ).pack(
                side="left",
                padx=3
            )

    # ========================================================
    # FACULTY & MENTORS
    #
    # NO DATE
    # NO START TIME
    # NO END TIME
    # NO DUE DATE
    # ========================================================

    def page_faculty(self):

        title = "Faculty & Mentors"
        key = "faculty"

        form = self.card()

        form.pack(
            fill="x",
            padx=22,
            pady=12
        )

        tk.Label(
            form,
            text="Add Faculty / Mentor",
            bg=DARK["CARD"],
            fg=DARK["WHITE"],
            font=("Segoe UI", 15, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=12
        )

        name = self.field(
            form,
            "Faculty / Mentor Name"
        )

        department = self.field(
            form,
            "Department / Subject"
        )

        contact = self.field(
            form,
            "Contact / Notes"
        )

        def save_faculty():

            faculty_name = name.get().strip()

            if not faculty_name:

                messagebox.showwarning(
                    "Faculty & Mentors",
                    "Enter the faculty or mentor name."
                )

                return

            item = {

                "id": new_id(),

                "name":
                    faculty_name,

                "values": {

                    "Department / Subject":
                        department.get().strip(),

                    "Contact / Notes":
                        contact.get().strip()
                },

                "created":
                    now_text()
            }

            self.data[key].append(
                item
            )

            self.log_history(
                "Added",
                title,
                faculty_name
            )

            self.save_data()

            self.show_page(
                title
            )

        self.button(
            form,
            "Save Faculty / Mentor",
            save_faculty,
            DARK["GREEN"]
        ).pack(
            anchor="e",
            padx=12,
            pady=10
        )

        # ----------------------------------------------------
        # EXISTING FACULTY
        # ----------------------------------------------------

        for item in reversed(
            self.data.get(
                key,
                []
            )
        ):

            faculty_card = self.card()

            faculty_card.pack(
                fill="x",
                padx=22,
                pady=5
            )

            tk.Label(
                faculty_card,
                text=item.get(
                    "name",
                    ""
                ),
                bg=DARK["CARD"],
                fg=DARK["WHITE"],
                font=("Segoe UI", 12, "bold")
            ).pack(
                anchor="w",
                padx=12,
                pady=(10, 3)
            )

            values = item.get(
                "values",
                {}
            )

            details = "\n".join(
                f"{field}: {value}"
                for field, value
                in values.items()
                if value
            )

            if not details:

                details = "No additional information."

            tk.Label(
                faculty_card,
                text=details,
                bg=DARK["CARD"],
                fg=DARK["MUTED"],
                justify="left"
            ).pack(
                anchor="w",
                padx=12,
                pady=(0, 8)
            )

            self.button(
                faculty_card,
                "Delete",
                lambda current_item=item:
                self.delete_generic(
                    key,
                    current_item,
                    title
                ),
                DARK["RED"],
                8
            ).pack(
                anchor="e",
                padx=10,
                pady=(0, 10)
            )

    # ========================================================
    # GOALS & HABITS
    #
    # NO DATE
    # NO START TIME
    # NO END TIME
    # NO DUE DATE
    # ========================================================

    def page_goals(self):

        title = "Goals & Habits"
        key = "goals"

        form = self.card()

        form.pack(
            fill="x",
            padx=22,
            pady=12
        )

        tk.Label(
            form,
            text="Add Goal / Habit",
            bg=DARK["CARD"],
            fg=DARK["WHITE"],
            font=("Segoe UI", 15, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=12
        )

        name = self.field(
            form,
            "Goal / Habit Name"
        )

        description = self.field(
            form,
            "Description"
        )

        target = self.field(
            form,
            "Target / Frequency"
        )

        def save_goal():

            goal_name = name.get().strip()

            if not goal_name:

                messagebox.showwarning(
                    "Goals & Habits",
                    "Enter a goal or habit name."
                )

                return

            item = {

                "id": new_id(),

                "name":
                    goal_name,

                "values": {

                    "Description":
                        description.get().strip(),

                    "Target / Frequency":
                        target.get().strip()
                },

                "status":
                    "Active",

                "created":
                    now_text()
            }

            self.data[key].append(
                item
            )

            self.log_history(
                "Added",
                title,
                goal_name
            )

            self.save_data()

            self.show_page(
                title
            )

        self.button(
            form,
            "Save Goal / Habit",
            save_goal,
            DARK["GREEN"]
        ).pack(
            anchor="e",
            padx=12,
            pady=10
        )

        # ----------------------------------------------------
        # EXISTING GOALS
        # ----------------------------------------------------

        for item in reversed(
            self.data.get(
                key,
                []
            )
        ):

            goal_card = self.card()

            goal_card.pack(
                fill="x",
                padx=22,
                pady=5
            )

            top = tk.Frame(
                goal_card,
                bg=DARK["CARD"]
            )

            top.pack(
                fill="x",
                padx=12,
                pady=(10, 3)
            )

            tk.Label(
                top,
                text=item.get(
                    "name",
                    ""
                ),
                bg=DARK["CARD"],
                fg=DARK["WHITE"],
                font=("Segoe UI", 12, "bold")
            ).pack(
                side="left"
            )

            status = item.get(
                "status",
                "Active"
            )

            status_color = (
                DARK["GREEN"]
                if status == "Completed"
                else DARK["CYAN"]
            )

            status_label = tk.Label(
                top,
                text=status,
                bg=DARK["CARD"],
                fg=status_color,
                font=("Segoe UI", 9, "bold")
            )

            status_label.pack(
                side="right"
            )

            values = item.get(
                "values",
                {}
            )

            details = "\n".join(
                f"{field}: {value}"
                for field, value
                in values.items()
                if value
            )

            if not details:

                details = "No additional information."

            tk.Label(
                goal_card,
                text=details,
                bg=DARK["CARD"],
                fg=DARK["MUTED"],
                justify="left"
            ).pack(
                anchor="w",
                padx=12,
                pady=(0, 8)
            )

            buttons = tk.Frame(
                goal_card,
                bg=DARK["CARD"]
            )

            buttons.pack(
                anchor="e",
                padx=10,
                pady=(0, 10)
            )

            def complete_goal(
                current_item=item,
                current_status_label=status_label
            ):

                current_item["status"] = "Completed"

                self.log_history(
                    "Completed",
                    title,
                    current_item.get(
                        "name",
                        ""
                    )
                )

                self.save_data()

                current_status_label.config(
                    text="Completed",
                    fg=DARK["GREEN"]
                )

            self.button(
                buttons,
                "Completed",
                complete_goal,
                DARK["GREEN"],
                10
            ).pack(
                side="left",
                padx=3
            )

            self.button(
                buttons,
                "Delete",
                lambda current_item=item:
                self.delete_generic(
                    key,
                    current_item,
                    title
                ),
                DARK["RED"],
                8
            ).pack(
                side="left",
                padx=3
            )

    # ========================================================
    # DELETE GENERIC
    # ========================================================

    def delete_generic(
        self,
        key,
        item,
        title
    ):

        snapshot = json.dumps(
            item,
            ensure_ascii=False
        )

        self.log_history(
            "Deleted",
            title,
            item.get(
                "name",
                ""
            ),
            "Deleted snapshot: "
            + snapshot
        )

        self.data[key] = [
            x
            for x in self.data[key]
            if x.get("id")
            != item.get("id")
        ]

        self.save_data()

        self.show_page(
            title
        )

    # ========================================================
    # ATTENDANCE
    # ========================================================

    def page_attendance(self):

        self.simple_form_page(
            "Attendance",
            "attendance",
            [
                "Subject",
                "Classes Held",
                "Classes Attended"
            ]
        )

    # ========================================================
    # PROGRESS
    # ========================================================

    def page_progress(self):

        self.simple_form_page(
            "Academic Progress",
            "progress",
            [
                "Subject / Skill",
                "Current Progress",
                "Target"
            ]
        )

    # ========================================================
    # EXPENSES
    # ========================================================

    def page_expenses(self):

        self.simple_form_page(
            "Expense Tracker",
            "expenses",
            [
                "Expense Name",
                "Amount",
                "Category"
            ]
        )

    # ========================================================
    # DOCUMENTS
    # ========================================================

    def page_documents(self):

        self.simple_form_page(
            "Document Manager",
            "documents",
            [
                "Document Name",
                "Document Type",
                "Location / Note"
            ]
        )

    # ========================================================
    # FEEDBACK
    # ========================================================

    def page_feedback(self):

        self.simple_form_page(
            "Feedback & Help",
            "feedback",
            [
                "Topic",
                "Feedback / Question",
                "Priority"
            ]
        )

    # ========================================================
    # SIMPLE FORM
    # ========================================================

    def simple_form_page(
        self,
        title,
        key,
        fields
    ):

        form = self.card()

        form.pack(
            fill="x",
            padx=22,
            pady=12
        )

        tk.Label(
            form,
            text=f"Add {title}",
            bg=DARK["CARD"],
            fg=DARK["WHITE"],
            font=("Segoe UI", 15, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=12
        )

        entries = []

        for field_name in fields:

            entries.append(
                self.field(
                    form,
                    field_name
                )
            )

        def save_record():

            values = [
                entry.get().strip()
                for entry in entries
            ]

            if not values[0]:

                messagebox.showwarning(
                    title,
                    f"Enter {fields[0]}."
                )

                return

            item = {

                "id": new_id(),

                "name":
                    values[0],

                "values":
                    dict(
                        zip(
                            fields[1:],
                            values[1:]
                        )
                    ),

                "created":
                    now_text()
            }

            self.data[key].append(
                item
            )

            self.log_history(
                "Added",
                title,
                values[0],
                json.dumps(
                    item,
                    ensure_ascii=False
                )
            )

            self.save_data()

            self.show_page(
                title
            )

        self.button(
            form,
            "Save",
            save_record,
            DARK["GREEN"]
        ).pack(
            anchor="e",
            padx=12,
            pady=10
        )

        for item in reversed(
            self.data.get(
                key,
                []
            )
        ):

            record_card = self.card()

            record_card.pack(
                fill="x",
                padx=22,
                pady=4
            )

            text = item.get(
                "name",
                ""
            )

            if "values" in item:

                text += "\n"

                text += " | ".join(
                    f"{field}: {value}"
                    for field, value
                    in item["values"].items()
                )

            tk.Label(
                record_card,
                text=text,
                bg=DARK["CARD"],
                fg=DARK["WHITE"],
                justify="left"
            ).pack(
                side="left",
                padx=12,
                pady=10
            )

            self.button(
                record_card,
                "Delete",
                lambda current_item=item:
                self.delete_generic(
                    key,
                    current_item,
                    title
                ),
                DARK["RED"],
                8
            ).pack(
                side="right",
                padx=10
            )

    # ========================================================
    # REMINDER SYSTEM
    #
    # 24 HOURS BEFORE
    # 12 HOURS BEFORE
    #
    # Faculty & Goals have no due_datetime,
    # therefore they are automatically ignored.
    # ========================================================

    def check_reminders(self):

        current_time = now_dt()

        collections = []

        for key in DEFAULT_DATA:

            if isinstance(
                self.data.get(key),
                list
            ):

                collections.append(
                    (
                        key,
                        key.replace(
                            "_",
                            " "
                        ).title()
                    )
                )

        reminder_messages = []

        changed = False

        for key, title in collections:

            for item in self.data.get(
                key,
                []
            ):

                if not item.get(
                    "due_date"
                ):

                    continue

                if not item.get(
                    "due_time"
                ):

                    continue

                try:

                    due_time = parse_datetime(
                        item["due_date"],
                        item["due_time"]
                    )

                except Exception:

                    continue

                if item.get(
                    "status"
                ) == "Completed":

                    continue

                seconds_remaining = (
                    due_time
                    - current_time
                ).total_seconds()

                # =================================================
                # 24 HOUR REMINDER
                # =================================================

                if (
                    seconds_remaining <= 86400
                    and
                    seconds_remaining > 43200
                    and
                    not item.get(
                        "reminder_24_sent",
                        False
                    )
                ):

                    item[
                        "reminder_24_sent"
                    ] = True

                    reminder_messages.append(
                        "24-HOUR REMINDER\n"
                        f"{item.get('name', 'Unnamed')}\n"
                        f"Ends/Due: "
                        f"{due_time.strftime('%d-%m-%Y %I:%M %p')}"
                    )

                    self.data[
                        "history"
                    ].append({

                        "id": new_id(),

                        "action":
                            "24-hour reminder",

                        "item_type":
                            title,

                        "item_name":
                            item.get(
                                "name",
                                ""
                            ),

                        "details":
                            "Automatic 24-hour reminder",

                        "timestamp":
                            now_text()
                    })

                    changed = True

                # =================================================
                # 12 HOUR REMINDER
                # =================================================

                if (
                    seconds_remaining <= 43200
                    and
                    seconds_remaining > 0
                    and
                    not item.get(
                        "reminder_12_sent",
                        False
                    )
                ):

                    item[
                        "reminder_12_sent"
                    ] = True

                    reminder_messages.append(
                        "12-HOUR REMINDER\n"
                        f"{item.get('name', 'Unnamed')}\n"
                        f"Ends/Due: "
                        f"{due_time.strftime('%d-%m-%Y %I:%M %p')}"
                    )

                    self.data[
                        "history"
                    ].append({

                        "id": new_id(),

                        "action":
                            "12-hour reminder",

                        "item_type":
                            title,

                        "item_name":
                            item.get(
                                "name",
                                ""
                            ),

                        "details":
                            "Automatic 12-hour reminder",

                        "timestamp":
                            now_text()
                    })

                    changed = True

        if changed:

            self.save_data()

            messagebox.showinfo(
                "SMART STUDENT HUB Reminder",
                "\n\n".join(
                    reminder_messages
                )
            )

        self.reminder_job = self.root.after(
            30000,
            self.check_reminders
        )

    # ========================================================
    # SETTINGS
    # ========================================================

    def page_settings(self):

        card = self.card()

        card.pack(
            fill="x",
            padx=22,
            pady=20
        )

        tk.Label(
            card,
            text="Settings",
            bg=DARK["CARD"],
            fg=DARK["WHITE"],
            font=("Segoe UI", 17, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=15
        )

        tk.Label(
            card,
            text=(
                f"Application: {APP_NAME}\n"
                f"Student: {STUDENT_NAME}\n"
                f"Data file: "
                f"{os.path.abspath(DATA_FILE)}"
            ),
            bg=DARK["CARD"],
            fg=DARK["MUTED"],
            justify="left"
        ).pack(
            anchor="w",
            padx=15,
            pady=10
        )

        self.button(
            card,
            "Save Data Now",
            self.manual_save,
            DARK["GREEN"]
        ).pack(
            anchor="w",
            padx=15,
            pady=8
        )

        self.button(
            card,
            "Clear Active Tasks",
            self.clear_active_tasks,
            DARK["RED"]
        ).pack(
            anchor="w",
            padx=15,
            pady=(0, 15)
        )

    def manual_save(self):

        self.save_data()

        messagebox.showinfo(
            "Saved",
            "All data has been saved."
        )

    def clear_active_tasks(self):

        answer = messagebox.askyesno(
            "Confirm",
            "Delete all active To-Do tasks?\n\n"
            "They will remain permanently in History."
        )

        if not answer:

            return

        for item in list(
            self.data["todos"]
        ):

            self.log_history(
                "Deleted",
                "To-Do",
                item.get(
                    "name",
                    ""
                ),
                "Bulk deletion snapshot: "
                + json.dumps(
                    item,
                    ensure_ascii=False
                )
            )

        self.data["todos"] = []

        self.save_data()

        self.show_page(
            "Settings"
        )

    # ========================================================
    # HISTORY
    # ========================================================

    def page_history(self):

        card = self.card()

        card.pack(
            fill="x",
            padx=22,
            pady=12
        )

        tk.Label(
            card,
            text="Permanent Activity History",
            bg=DARK["CARD"],
            fg=DARK["WHITE"],
            font=("Segoe UI", 16, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=12
        )

        tk.Label(
            card,
            text=(
                "Deleted tasks, completed activities, "
                "timers, reminders and other actions "
                "remain stored here."
            ),
            bg=DARK["CARD"],
            fg=DARK["MUTED"]
        ).pack(
            anchor="w",
            padx=15,
            pady=(0, 10)
        )

        if not self.data["history"]:

            tk.Label(
                card,
                text="No history yet.",
                bg=DARK["CARD"],
                fg=DARK["MUTED"]
            ).pack(
                anchor="w",
                padx=15,
                pady=15
            )

        for history in reversed(
            self.data["history"]
        ):

            history_row = tk.Frame(
                card,
                bg=DARK["CARD2"]
            )

            history_row.pack(
                fill="x",
                padx=10,
                pady=3
            )

            tk.Label(
                history_row,
                text=(
                    f"{history.get('timestamp', '')}"
                    f"  |  "
                    f"{history.get('action', '')}"
                    f"  |  "
                    f"{history.get('item_type', '')}"
                    f"  |  "
                    f"{history.get('item_name', '')}"
                ),
                bg=DARK["CARD2"],
                fg=DARK["WHITE"],
                font=("Segoe UI", 9, "bold")
            ).pack(
                anchor="w",
                padx=8,
                pady=(7, 2)
            )

            tk.Label(
                history_row,
                text=history.get(
                    "details",
                    ""
                ),
                bg=DARK["CARD2"],
                fg=DARK["MUTED"],
                wraplength=850,
                justify="left"
            ).pack(
                anchor="w",
                padx=8,
                pady=(0, 7)
            )

    # ========================================================
    # CLOCK
    # ========================================================

    def update_clock(self):

        self.clock_label.config(
            text=now_dt().strftime(
                "%A, %d %B %Y  •  %I:%M:%S %p"
            )
        )

        self.clock_job = self.root.after(
            1000,
            self.update_clock
        )

    # ========================================================
    # CLOSE APPLICATION
    # ========================================================

    def close_app(self):

        # Save running timer time

        for item in self.data.get(
            "todos",
            []
        ):

            if item.get(
                "timer_running"
            ):

                self.accumulate_timer(
                    item
                )

        self.save_data()

        try:

            if self.clock_job:

                self.root.after_cancel(
                    self.clock_job
                )

            if self.reminder_job:

                self.root.after_cancel(
                    self.reminder_job
                )

            if self.todo_refresh_job:

                self.root.after_cancel(
                    self.todo_refresh_job
                )

        except Exception:
            pass

        self.root.destroy()


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = SmartStudentHub(
        root
    )

    root.mainloop()