import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import sys
import webbrowser
import subprocess
import hashlib
from PIL import Image, ImageTk

# ----------------------- COLORS -----------------------
MAROON       = "#7B1113"
MAROON_DARK  = "#5B0E0F"
CARD_BORDER  = "#E6E6E6"
BG           = "#FAFAFA"
TEXT         = "#1E1E1E"
SUBDUED      = "#636363"
ACTIVE_BG    = "#800000"
ACTIVE_HOVER = "#A52A2A"

ctk.set_appearance_mode("light")

# ----------------------- DATABASE -----------------------
DB_FILE = "Scholarship.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def get_maintainer_by_studentid(student_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT student_id, name, username, email, school, course, yearlevel, phone_number, gwa, status
        FROM Maintainer
        WHERE student_id=?
    """, (student_id,))
    row = c.fetchone()
    conn.close()
    if row:
        parts = row[1].split()
        initials = "".join([p[0] for p in parts[:2]]).upper()
        return {
            "student_id": row[0],
            "initials": initials,
            "name": row[1],
            "maintainer_no": row[0],
            "program": f"{row[6]} ({row[5]})",
            "year": row[6],
            "status": row[9],
            "username": row[2],
            "email": row[3],
            "phone": row[7],
            "gwa": row[8],
        }
    return None

def get_maintainer_by_username(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT student_id, name, username, email, school, course, yearlevel, phone_number, gwa, status 
        FROM Maintainer
        WHERE username=?
    """, (username,))
    row = c.fetchone()
    conn.close()
    if row:
        parts = row[1].split()
        initials = "".join([p[0] for p in parts[:2]]).upper()
        return {
            "student_id": row[0],
            "initials": initials,
            "name": row[1],
            "maintainer_no": row[0],
            "program": f"{row[6]} ({row[5]})",
            "year": row[6],
            "status": row[9],
            "username": row[2],
            "email": row[3],
            "phone": row[7],
            "gwa": row[8],
            "avatar_path": row[10]
        }
    return None

def get_maintainer_requirements(students_id):
    """
    Check if requirements exist as BLOB data (not just 0 or 1)
    Returns a dictionary with True if BLOB exists, False otherwise
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT COR, TOR, GOOD_MORAL
        FROM Maintainer_Requirements
        WHERE maintainer_id = ?
    """, (students_id,))
    row = c.fetchone()
    conn.close()
    
    requirements = {
        "COR (Certificate of Registration)": False,
        "Grades (Previous Semester)": False,
        "Good Moral Certificate": False
    }
    
    if row:
        # Check if BLOB data exists (not None and not empty)
        requirements["COR (Certificate of Registration)"] = bool(row[0])
        requirements["Grades (Previous Semester)"] = bool(row[1])
        requirements["Good Moral Certificate"] = bool(row[2])
    
    return requirements

# ----------------------- COMPONENTS -----------------------
class Tag(ctk.CTkLabel):
    """Status pill"""
    def __init__(self, master, text="PENDING", fg="#FFF2CC", text_color=MAROON):
        super().__init__(master, text=text, fg_color=fg, text_color=text_color,
                         corner_radius=999, padx=12, pady=6)

class AvatarCanvas(tk.Canvas):
    """Big square avatar with initials or image."""
    def __init__(self, master, initials="JD", size=200,
                 bg_color="white", square_color="#F2E7E7",
                 text_color=MAROON):
        super().__init__(master, width=size, height=size,
                         highlightthickness=0, bg=bg_color)
        self.size = size
        self.square_color = square_color
        self.text_color = text_color
        self.initials = initials
        self._img_ref = None
        self.draw_initials()

    def draw_initials(self):
        self.delete("all")
        self.create_rectangle(2, 2, self.size-2, self.size-2, fill=self.square_color, outline=self.square_color)
        self.create_text(self.size/2, self.size/2, text=self.initials,
                         font=("Segoe UI", int(self.size/2.8), "bold"),
                         fill=self.text_color, tags="initials")

    def set_image(self, path):
        try:
            img = Image.open(path).convert("RGBA")
            # resize and crop to square
            w, h = img.size
            s = min(w, h)
            left = (w - s)//2
            top = (h - s)//2
            img = img.crop((left, top, left+s, top+s))
            img = img.resize((self.size-4, self.size-4), Image.LANCZOS)
            tkimg = ImageTk.PhotoImage(img)
            self.delete("all")
            self.create_image(self.size/2, self.size/2, image=tkimg)
            self._img_ref = tkimg
        except Exception as e:
            # fallback to initials if image fails
            self.draw_initials()

# ---------------------------------------------------------
# MAINTAINER DASHBOARD CARD
# ---------------------------------------------------------
class MaintainerDashboard(ctk.CTkFrame):
    def __init__(self, master, maintainer, **kwargs):
        super().__init__(master, fg_color="white", corner_radius=16,
                         border_width=1, border_color=CARD_BORDER, **kwargs)
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text="MAINTAINER DASHBOARD",
                     text_color=MAROON, font=("Segoe UI",18,"bold")).grid(
                        row=0, column=0, columnspan=2,
                        sticky="w", padx=18, pady=(16,6))

        AvatarCanvas(self, initials=maintainer["initials"]).grid(
            row=1, column=0, rowspan=8, sticky="nw", padx=18, pady=4
        )

        ctk.CTkLabel(self, text=maintainer["name"],
                     font=("Segoe UI",20,"bold"),
                     text_color=ACTIVE_BG).grid(row=1, column=1, sticky="w", padx=6, pady=(6,2))

        def row(label, value, r):
            ctk.CTkLabel(self, text=label, text_color=SUBDUED,
                         font=("Segoe UI",13)).grid(row=r, column=1,
                         sticky="w", padx=6)
            ctk.CTkLabel(self, text=value, text_color=TEXT,
                         font=("Segoe UI",13,"bold")).grid(
                            row=r, column=1, sticky="w", padx=160
                         )

        row("Maintainer No.:", maintainer["maintainer_no"], 2)
        row("Program:", maintainer["program"], 3)
        row("Year Level:", str(maintainer["year"]), 4)
        row("Username:", maintainer["username"], 5)
        row("Email:", maintainer["email"], 6)
        row("Phone:", maintainer["phone"], 7)
        row("GWA:", str(maintainer["gwa"]), 8)

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=9, column=1, sticky="e", padx=18, pady=(12,12))

        status = maintainer["status"]
        color_map = {"APPROVED": "#DAF1DD", "PENDING": "#FFF2CC", "REJECTED": "#FCE5E5"}
        status_text_color = MAROON if status != "REJECTED" else "#B00020"

        Tag(container, text=f"STATUS: {status}",
            fg=color_map.get(status, "#FFF2CC"),
            text_color=status_text_color).pack(side="left", padx=(0,10))



# ---------------------------------------------------------
# SCROLLABLE FRAME WRAPPER
# ---------------------------------------------------------
# ---------------------------------------------------------
# SCHOLARSHIPS SECTION WITH UPLOAD
# ---------------------------------------------------------
from tkinter import filedialog
import os

class ScholarshipsAvailable(ctk.CTkFrame):
    def __init__(self, master, maintainer_id=None, **kwargs):
        super().__init__(master, fg_color="white", corner_radius=16,
                         border_width=1, border_color=CARD_BORDER, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.maintainer_id = maintainer_id

        ctk.CTkLabel(self, text="SCHOLARSHIP AVAILABLE",
                     text_color=MAROON,
                     font=("Segoe UI",18,"bold")).grid(
                        row=0, column=0, sticky="w",
                        padx=18, pady=(16,10))

        # Main card
        self.card = ctk.CTkFrame(self, fg_color="white",
                                 corner_radius=14, border_width=1,
                                 border_color=CARD_BORDER)
        self.card.grid(row=1, column=0, sticky="nsew", padx=12, pady=(2,16))
        self.card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.card,
                     text="GOVERNOR VILMA SANTOS-RECTO EDUCATIONAL ASSISTANCE",
                     wraplength=480, text_color=TEXT,
                     font=("Segoe UI",16,"bold")).grid(
                        row=0, column=0, sticky="n", padx=16, pady=(14,6))

        # Load status from database
        if maintainer_id:
            self.status = get_maintainer_requirements(maintainer_id)
        else:
            self.status = {
                "COR (Certificate of Registration)": False,
                "Grades (Previous Semester)": False,
                "Good Moral Certificate": False
            }

        # ---------------- Progress Section ----------------
        self.progress_section = ctk.CTkFrame(self.card, fg_color="transparent")
        self.progress_section.grid(row=1, column=0, sticky="ew", padx=16, pady=(6,12))
        self.progress_section.grid_columnconfigure(0, weight=1)

        self.pb = ctk.CTkProgressBar(self.progress_section, height=12)
        self.pb.grid(row=1,column=0,sticky="ew", pady=(4,2))

        self.pct_label = ctk.CTkLabel(self.progress_section, text="0%", text_color=SUBDUED, font=("Segoe UI",12))
        self.pct_label.grid(row=2,column=0, sticky="n", pady=(2,0))

        self.legend_frame = ctk.CTkFrame(self.progress_section, fg_color="transparent")
        self.legend_frame.grid(row=3, column=0, sticky="w", pady=(8,2))

        self.refresh_progress()

        # ---------------- BUTTONS ----------------
        self.upload_btn_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.upload_btn_frame.grid(row=2, column=0, sticky="ew", padx=12, pady=(10,16))
        self.upload_btn_frame.grid_columnconfigure(0, weight=1)

        self.upload_btn = ctk.CTkButton(
            self.upload_btn_frame,
            text="UPLOAD REQUIREMENTS",
            fg_color=MAROON,
            hover_color="#A52A2A",
            text_color="white",
            command=self.show_upload_form
        )
        self.upload_btn.pack()


    # ---------------- REFRESH PROGRESS ----------------
    def refresh_progress(self):
        completed = sum(1 for v in self.status.values() if v)
        total = len(self.status)
        progress_value = completed / total
        self.pb.set(progress_value)
        self.pct_label.configure(text=f"{int(progress_value*100)}%")

        for widget in self.legend_frame.winfo_children():
            widget.destroy()

        for doc, done in self.status.items():
            row_frame = ctk.CTkFrame(self.legend_frame, fg_color="transparent")
            row_frame.pack(anchor="w", pady=2)
            icon = "🟩" if done else "🟥"
            text_color = "green" if done else "red"
            ctk.CTkLabel(row_frame, text=icon, font=("Segoe UI",18)).pack(side="left", padx=(0,8))
            ctk.CTkLabel(row_frame, text=doc, text_color=TEXT, font=("Segoe UI",13,"bold")).pack(side="left")
            ctk.CTkLabel(row_frame, text=f"– {'Completed' if done else 'Not Submitted'}", text_color=text_color, font=("Segoe UI",12)).pack(side="left", padx=(6,0))

    # ---------------- UPLOAD FORM ----------------
    def show_upload_form(self):
        self.upload_frame = ctk.CTkFrame(self.card, fg_color="white")
        self.upload_frame.grid(row=1, column=0, sticky="nsew")
        self.upload_frame.grid_columnconfigure(0, weight=1)
        self.upload_frame.grid_rowconfigure(0, weight=1)

        container = ctk.CTkFrame(self.upload_frame, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        self.entries = {}
        self.uploaded_files = {}
        for doc in ["COR", "Grades", "Good Moral"]:
            row = ctk.CTkFrame(container, fg_color="white")
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=doc, text_color=MAROON, font=("Segoe UI",13,"bold")).pack(side="left", padx=(0,10))
            entry = ctk.CTkEntry(row, width=250)
            entry.pack(side="left", padx=(0,10))
            self.entries[doc] = entry
            ctk.CTkButton(row, text="Browse", fg_color=MAROON, hover_color="#A52A2A", command=lambda d=doc: self.browse_file(d)).pack(side="left")

        # Submit & Back buttons
        btn_row = ctk.CTkFrame(container, fg_color="transparent")
        btn_row.pack(pady=16)
        ctk.CTkButton(btn_row, text="Submit", fg_color=MAROON, hover_color="#A52A2A", command=self.submit_files).pack(side="left", padx=10)
        ctk.CTkButton(btn_row, text="Back", fg_color="#EFEFEF", text_color=MAROON, hover_color="#E5E5E5", command=self.back_to_card).pack(side="left", padx=10)

    def browse_file(self, doc):
        file_path = filedialog.askopenfilename(title=f"Select {doc} File", filetypes=[("PDF Files","*.pdf")])
        if file_path:
            self.entries[doc].delete(0, "end")
            self.entries[doc].insert(0, os.path.basename(file_path))
            self.uploaded_files[doc] = file_path

    def submit_files(self):
        if not self.uploaded_files:
            messagebox.showerror("Error", "No files selected!")
            return
        
        if not self.maintainer_id:
            messagebox.showerror("Error", "No maintainer ID found!")
            return
        
        # Ensure maintainer_id is a string (student ID format like '2024002')
        maintainer_id_str = str(self.maintainer_id)
        
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            
            # Check if record exists
            c.execute("SELECT COR, TOR, GOOD_MORAL FROM Maintainer_Requirements WHERE maintainer_id = ?", (maintainer_id_str,))
            row = c.fetchone()
            
            # Get existing BLOBs or None
            existing_cor = row[0] if row else None
            existing_tor = row[1] if row else None
            existing_moral = row[2] if row else None
            
            # Read new files as BLOB (binary data)
            cor_blob = existing_cor
            tor_blob = existing_tor
            moral_blob = existing_moral
            
            if "COR" in self.uploaded_files:
                with open(self.uploaded_files["COR"], 'rb') as f:
                    cor_blob = f.read()
            
            if "Grades" in self.uploaded_files:
                with open(self.uploaded_files["Grades"], 'rb') as f:
                    tor_blob = f.read()
            
            if "Good Moral" in self.uploaded_files:
                with open(self.uploaded_files["Good Moral"], 'rb') as f:
                    moral_blob = f.read()
            
            if row:
                # Update existing record
                c.execute("""
                    UPDATE Maintainer_Requirements 
                    SET COR = ?, TOR = ?, GOOD_MORAL = ?
                    WHERE maintainer_id = ?
                """, (cor_blob, tor_blob, moral_blob, maintainer_id_str))
            else:
                # Insert new record
                c.execute("""
                    INSERT INTO Maintainer_Requirements (maintainer_id, COR, TOR, GOOD_MORAL)
                    VALUES (?, ?, ?, ?)
                """, (maintainer_id_str, cor_blob, tor_blob, moral_blob))
            
            conn.commit()
            conn.close()
            
            # Update local status
            if "COR" in self.uploaded_files:
                self.status["COR (Certificate of Registration)"] = True
            if "Grades" in self.uploaded_files:
                self.status["Grades (Previous Semester)"] = True
            if "Good Moral" in self.uploaded_files:
                self.status["Good Moral Certificate"] = True
            
            messagebox.showinfo("Success", "Requirements uploaded and saved successfully!")
            self.back_to_card()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to save requirements: {e}")
        except FileNotFoundError as e:
            messagebox.showerror("File Error", f"Could not read file: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def back_to_card(self):
        # Destroy upload form
        self.upload_frame.destroy()
        self.progress_section.grid()
        self.upload_btn_frame.grid()
        self.refresh_progress()


# ---------------------------------------------------------
# ANNOUNCEMENTS SECTION
# ---------------------------------------------------------
announcements = [
    {
        "title": "SM FOUNDATION COLLEGE SCHOLARSHIP",
        "description": "Philippine Scholar",
        "link": "https://www.facebook.com/share/p/17h9T2NDUM/"
    },
    {
        "title": "CHED MERIT SCHOLARSHIP PROGRAM",
        "description": "Philippine Scholar",
        "link": "https://philscholar.com/ched-merit-scholarship-2025-2026/"
    },
    {
        "title": "Cebuana Lhuillier Scholarship 2025 | Now Open!",
        "description": "Philippine Scholar",
        "link": "https://philscholar.com/cebuana-lhuillier-scholarship/"
    },
    {
        "title": "OWWA Education for Development Scholarship Program (EDSP) | 2026-2027",
        "description": "Philippine Scholar",
        "link": "https://philscholar.com/owwa-education-for-development-scholarship-program/#google_vignette"
    },
]

def create_announcement_card(parent, title, description, link=None):
    card = ctk.CTkFrame(parent, fg_color="white", corner_radius=16, border_width=1, border_color=CARD_BORDER)
    card.pack(fill="x", pady=10, padx=16)

    ctk.CTkLabel(card, text=title, font=("Segoe UI", 16, "bold"), text_color=MAROON, wraplength=600).pack(anchor="w", pady=(10,5), padx=10)
    ctk.CTkLabel(card, text=description, font=("Segoe UI", 13), text_color=TEXT, wraplength=600, justify="left").pack(anchor="w", pady=(0,10), padx=10)
    
    if link:
        ctk.CTkButton(card, text="Read More", text_color="#F2E7E7",fg_color=MAROON,command=lambda: webbrowser.open(link), font=("Segoe UI", 12)).pack(anchor="w", pady=(0,10), padx=10)

# ---------------------------------------------------------
# MAIN DASHBOARD APP
# ---------------------------------------------------------
class MaintainerApp(ctk.CTk):
    def __init__(self, maintainer):
        super().__init__()
        self.maintainer = maintainer
        self.title("BatStateU • Scholarship Management System")
        self.geometry("1100x720")
        self.minsize(960,640)
        self.configure(fg_color=BG)
        
        # ---------------- HEADER ----------------
        self.header = ctk.CTkFrame(self, fg_color=MAROON, height=110, corner_radius=0)
        self.header.pack(fill="x")
        self.header_label = ctk.CTkLabel(self.header, text="BATANGAS STATE UNIVERSITY", font=("Arial Black",34), text_color="white")
        self.header_label.pack(pady=(10,0))
        ctk.CTkLabel(self.header, text="SCHOLARSHIP MANAGEMENT SYSTEM", font=("Arial",18), text_color="white").pack(pady=(0,10))

        # ---------------- SIDEBAR ----------------
        self.sidebar = ctk.CTkFrame(self, width=250, fg_color="white", corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        sidebar_center = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        sidebar_center.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(sidebar_center, text="NAVIGATION", font=("Segoe UI", 18, "bold"), text_color=MAROON).pack(pady=(0,20))

        self.buttons = {}

        def nav_btn(key, text, command=None):
            active = key=="dashboard"
            fg = ACTIVE_BG if active else "#EFEFEF"
            hover = ACTIVE_HOVER if active else "#F5F5F5"
            txt_color = "white" if active else MAROON
            btn = ctk.CTkButton(sidebar_center, text=text, fg_color=fg, hover_color=hover, text_color=txt_color,
                                anchor="w", width=200, height=45, corner_radius=20,
                                font=("Helvetica", 14, "bold"), command=command)
            btn.pack(pady=6)
            self.buttons[key] = btn

        nav_btn("dashboard", "📊 Dashboard", command=self.show_dashboard)
        nav_btn("announcements", "📢 Announcements", command=self.show_announcements)
        nav_btn("profile", "👤 Profile Settings", command=self.show_profile)

        logout_btn = ctk.CTkButton(sidebar_center, text="🚪 Logout", fg_color=ACTIVE_BG,
                                   hover_color=ACTIVE_HOVER, text_color="white",
                                   width=200, height=45, corner_radius=20,
                                   font=("Helvetica", 14, "bold"), command=self.logout)
        logout_btn.pack(pady=(25,0))

        # ---------------- BODY ----------------
        self.body = ctk.CTkFrame(self, fg_color=BG)
        self.body.pack(side="left", fill="both", expand=True)
        self.content_frame = ctk.CTkScrollableFrame(self.body)
        self.content_frame.pack(fill="both", expand=True)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Default page
        self.show_dashboard()
        
    def logout(self):
        self.destroy()  
        subprocess.Popen(["python", "login.py"])
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

    def show_dashboard(self):
        self.clear_content()
        self.set_active_button("dashboard")
        self.header_label.configure(text="BATANGAS STATE UNIVERSITY")
        dashboard = MaintainerDashboard(self.content_frame, maintainer=self.maintainer)
        dashboard.pack(fill="x", pady=(0,16))
        scholarships = ScholarshipsAvailable(self.content_frame, maintainer_id=self.maintainer["student_id"])
        scholarships.pack(fill="x")

    def show_announcements(self):
        self.clear_content()
        self.set_active_button("announcements")
        self.header_label.configure(text="BATANGAS STATE UNIVERSITY")
        for item in announcements:
            create_announcement_card(self.content_frame, item["title"], item["description"], item.get("link"))

    def show_profile(self):
        """
        Profile Settings UI
        """
        import sqlite3
        from tkinter import filedialog

        self.clear_content()
        self.set_active_button("profile")
        self.header_label.configure(text="PROFILE SETTINGS")

        maintainer = self.maintainer or {}

        # Outer card
        card = ctk.CTkFrame(self.content_frame, fg_color="white", corner_radius=16,
                            border_width=1, border_color=CARD_BORDER)
        card.pack(padx=40, pady=30, fill="both", expand=True)

        # Single column layout (walang avatar)
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(padx=24, pady=20, fill="both", expand=True)
        content.grid_columnconfigure(0, weight=1)

        # ========== PROFILE INFO SECTION ==========
        name_lbl = ctk.CTkLabel(content, text=maintainer.get("name", "Unknown"),
                                font=("Segoe UI", 22, "bold"), text_color=ACTIVE_BG)
        name_lbl.grid(row=0, column=0, sticky="w")

        status = maintainer.get('status', 'PENDING')
        color_map = {"APPROVED": "#DAF1DD", "PENDING": "#FFF2CC", "REJECTED": "#FCE5E5"}
        status_text_color = MAROON if status != "REJECTED" else "#B00020"
        Tag(content, text=f"STATUS: {status}", fg=color_map.get(status, "#FFF2CC"), text_color=status_text_color).grid(row=1, column=0, sticky="w", pady=(6,12))

        # ========== DETAILS GRID ==========
        details_frame = ctk.CTkFrame(content, fg_color="transparent")
        details_frame.grid(row=2, column=0, sticky="ew", pady=(12,0))
        details_frame.grid_columnconfigure(1, weight=1)

        fields = [
            ("Student ID", "student_id", False),
            ("Maintainer No.", "maintainer_no", False),
            ("Program", "program", True),
            ("Year Level", "year", True),
            ("Username", "username", False),
            ("Email", "email", True),
            ("Phone", "phone", True),
            ("GWA", "gwa", True),
        ]

        entries = {}
        row = 0
        for label_text, key, editable in fields:
            lbl = ctk.CTkLabel(details_frame, text=label_text + ":", text_color=SUBDUED, font=("Segoe UI", 12))
            lbl.grid(row=row, column=0, sticky="w", pady=8, padx=(0,8))
            ent = ctk.CTkEntry(details_frame, width=420, font=("Segoe UI", 12))
            ent.grid(row=row, column=1, sticky="ew", pady=8)
            ent.insert(0, str(maintainer.get(key, "")))
            ent.configure(state="readonly")
            entries[key] = (ent, editable)
            row += 1

        # ========== ACTION BUTTONS ==========
        actions = ctk.CTkFrame(content, fg_color="transparent")
        actions.grid(row=3, column=0, pady=(16,0), sticky="w")

        # Change Password Button
        def open_change_password():
            win = ctk.CTkToplevel(self)
            win.title("Change Password")
            win.geometry("420x240")
            win.resizable(False, False)
            
            ctk.CTkLabel(win, text="Change Password", font=("Segoe UI", 16, "bold"), text_color=MAROON).pack(pady=(16,12))
            
            old_pw = ctk.CTkEntry(win, placeholder_text="Current password", show="●", width=360)
            old_pw.pack(pady=6)
            new_pw = ctk.CTkEntry(win, placeholder_text="New password", show="●", width=360)
            new_pw.pack(pady=6)
            confirm_pw = ctk.CTkEntry(win, placeholder_text="Confirm new password", show="●", width=360)
            confirm_pw.pack(pady=6)

            def hash_pw(pw):
                return hashlib.sha256(pw.encode()).hexdigest()

            def submit_change():
                if not old_pw.get() or not new_pw.get() or not confirm_pw.get():
                    messagebox.showerror("Error", "All fields are required.")
                    return
                if new_pw.get() != confirm_pw.get():
                    messagebox.showerror("Error", "New passwords do not match.")
                    return
                if len(new_pw.get()) < 6:
                    messagebox.showerror("Error", "Password must be at least 6 characters.")
                    return
                try:
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    c.execute("SELECT password FROM Maintainer WHERE student_id=?", (maintainer.get("student_id"),))
                    row = c.fetchone()
                    conn.close()
                    stored = row[0] if row else None
                    if stored and stored != "" and hash_pw(old_pw.get()) != stored:
                        messagebox.showerror("Error", "Current password is incorrect.")
                        return
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    c.execute("UPDATE Maintainer SET password=? WHERE student_id=?", (hash_pw(new_pw.get()), maintainer.get("student_id")))
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Success", "Password changed successfully.")
                    win.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to change password: {e}")

            btn_frame = ctk.CTkFrame(win, fg_color="transparent")
            btn_frame.pack(pady=(12,8))
            ctk.CTkButton(btn_frame, text="Change", width=100, fg_color=MAROON, hover_color=ACTIVE_HOVER, command=submit_change).pack(side="left", padx=5)
            ctk.CTkButton(btn_frame, text="Cancel", width=100, fg_color="#EFEFEF", text_color=MAROON, hover_color="#F6F6F6", command=win.destroy).pack(side="left", padx=5)

        change_pw_btn = ctk.CTkButton(actions, text="🔐 Change Password", width=170, fg_color="#EFEFEF",
                                      text_color=ACTIVE_BG, hover_color="#F6F6F6", command=open_change_password)
        change_pw_btn.pack(side="left", padx=(0,10))

        # Edit / Save Functionality
        def enable_edit():
            for ent, editable in entries.values():
                if editable:
                    ent.configure(state="normal")
            edit_btn.configure(state="disabled")
            save_btn.configure(state="normal")
            cancel_btn.configure(state="normal")

        def save_changes():
            updated = {}
            for key, (ent, editable) in entries.items():
                if editable and ent.cget("state") == "normal":
                    updated[key] = ent.get().strip()
            
            if not updated:
                messagebox.showwarning("No Changes", "No fields were modified.")
                disable_edit()
                return

            # Validation
            if "email" in updated and updated["email"]:
                if "@" not in updated["email"] or "." not in updated["email"]:
                    messagebox.showerror("Validation", "Invalid email address.")
                    return
            if "phone" in updated and updated["phone"]:
                if not updated["phone"].replace("-", "").replace("+", "").isdigit() or len(updated["phone"].replace("-", "")) < 7:
                    messagebox.showerror("Validation", "Invalid phone number (min 7 digits).")
                    return
            if "gwa" in updated and updated["gwa"]:
                try:
                    g = float(updated["gwa"])
                    if not (1.0 <= g <= 5.0):
                        raise ValueError()
                except:
                    messagebox.showerror("Validation", "GWA must be between 1.0 and 5.0.")
                    return

            # Password verification window
            verify_win = ctk.CTkToplevel(self)
            verify_win.title("Verify Password")
            verify_win.geometry("380x180")
            verify_win.resizable(False, False)
            verify_win.grab_set()  # Make window modal
            
            ctk.CTkLabel(verify_win, text="Enter your password to confirm changes", 
                        font=("Segoe UI", 14, "bold"), text_color=MAROON).pack(pady=(20,12))
            
            password_entry = ctk.CTkEntry(verify_win, placeholder_text="Password", show="●", width=320)
            password_entry.pack(pady=8)
            password_entry.focus()

            def hash_pw(pw):
                return hashlib.sha256(pw.encode()).hexdigest()

            def verify_and_save():
                entered_password = password_entry.get()
                if not entered_password:
                    messagebox.showerror("Error", "Password is required.")
                    return
                
                try:
                    # Verify password
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    c.execute("SELECT password FROM Maintainer WHERE student_id=?", (maintainer.get("student_id"),))
                    row = c.fetchone()
                    conn.close()
                    
                    stored = row[0] if row else None
                    # Check both hashed and plain text password
                    if stored and stored != "":
                        if hash_pw(entered_password) != stored and entered_password != stored:
                            messagebox.showerror("Error", "Incorrect password.")
                            return
                    
                    # Prepare DB update
                    key_map = {"program": "course", "year": "yearlevel", "phone": "phone_number"}
                    db_updates = {}
                    for k, v in updated.items():
                        if k == "program" and "(" in v and ")" in v:
                            try:
                                course_part = v.split("(",1)[1].rsplit(")",1)[0].strip()
                                db_updates["course"] = course_part
                            except:
                                db_updates["course"] = v
                        else:
                            db_updates[key_map.get(k, k)] = v

                    # Save to database
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    set_clause = ", ".join([f"{col}=?" for col in db_updates.keys()])
                    values = list(db_updates.values())
                    values.append(maintainer.get("student_id"))
                    c.execute(f"UPDATE Maintainer SET {set_clause} WHERE student_id=?", values)
                    conn.commit()
                    conn.close()
                    
                    # Update maintainer object with new values
                    for key, value in updated.items():
                        self.maintainer[key] = value
                    
                    verify_win.destroy()
                    messagebox.showinfo("Success", "Profile updated successfully.")
                    disable_edit()
                    
                    # Refresh the display with updated values
                    name_lbl.configure(text=self.maintainer.get("name", "Unknown"))
                    status = self.maintainer.get('status', 'PENDING')
                    for key, (ent, editable) in entries.items():
                        ent.configure(state="normal")
                        ent.delete(0, "end")
                        ent.insert(0, str(self.maintainer.get(key, "")))
                        if not editable:
                            ent.configure(state="readonly")
                    disable_edit()
                    
                except Exception as e:
                    verify_win.destroy()
                    messagebox.showerror("Error", f"Failed to save: {e}")

            btn_frame = ctk.CTkFrame(verify_win, fg_color="transparent")
            btn_frame.pack(pady=(16,8))
            ctk.CTkButton(btn_frame, text="Confirm", width=120, fg_color=MAROON, 
                         hover_color=ACTIVE_HOVER, command=verify_and_save).pack(side="left", padx=5)
            ctk.CTkButton(btn_frame, text="Cancel", width=120, fg_color="#EFEFEF", 
                         text_color=MAROON, hover_color="#F6F6F6", 
                         command=verify_win.destroy).pack(side="left", padx=5)
            
            # Bind Enter key to confirm
            password_entry.bind("<Return>", lambda e: verify_and_save())

        def disable_edit():
            for ent, editable in entries.values():
                if editable:
                    ent.configure(state="readonly")
            edit_btn.configure(state="normal")
            save_btn.configure(state="disabled")
            cancel_btn.configure(state="disabled")

        def cancel_changes():
            for key, (ent, editable) in entries.items():
                if editable:
                    ent.delete(0, "end")
                    ent.insert(0, str(maintainer.get(key, "")))
            disable_edit()

        edit_btn = ctk.CTkButton(actions, text="✏️ Edit Profile", width=150, fg_color=ACTIVE_BG,
                                 hover_color=ACTIVE_HOVER, text_color="white", command=enable_edit)
        edit_btn.pack(side="left", padx=(0,10))

        save_btn = ctk.CTkButton(actions, text="💾 Save", width=100, fg_color="#EFEFEF",
                                 text_color=ACTIVE_BG, hover_color="#F6F6F6", command=save_changes, state="disabled")
        save_btn.pack(side="left", padx=(0,6))

        cancel_btn = ctk.CTkButton(actions, text="✕ Cancel", width=100, fg_color="#EFEFEF",
                                   text_color="#C41E3A", hover_color="#FCE5E5", command=cancel_changes, state="disabled")
        cancel_btn.pack(side="left")

        # ========== HELP TEXT ==========
        divider = ctk.CTkFrame(content, fg_color=CARD_BORDER, height=1)
        divider.grid(row=4, column=0, sticky="ew", pady=(18,8))
        help_text = "💡 Tip: Click Edit Profile to modify fields. Changes are saved to the database."
        ctk.CTkLabel(content, text=help_text, text_color=SUBDUED, font=("Segoe UI", 11)).grid(row=5, column=0, sticky="w", pady=(6,0))

# ---------------------------------------------------------
# RUN
# ---------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        tk.Tk().withdraw()
        messagebox.showerror("Error", "No username provided!")
        sys.exit(1)

    username = sys.argv[1]
    maintainer = get_maintainer_by_username(username)

    if not maintainer:
        tk.Tk().withdraw()
        messagebox.showerror("Error", f"Maintainer '{username}' not found!")
        sys.exit(1)

    app = MaintainerApp(maintainer)
    app.after(100, lambda: app.state("zoomed"))
    app.mainloop()
