import customtkinter as ctk
from tkinter import messagebox
import subprocess

# ------------------------- CONFIG -------------------------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

# ============================================================
#          MINI WINDOW FOR FORGOT PASSWORD / RESET
# ============================================================
class ForgotPasswordWindow:

    def __init__(self, width=500, height=300):
        self.win = ctk.CTk()
        self.win.title("Reset Password")

        # Centering window
        screen_w = self.win.winfo_screenwidth()
        screen_h = self.win.winfo_screenheight()
        x = int((screen_w / 2) - (width / 2))
        y = int((screen_h / 2) - (height / 2))

        self.win.geometry(f"{width}x{height}+{x}+{y}")
        self.win.resizable(False, False)

        self.build_ui()

        self.win.mainloop()

    def build_ui(self):

        frame = ctk.CTkFrame(self.win, fg_color="white", corner_radius=15)
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Title
        title = ctk.CTkLabel(
            frame,
            text="Password Reset Recommended",
            font=("Helvetica", 22, "bold"),
            text_color="#800000"
        )
        title.pack(pady=(20, 10))

        # Subtext
        msg = ctk.CTkLabel(
            frame,
            text="You have exceeded the allowed login attempts.\n"
                 "For your security, please reset your password.",
            font=("Arial", 14),
            text_color="black"
        )
        msg.pack(pady=(0, 20))

        # Change password button
        change_btn = ctk.CTkButton(
            frame,
            text="Change Password",
            fg_color="#800000",
            hover_color="#A52A2A",
            text_color="white",
            width=200,
            height=45,
            corner_radius=20,
            font=("Helvetica", 15, "bold"),
            command=self.open_change_password_window
        )
        change_btn.pack(pady=10)

    # 🟥 Ito yung magbubukas ng separate file para mag-reset
    def open_change_password_window(self):
        try:
            # Example: Opens separate python file for actual change-password UI
            subprocess.Popen(["python", "reset_password.py"])
            self.win.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))


# ============================================================
# RUN WINDOW DIRECTLY (for testing)
# ============================================================
if __name__ == "__main__":
    ForgotPasswordWindow()
