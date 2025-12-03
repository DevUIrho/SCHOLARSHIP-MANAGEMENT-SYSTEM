import customtkinter as ctk
import tkinter as tk
import webbrowser
import subprocess
import sys

# ---------------- CONFIG ----------------
ctk.set_appearance_mode("light")
MAROON       = "#7B1113"
MAROON_DARK  = "#5B0E0F"
CARD_BORDER  = "#E6E6E6"
BG           = "#FAFAFA"
TEXT         = "#1E1E1E"
SUBDUED      = "#636363"
ACTIVE_BG    = "#800000"
ACTIVE_HOVER = "#A52A2A"

# ---------------- SAMPLE DATA ----------------
announcements = [
    {
        "title": "CHED Full Scholarship Opening",
        "description": "Applications for CHED Full Scholarship 2025 are now open. Submit all requirements before July 30.",
        "link": "https://ched.gov.ph/scholarships"
    },
    {
        "title": "Provincial Scholarship Deadline Extended",
        "description": "The Provincial Government of Batangas extended the scholarship application deadline until August 15.",
        "link": "https://batangas.gov.ph/scholarship"
    },
]

# ---------------- CREATE ANNOUNCEMENT CARD ----------------
def create_announcement_card(parent, title, description, link=None):
    card = ctk.CTkFrame(parent, fg_color="white", corner_radius=16, border_width=1, border_color=CARD_BORDER)
    card.pack(fill="x", pady=10, padx=16)

    ctk.CTkLabel(card, text=title, font=("Segoe UI", 16, "bold"), text_color=MAROON, wraplength=600).pack(anchor="w", pady=(10,5), padx=10)
    ctk.CTkLabel(card, text=description, font=("Segoe UI", 13), text_color=TEXT, wraplength=600, justify="left").pack(anchor="w", pady=(0,10), padx=10)
    
    if link:
        ctk.CTkButton(card, text="Read More", command=lambda: webbrowser.open(link), font=("Segoe UI", 12)).pack(anchor="w", pady=(0,10), padx=10)

# ---------------- SCROLLABLE FRAME ----------------
class ScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.pack(fill="both", expand=True)

# ---------------- MAIN ANNOUNCEMENT APP ----------------
class AnnouncementApp(ctk.CTk):
    def __init__(self, username="example_user"):
        super().__init__()
        self.username = username
        self.title("Scholarship Announcements")
        self.geometry("1100x720")
        self.minsize(960,640)
        self.configure(fg_color=BG)

        # ---------------- HEADER ----------------
        self.header = ctk.CTkFrame(self, fg_color=MAROON, height=110, corner_radius=0)
        self.header.pack(fill="x")
        ctk.CTkLabel(self.header, text="SCHOLARSHIP ANNOUNCEMENTS",
                     font=("Arial Black",28), text_color="white").pack(pady=25)

        # ---------------- SIDEBAR ----------------
        self.sidebar = ctk.CTkFrame(self, width=250, fg_color="white", corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        sidebar_center = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        sidebar_center.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            sidebar_center,
            text="NAVIGATION",
            font=("Segoe UI", 18, "bold"),
            text_color=MAROON
        ).pack(pady=(0,20))

        self.buttons = {}

        # ---------------- FUNCTIONS ----------------
        def open_dashboard():
            self.destroy()
            subprocess.Popen([sys.executable, "maintainersdashboard.py", self.username])

        def nav_btn(key, text, command=None):
            active = key == "announcements"
            fg = ACTIVE_BG if active else "#EFEFEF"
            hover = ACTIVE_HOVER if active else "#F5F5F5"
            txt_color = "white" if active else MAROON
            btn = ctk.CTkButton(
                sidebar_center, text=text,
                fg_color=fg,
                hover_color=hover,
                text_color=txt_color,
                anchor="w",
                width=200,
                height=45,
                corner_radius=20,
                font=("Helvetica", 14, "bold"),
                command=command
            )
            btn.pack(pady=6)
            self.buttons[key] = btn

        # ---------------- CREATE SIDEBAR BUTTONS ----------------
        nav_btn("dashboard", "📊 Dashboard", command=open_dashboard)
        nav_btn("announcements", "📢 Announcements", command=self.show_announcements)
        nav_btn("profile", "👤 Profile Settings", command=self.show_profile)

        logout_btn = ctk.CTkButton(sidebar_center, text="🚪 Logout",
                                   fg_color=ACTIVE_BG, hover_color=ACTIVE_HOVER,
                                   text_color="white", width=200, height=45,
                                   corner_radius=20, font=("Helvetica", 14, "bold"),
                                   command=self.destroy)
        logout_btn.pack(pady=(25,0))

        # ---------------- BODY ----------------
        self.body = ctk.CTkFrame(self, fg_color=BG)
        self.body.pack(side="left", fill="both", expand=True)

        self.content_frame = ScrollableFrame(self.body)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Default page: announcements
        self.show_announcements()

    # ---------------- PAGE FUNCTIONS ----------------
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def set_active_button(self, key):
        for k, btn in self.buttons.items():
            if k == key:
                btn.configure(fg_color=ACTIVE_BG, hover_color=ACTIVE_HOVER, text_color="white")
            else:
                btn.configure(fg_color="#EFEFEF", hover_color="#F5F5F5", text_color=MAROON)

    def show_announcements(self):
        self.clear_content()
        self.set_active_button("announcements")
        self.header.children['!ctklabel'].configure(text="SCHOLARSHIP ANNOUNCEMENTS")
        for item in announcements:
            create_announcement_card(self.content_frame, item["title"], item["description"], item.get("link"))

    def show_profile(self):
        self.clear_content()
        self.set_active_button("profile")
        self.header.children['!ctklabel'].configure(text="PROFILE SETTINGS")
        tk.Label(self.content_frame, text="Profile Page Placeholder", font=("Segoe UI", 18)).pack(pady=20)

# ---------------- RUN ----------------
if __name__ == "__main__":
    username = "example_user"  # replace with real username from login
    app = AnnouncementApp(username=username)
    app.after(100, lambda: app.state("zoomed"))
    app.mainloop()
