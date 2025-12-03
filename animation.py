import customtkinter as ctk
import subprocess

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

def splash_screen():
    splash = ctk.CTk()
    splash.overrideredirect(True)

    # Splash size
    w, h = 640, 360

    # Center window
    splash.update_idletasks()
    sw, sh = splash.winfo_screenwidth(), splash.winfo_screenheight()
    x, y = (sw - w) // 2, (sh - h) // 2
    splash.geometry(f"{w}x{h}+{x}+{y}")

    # Full maroon background
    splash.configure(fg_color="maroon")

    # --------- Elements (properly spaced) ---------
    # Logo
    logo_label = ctk.CTkLabel(splash, text="🎓", font=("Helvetica", 36, "bold"), text_color="white", fg_color="maroon")
    logo_label.place(relx=0.5, rely=0.25, anchor="center")

    # University name
    uni_label = ctk.CTkLabel(splash, text="Batangas State University",
                             font=("Helvetica", 24, "bold"),
                             text_color="white", fg_color="maroon")
    uni_label.place(relx=0.5, rely=0.50, anchor="center")

    # Scholarship system text
    sys_label = ctk.CTkLabel(splash, text="Scholarship Management System",
                             font=("Helvetica", 16),
                             text_color="white", fg_color="maroon")
    sys_label.place(relx=0.5, rely=0.65, anchor="center")

    # Loading dots
    dots_label = ctk.CTkLabel(splash, text="", font=("Helvetica", 18, "bold"),
                              text_color="white", fg_color="maroon")
    dots_label.place(relx=0.5, rely=0.80, anchor="center")

    # --------- Animations ---------
    def animate_dots(counter=0):
        dots_label.configure(text="." * ((counter % 3) + 1))
        splash.after(500, animate_dots, counter + 1)

    animate_dots()

    # Close splash after 4 seconds and open login
    splash.after(4000, lambda: [splash.destroy(),
                                subprocess.Popen(["python", "login.py"])])

    splash.mainloop()


if __name__ == "__main__":
    splash_screen()
