import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import smtplib
import random
import subprocess
import os
from PIL import Image

# ------------------------- CONFIG -------------------------
DB_FILE = "Scholarship.db"
RESET_EMAIL = None
RESET_OTP = None

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

MAROON = "#800000"
HOVER = "#A52A2A"

# ============================================================
# OPEN LOGIN SCREEN
# ============================================================
def open_login():
    subprocess.Popen(["python", "login.py"])

# ============================================================
# SEND OTP EMAIL
# ============================================================
def send_otp(email, win):
    email = email.strip()
    if email == "":
        messagebox.showerror("Error", "Please enter your email.")
        return

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM Maintainer WHERE email=?", (email,))
    result = c.fetchone()
    conn.close()

    if not result:
        messagebox.showerror("Error", "Email is not registered.")
        return

    global RESET_EMAIL, RESET_OTP
    RESET_EMAIL = email
    RESET_OTP = str(random.randint(100000, 999999))

    try:
        sender = "bsu.smsoffice@gmail.com"
        app_password = "eltk hyar kjve dbhu"

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, app_password)
            msg = f""""Subject: Password Reset

Dear User,

Your OTP Code is: **{RESET_OTP}**

Please keep this OTP secure and do not share it with anyone. 
This code is confidential and will only be used to reset your password.

Thank you for your cooperation.
"""
            server.sendmail(sender, email, msg)

        win.destroy()
        otp_screen()
    except Exception as e:
        messagebox.showerror("Email Error", str(e))

# ============================================================
# OTP SCREEN
# ============================================================
def otp_screen():
    win = ctk.CTk()
    win.title("Verify Code")
    win.after(100, lambda: win.state("zoomed"))

    # LEFT PANEL
    left_frame = ctk.CTkFrame(win, width=400, fg_color=MAROON)
    left_frame.pack(side="left", fill="y")

    ctk.CTkLabel(left_frame, text="BATANGAS STATE UNIVERSITY",
                 font=("Helvetica", 24, "bold"), text_color="white").pack(pady=(150, 10))
    ctk.CTkLabel(left_frame, text="SCHOLARSHIP MANAGEMENT SYSTEM",
                 font=("Helvetica", 15), text_color="white").pack(pady=(0, 50))

    # RIGHT PANEL
    right_frame = ctk.CTkFrame(win, fg_color="white")
    right_frame.pack(side="left", fill="both", expand=True)

    container = ctk.CTkFrame(right_frame, fg_color="transparent")
    container.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(container, text="Verification Code",
                 font=("Helvetica", 32, "bold"), text_color=MAROON).pack(pady=(0, 20))

    ctk.CTkLabel(container,
                 text=f"A 6-digit verification code was sent to:\n{RESET_EMAIL}",
                 font=("Helvetica", 16), text_color="#555555").pack(pady=(0, 30))

    frame = ctk.CTkFrame(container, fg_color="white")
    frame.pack(pady=(0, 40))

    otp_vars = []
    for _ in range(6):
        var = ctk.StringVar()
        entry = ctk.CTkEntry(frame, width=60, height=65,
                             fg_color="#f2f2f2",
                             corner_radius=10, justify="center",
                             font=("Helvetica", 20, "bold"),
                             textvariable=var)
        entry.pack(side="left", padx=8)
        otp_vars.append(var)

    def verify():
        entered = "".join([v.get() for v in otp_vars])
        if entered == RESET_OTP:
            win.destroy()
            reset_password_screen()
        else:
            messagebox.showerror("Error", "Incorrect verification code.")

    ctk.CTkButton(container, text="Verify",
                  fg_color=MAROON, hover_color=HOVER,
                  corner_radius=20, width=200, height=50,
                  font=("Helvetica", 18, "bold"),
                  command=verify).pack()

    win.mainloop()

# ============================================================
# RESET PASSWORD SCREEN
# ============================================================
def reset_password_screen():
    win = ctk.CTk()
    win.title("Reset Password")
    win.after(100, lambda: win.state("zoomed"))

    # LEFT PANEL
    left_frame = ctk.CTkFrame(win, width=400, fg_color=MAROON)
    left_frame.pack(side="left", fill="y")

    ctk.CTkLabel(left_frame, text="BATANGAS STATE UNIVERSITY",
                 font=("Helvetica", 24, "bold"), text_color="white").pack(pady=(150, 10))
    ctk.CTkLabel(left_frame, text="SCHOLARSHIP MANAGEMENT SYSTEM",
                 font=("Helvetica", 15), text_color="white").pack(pady=(0, 50))

    # RIGHT PANEL
    right_frame = ctk.CTkFrame(win, fg_color="white")
    right_frame.pack(side="left", fill="both", expand=True)

    container = ctk.CTkFrame(right_frame, fg_color="transparent")
    container.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(container, text="Reset Password",
                 font=("Helvetica", 32, "bold"), text_color=MAROON).pack(pady=(0, 40))

    new_pw = ctk.CTkEntry(container, show="●", placeholder_text="New Password",
                           width=400, height=55, font=("Helvetica", 16),
                           fg_color="white", border_color=MAROON,
                           border_width=2, corner_radius=25)
    new_pw.pack(pady=(0, 20))

    confirm_pw = ctk.CTkEntry(container, show="●", placeholder_text="Confirm Password",
                               width=400, height=55, font=("Helvetica", 16),
                               fg_color="white", border_color=MAROON,
                               border_width=2, corner_radius=25)
    confirm_pw.pack(pady=(0, 40))

    def update_pw():
        pw1 = new_pw.get()
        pw2 = confirm_pw.get()

        if pw1.strip() == "" or pw2.strip() == "":
            messagebox.showerror("Error", "Please fill out all fields.")
            return
        if pw1 != pw2:
            messagebox.showerror("Error", "Passwords do not match!")
            return

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("UPDATE Maintainer SET password=? WHERE email=?", (pw1, RESET_EMAIL))
        conn.commit()
        conn.close()

        win.destroy()
        success_popup()

    ctk.CTkButton(container, text="Reset Password",
                  fg_color=MAROON, hover_color=HOVER,
                  width=250, height=55, corner_radius=25,
                  font=("Helvetica", 18, "bold"),
                  command=update_pw).pack()

    win.mainloop()

# ============================================================
# SUCCESS POPUP
# ============================================================
def success_popup():
    win = ctk.CTk()
    win.title("Success")
    win.after(100, lambda: win.state("zoomed"))

    container = ctk.CTkFrame(win, fg_color="transparent")
    container.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(container, text="Password reset successfully!",
                 font=("Helvetica", 22, "bold"), text_color=MAROON).pack(pady=(0, 30))

    ctk.CTkButton(container, text="Return to Login",
                  fg_color=MAROON, hover_color=HOVER,
                  width=180, height=50, corner_radius=25,
                  font=("Helvetica", 18, "bold"),
                  command=win.destroy).pack()

    win.mainloop()

# ============================================================
# MAIN SCREEN
# ============================================================
def main():
    win = ctk.CTk()
    win.title("Forgot Password")
    win.after(100, lambda: win.state("zoomed"))
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(BASE_DIR, "logo.png")

    # ----------------- LEFT PANEL -----------------
    left_frame = ctk.CTkFrame(win, width=400, fg_color=MAROON, corner_radius=0)
    left_frame.pack(side="left", fill="y")

    left_center_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
    left_center_frame.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(left_center_frame,
                 text="BATANGAS STATE UNIVERSITY",
                 font=("Helvetica", 24, "bold"),
                 text_color="white").pack(pady=(0, 10), padx=20)
    ctk.CTkLabel(left_center_frame,
                 text="SCHOLARSHIP MANAGEMENT SYSTEM",
                 font=("Helvetica", 15),
                 text_color="white").pack()

    # ----------------- RIGHT PANEL -----------------
    right_frame = ctk.CTkFrame(win, fg_color="white")
    right_frame.pack(side="left", fill="both", expand=True)

    # LOGO ON TOP OF RIGHT PANEL
    if os.path.exists(logo_path):
        logo_img = ctk.CTkImage(Image.open(logo_path), size=(120, 100))
        logo_label = ctk.CTkLabel(right_frame, image=logo_img, text="")
        logo_label.pack(pady=30)
    else:
        print("Logo not found:", logo_path)

    container = ctk.CTkFrame(right_frame, fg_color="transparent")
    container.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(container, text="Forgot Password ?",
                 font=("Helvetica", 36, "bold"), text_color=MAROON).pack(pady=(0, 20))

    ctk.CTkLabel(container, text="Please enter your Email Account",
                 font=("Helvetica", 16), text_color="#555555").pack(pady=(0, 40))

    ctk.CTkLabel(container, text="E-mail",
                 font=("Helvetica", 16, "bold"), text_color=MAROON).pack(pady=(0, 10))

    email_entry = ctk.CTkEntry(container, placeholder_text="username@gmail.com",
                                width=400, height=45, fg_color="white",
                                border_color=MAROON, border_width=2,
                                corner_radius=25, font=("Helvetica", 16))
    email_entry.pack(pady=(0, 40))

    # ----------------- Buttons Frame -----------------
    button_frame = ctk.CTkFrame(container, fg_color="transparent")
    button_frame.pack(pady=(0, 20))

    # Back Button (left)
    ctk.CTkButton(
        button_frame, text="Back", fg_color=MAROON, hover_color=HOVER,
        width=150, height=45, corner_radius=25,
        font=("Helvetica", 16, "bold"),
        command=lambda: [win.destroy(), open_login()]
    ).pack(side="left", padx=(0, 10))

    # Send Code Button (right)
    ctk.CTkButton(
        button_frame, text="Send Code", fg_color=MAROON, hover_color=HOVER,
        width=150, height=45, corner_radius=25,
        font=("Helvetica", 16, "bold"),
        command=lambda: send_otp(email_entry.get(), win)
    ).pack(side="left")

    win.mainloop()

# ============================================================
# RUN APP
# ============================================================
if __name__ == "__main__":
    main()
