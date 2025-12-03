import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import subprocess
from PIL import Image
import os

# ------------------------- CONFIG -------------------------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

# ------------------------- IMPORT MAINTAINER DASHBOARD -------------------------
from maintainersdashboard import get_maintainer_by_studentid, MaintainerApp
# ⚠ NOTE:
#   - Siguraduhin meron kang function na get_maintainer_by_studentid()
#     sa maintainersdashboard.py

# ============================================================
#                OOP CLASS FOR LOGIN SYSTEM
# ============================================================
class LoginSystem:
    def __init__(self, win):
        self.win = win
        self.user_attempts = 0
        self.admin_attempts = 0

    # ------------------------ USER LOGIN ------------------------
    def user_login(self, student_id, password):
        student_id = student_id.strip()
        password = password.strip()

        if student_id == "" or password == "":
            messagebox.showerror("Error", "All fields are required!")
            return

        if self.user_attempts >= 3:
            messagebox.showwarning("Locked", "Too many failed attempts.")
            return

        # Student login based on STUDENT ID
        maintainer = get_maintainer_by_studentid(student_id)

        if maintainer:
            self.user_attempts = 0
            self.win.destroy()

            app = MaintainerApp(maintainer)
            app.after(100, lambda: app.state("zoomed"))
            app.mainloop()
        else:
            self.user_attempts += 1
            messagebox.showerror("Error", "Invalid Student ID or Password!")

    # ------------------------ ADMIN LOGIN ------------------------
    def admin_login(self, username, password):
        username= username.strip()
        password = password.strip()

        if username == "" or password == "":
            messagebox.showerror("Error", "All fields are required!")
            return
        
        if self.admin_attempts >= 3:
            messagebox.showwarning("Locked", "Too many failed attempts.\nUse 'Forgot Password'.")
            return

        try:
            conn = sqlite3.connect("Scholarship.db")
            c = conn.cursor()
            c.execute("SELECT * FROM Admin WHERE username=? AND password=?", (username, password))
            result = c.fetchone()
            conn.close()

            if result:
                self.admin_attempts = 0
                self.win.destroy()
                subprocess.Popen(["python", "adminchart.py"]) #TO CONNECT ADMIN FILE
            else:
                self.admin_attempts += 1
                messagebox.showerror("Error", "Invalid Username or Password!")

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", str(e))

    def forgot_password(self):
        self.win.destroy()
        subprocess.Popen(["python", "forget_pass.py"])

    def open_signup(self):
        self.win.destroy()
        subprocess.Popen(["python", "signup.py"])


def main_login():

    win = ctk.CTk()
    win.title("Scholarship Management System - Batangas State University")
    win.after(100, lambda: win.state("zoomed"))

    system = LoginSystem(win)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # ------------------------- LEFT PANEL -------------------------
    left_frame = ctk.CTkFrame(win, width=400, fg_color="maroon", corner_radius=0)
    left_frame.pack(side="left", fill="y")

    left_center_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
    left_center_frame.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(left_center_frame, text="BATANGAS STATE UNIVERSITY",
                 font=("Helvetica", 24, "bold"), text_color="white").pack(pady=(0, 10))
    ctk.CTkLabel(left_center_frame, text="SCHOLARSHIP MANAGEMENT SYSTEM",
                 font=("Helvetica", 15), text_color="white").pack()

    # ------------------------- RIGHT PANEL -------------------------
    right_frame = ctk.CTkFrame(win, fg_color="white", corner_radius=0)
    right_frame.pack(side="left", fill="both", expand=True)

    # Logo
    logo_path = os.path.join(BASE_DIR, "logo.png")
    if os.path.exists(logo_path):
        logo_img = ctk.CTkImage(Image.open(logo_path), size=(120, 100))
        ctk.CTkLabel(right_frame, image=logo_img, text="").pack(pady=30)

    # Tabs
    tabview = ctk.CTkTabview(right_frame, width=600, height=400, fg_color="white", corner_radius=20)
    tabview.pack(pady=10)
    tabview.add("User Login")
    tabview.add("Admin Login")

    # Eye icons
    eye_open_img = ctk.CTkImage(Image.open(os.path.join(BASE_DIR, "eye_open.png")), size=(20, 20))
    eye_close_img = ctk.CTkImage(Image.open(os.path.join(BASE_DIR, "eye_closed.png")), size=(20, 20))

    # ------------------------- USER LOGIN TAB -------------------------
    user_tab = tabview.tab("User Login")
    ctk.CTkLabel(user_tab, text="Welcome back! Iskolar\nPlease login to your account",
                 font=("Helvetica", 22, "bold"), text_color="maroon").pack(pady=30)

    user_entry = ctk.CTkEntry(user_tab, placeholder_text="Student ID", width=400, height=40,
                              font=("Arial", 16), corner_radius=15,
                              border_color="#800000", border_width=2, fg_color="white")
    user_entry.pack(pady=15)

    # Password container
    pw_container = ctk.CTkFrame(user_tab, fg_color="white", border_width=2,
                                border_color="#800000", corner_radius=15, width=345, height=35)
    pw_container.pack(pady=15)

    user_pass = ctk.CTkEntry(pw_container, placeholder_text="Password", show="●",
                             width=345, height=35, font=("Arial", 16),
                             fg_color="white", border_width=0)
    user_pass.pack(side="left", fill="x", padx=(10, 0), pady=3)

    # Toggle password visibility
    user_pw_visible = False
    def toggle_user_pw():
        nonlocal user_pw_visible
        user_pw_visible = not user_pw_visible
        user_pass.configure(show="" if user_pw_visible else "●")
        user_eye_btn.configure(image=eye_open_img if user_pw_visible else eye_close_img)

    user_eye_btn = ctk.CTkButton(pw_container, text="", image=eye_close_img,
                                 width=30, height=30, fg_color="transparent",
                                 hover_color="#f8f8f8", command=toggle_user_pw)
    user_eye_btn.pack(side="right", padx=(0, 10), pady=3)

    # Forgot password
    ctk.CTkButton(user_tab, text="Forgot Password?", fg_color="white",
                  hover_color="#f0f0f0", text_color="maroon", width=120, height=25,
                  font=("Helvetica", 12), command=system.forgot_password).pack(pady=(0, 10))

    # Buttons
    user_buttons_frame = ctk.CTkFrame(user_tab, fg_color="transparent")
    user_buttons_frame.pack(pady=20)

    ctk.CTkButton(user_buttons_frame, text="Sign Up", fg_color="#800000",
                  hover_color="#A52A2A", text_color="white", corner_radius=20,
                  width=150, height=45, font=("Helvetica", 14, "bold"),
                  command=system.open_signup).pack(side="left", padx=10)

    ctk.CTkButton(user_buttons_frame, text="Log in", fg_color="#800000",
                  hover_color="#A52A2A", text_color="white", corner_radius=20,
                  width=150, height=45, font=("Helvetica", 14, "bold"),
                  command=lambda: system.user_login(user_entry.get(), user_pass.get())
                  ).pack(side="left", padx=10)

    # ------------------------- ADMIN LOGIN TAB -------------------------
    admin_tab = tabview.tab("Admin Login")
    ctk.CTkLabel(admin_tab, text="Administrator Access",
                 font=("Helvetica", 22, "bold"), text_color="maroon").pack(pady=30)

    admin_user = ctk.CTkEntry(admin_tab, placeholder_text="Username", width=400, height=40,
                              font=("Arial", 16), corner_radius=15,
                              border_color="#800000", border_width=2, fg_color="white")
    admin_user.pack(pady=15)

    admin_pass = ctk.CTkEntry(admin_tab, placeholder_text="Password", show="●", width=400, height=40,
                              font=("Arial", 16), corner_radius=15,
                              border_color="#800000", border_width=2, fg_color="white")
    admin_pass.pack(pady=15)

    ctk.CTkButton(admin_tab, text="Forgot Password?", fg_color="white",
                  hover_color="#f0f0f0", text_color="maroon", width=120, height=25,
                  font=("Helvetica", 12), command=system.forgot_password).pack(pady=(0, 10))

    ctk.CTkButton(admin_tab, text="Log in", fg_color="#800000", hover_color="#A52A2A",
                  text_color="white", corner_radius=20, width=150, height=45,
                  font=("Helvetica", 14, "bold"),
                  command=lambda: system.admin_login(admin_user.get(), admin_pass.get())
                  ).pack(pady=25)

    win.mainloop()


# ============================================================
# START APP
# ============================================================
if __name__ == "__main__":
    main_login()
