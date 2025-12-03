import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import os
import subprocess
import sys
import threading
import tempfile

class MaintainersDashboard(ctk.CTkToplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        # ---------------- DATABASE ---------------- #
        self.conn = sqlite3.connect("Scholarship.db", timeout=10)
        self.cursor = self.conn.cursor()
        self.title("Maintainers Dashboard")
        try:
            self.state("zoomed")
        except:
            pass

        # ---------------- HEADER ---------------- #
        header_height = 110
        header = ctk.CTkFrame(self, fg_color="#6F0000", height=header_height, corner_radius=0)
        header.pack(side="top", fill="x")
        header.grid_propagate(False)

        ctk.CTkLabel(header, text="BATANGAS STATE UNIVERSITY", font=("Arial Black", 34),
                     text_color="white").pack(pady=(20, 0))
        ctk.CTkLabel(header, text="SCHOLARSHIP MANAGEMENT SYSTEM", font=("Arial", 18),
                     text_color="white").pack()

        # ---------------- MAIN CONTENT ---------------- #
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=40, pady=20)

        top_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_frame.pack(fill="x", pady=(0, 20))

        back_btn = ctk.CTkButton(top_frame, text="← Back", width=120, height=40,
                                fg_color="#4a0000", hover_color="#7c0a02",
                                command=self.go_back)
        back_btn.pack(side="left")

        manage_label = ctk.CTkLabel(top_frame, text="Manage Maintainers", font=("Arial Black", 28),
                                    text_color="black")
        manage_label.place(relx=0.5, rely=0.5, anchor="center")

        # ---------------- Table container ---------------- #
        self.table_container = ctk.CTkFrame(self.main_frame, fg_color="#f2f2f2",
                                            corner_radius=10, width=1200, height=400)
        self.table_container.pack(fill="both", expand=True)
        self.table_container.pack_propagate(False)

        self.table_frame = ctk.CTkScrollableFrame(self.table_container, fg_color="white")
        self.table_frame.pack(fill="both", expand=True)

        self.load_maintainers()

    # ---------------- LOAD TABLE ---------------- #
    def load_maintainers(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        headers = ["Student ID", "Name", "Username", "Email", "Status", "Action"]
        for col, header in enumerate(headers):
            label = ctk.CTkLabel(self.table_frame, text=header, font=("Arial Black", 16),
                                fg_color="#7c0a02", text_color="white",
                                width=250, height=40)
            label.grid(row=0, column=col, padx=1, pady=1, sticky="nsew")

        self.cursor.execute("SELECT student_id, name, username, email, status FROM Maintainer")
        maintainers = self.cursor.fetchall()

        for row, entry in enumerate(maintainers, start=1):
            student_id, name, username, email, status = entry

            allowed_status = {"claimed": "claimed", "unclaimed": "unclaimed"}
            display_status = allowed_status.get(status.lower(), "not yet updated")

            values = [student_id, name, username, email, display_status]

            for col, value in enumerate(values):
                cell = ctk.CTkLabel(self.table_frame, text=value, font=("Arial", 14),
                                    width=250, height=40, fg_color="white", anchor="center")
                cell.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")

            action_frame = ctk.CTkFrame(self.table_frame, fg_color="white", width=250, height=40)
            action_frame.grid(row=row, column=len(headers)-1, padx=1, pady=1, sticky="nsew")
            action_frame.grid_propagate(False)
            action_frame.columnconfigure((0, 1), weight=1)

            view_btn = ctk.CTkButton(action_frame, text="View", width=80, height=30,
                                    command=lambda e=entry: self.view_maintainer(e))
            view_btn.grid(row=0, column=0, padx=5, pady=5)

            delete_btn = ctk.CTkButton(action_frame, text="Delete", width=80, height=30,
                                    fg_color="#B22222", hover_color="#FF0000",
                                    command=lambda e=entry: self.delete_maintainer(e[0]))
            delete_btn.grid(row=0, column=1, padx=5, pady=5)

        for col in range(len(headers)):
            self.table_frame.grid_columnconfigure(col, weight=1)

    # ---------------- VIEW / DELETE ---------------- #
    def view_maintainer(self, entry):
        student_id, name, username, email, status = entry
        self.ViewMaintainerRequirements(self, student_id)

    def delete_maintainer(self, student_id):
        if messagebox.askyesno(title="Confirm Delete", message="Are you sure you want to delete this maintainer?"):
            self.cursor.execute("DELETE FROM Maintainer WHERE student_id=?", (student_id,))
            self.conn.commit()
            self.load_maintainers()

    # ---------------- BACK ---------------- #
    def go_back(self):
        try:
            # Open adminchart.py again
            subprocess.Popen([sys.executable, "adminchart.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open adminchart.py\n{e}")

        # Close this window
        self.destroy()

    # ==========================================================================
    # ⭐ FULL WORKING ViewMaintainerRequirements (BLOB VERSION)
    # ==========================================================================
    class ViewMaintainerRequirements(ctk.CTkToplevel):
        def __init__(self, parent, student_id):
            super().__init__(parent)
            self.title("Maintainer's Requirements")
            self.geometry("520x380")
            self.resizable(False, False)

            # Center window
            self.update_idletasks()
            w, h = 520, 380
            x = (self.winfo_screenwidth() // 2) - (w // 2)
            y = (self.winfo_screenheight() // 2) - (h // 2)
            self.geometry(f"{w}x{h}+{x}+{y}")

            # DB
            self.conn = sqlite3.connect("Scholarship.db")
            self.cursor = self.conn.cursor()

            # Load BLOBs from Maintainer_Requirements
            self.cor_blob, self.tor_blob, self.gm_blob = self.load_from_db(student_id)

            ctk.CTkLabel(self, text=f"Requirements for Student ID {student_id}",
                         font=("Arial Black", 20)).pack(pady=20)

            # No files
            if not any([self.cor_blob, self.tor_blob, self.gm_blob]):
                ctk.CTkLabel(self, text="No requirements uploaded.", font=("Arial", 16)).pack(pady=20)
                return

            # Buttons
            if self.cor_blob:
                ctk.CTkButton(self, text="Open COR", width=200,
                    command=lambda: self.open_blob_with_loading("COR", self.cor_blob)
                ).pack(pady=10)

            if self.tor_blob:
                ctk.CTkButton(self, text="Open TOR", width=200,
                    command=lambda: self.open_blob_with_loading("TOR", self.tor_blob)
                ).pack(pady=10)

            if self.gm_blob:
                ctk.CTkButton(self, text="Open Good Moral", width=200,
                    command=lambda: self.open_blob_with_loading("GoodMoral", self.gm_blob)
                ).pack(pady=10)

        # ---------------- LOAD BLOB FROM TABLE ---------------- #
        def load_from_db(self, student_id):
            try:
                self.cursor.execute("""
                    SELECT COR, TOR, Good_Moral
                    FROM Maintainer_Requirements
                    WHERE maintainer_id = ?
                """, (student_id,))

                row = self.cursor.fetchone()
                if row:
                    return row[0], row[1], row[2]
            except Exception as e:
                messagebox.showerror("Database Error", str(e))

            return None, None, None

        # ---------------- OPEN FILE SAFELY ---------------- #
        def open_blob_file(self, name, blob_data):
            if not blob_data:
                return

            # Detect file type (default PDF)
            ext = ".pdf"
            if blob_data[:4] == b"\xFF\xD8\xFF\xE0":
                ext = ".jpg"
            elif blob_data[:8] == b"\x89PNG\r\n\x1a\n":
                ext = ".png"

            temp_path = os.path.join(tempfile.gettempdir(), f"{name}{ext}")

            with open(temp_path, "wb") as f:
                f.write(blob_data)

            try:
                if sys.platform.startswith("win"):
                    os.startfile(temp_path)
                elif sys.platform.startswith("darwin"):
                    subprocess.call(["open", temp_path])
                else:
                    subprocess.call(["xdg-open", temp_path])
            except Exception as e:
                messagebox.showerror("Open Error", str(e))

        # ---------------- LOADING LABEL WRAPPER ---------------- #
        def open_blob_with_loading(self, name, blob_data):
            loading = ctk.CTkLabel(self, text="Opening file...", font=("Arial", 14))
            loading.pack(pady=10)

            def task():
                self.open_blob_file(name, blob_data)
                loading.destroy()

            threading.Thread(target=task, daemon=True).start()


# ------------------ STANDALONE VERSION ------------------ #
class MaintainersDashboardStandalone(ctk.CTk):
    """Standalone version using CTk (not CTkToplevel) to avoid extra Tk window"""
    def __init__(self):
        super().__init__()

        # ---------------- DATABASE ---------------- #
        self.conn = sqlite3.connect("Scholarship.db", timeout=10)
        self.cursor = self.conn.cursor()
        self.title("Maintainers Dashboard")
        self.attributes('-fullscreen', True)  # True fullscreen mode

        # ---------------- HEADER ---------------- #
        header_height = 110
        header = ctk.CTkFrame(self, fg_color="#6F0000", height=header_height, corner_radius=0)
        header.pack(side="top", fill="x")
        header.grid_propagate(False)

        ctk.CTkLabel(header, text="BATANGAS STATE UNIVERSITY", font=("Arial Black", 34),
                     text_color="white").pack(pady=(20, 0))
        ctk.CTkLabel(header, text="SCHOLARSHIP MANAGEMENT SYSTEM", font=("Arial", 18),
                     text_color="white").pack()

        # ---------------- MAIN CONTENT ---------------- #
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=40, pady=20)

        top_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_frame.pack(fill="x", pady=(0, 20))

        back_btn = ctk.CTkButton(top_frame, text="← Back", width=120, height=40,
                                fg_color="#4a0000", hover_color="#7c0a02",
                                command=self.go_back)
        back_btn.pack(side="left")

        manage_label = ctk.CTkLabel(top_frame, text="Manage Maintainers", font=("Arial Black", 28),
                                    text_color="black")
        manage_label.place(relx=0.5, rely=0.5, anchor="center")

        # ---------------- Table container ---------------- #
        self.table_container = ctk.CTkFrame(self.main_frame, fg_color="#f2f2f2",
                                            corner_radius=10, width=1200, height=400)
        self.table_container.pack(fill="both", expand=True)
        self.table_container.pack_propagate(False)

        self.table_frame = ctk.CTkScrollableFrame(self.table_container, fg_color="white")
        self.table_frame.pack(fill="both", expand=True)

        self.load_maintainers()

    def load_maintainers(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        headers = ["Student ID", "Name", "Username", "Email", "Status", "Action"]
        for col, header in enumerate(headers):
            label = ctk.CTkLabel(self.table_frame, text=header, font=("Arial Black", 16),
                                fg_color="#7c0a02", text_color="white",
                                width=250, height=40)
            label.grid(row=0, column=col, padx=1, pady=1, sticky="nsew")

        self.cursor.execute("SELECT student_id, name, username, email, status FROM Maintainer")
        maintainers = self.cursor.fetchall()

        for row, entry in enumerate(maintainers, start=1):
            student_id, name, username, email, status = entry

            allowed_status = {"claimed": "claimed", "unclaimed": "unclaimed"}
            display_status = allowed_status.get(status.lower(), "not yet updated")

            values = [student_id, name, username, email, display_status]

            for col, value in enumerate(values):
                cell = ctk.CTkLabel(self.table_frame, text=value, font=("Arial", 14),
                                    width=250, height=40, fg_color="white", anchor="center")
                cell.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")

            action_frame = ctk.CTkFrame(self.table_frame, fg_color="white", width=250, height=40)
            action_frame.grid(row=row, column=len(headers)-1, padx=1, pady=1, sticky="nsew")
            action_frame.grid_propagate(False)
            action_frame.columnconfigure((0, 1), weight=1)

            view_btn = ctk.CTkButton(action_frame, text="View", width=80, height=30,
                                    command=lambda e=entry: self.view_maintainer(e))
            view_btn.grid(row=0, column=0, padx=5, pady=5)

            delete_btn = ctk.CTkButton(action_frame, text="Delete", width=80, height=30,
                                    fg_color="#B22222", hover_color="#FF0000",
                                    command=lambda e=entry: self.delete_maintainer(e[0]))
            delete_btn.grid(row=0, column=1, padx=5, pady=5)

        for col in range(len(headers)):
            self.table_frame.grid_columnconfigure(col, weight=1)

    def view_maintainer(self, entry):
        student_id = entry[0]
        ViewMaintainerRequirements(self, student_id)

    def delete_maintainer(self, student_id):
        if messagebox.askyesno(title="Confirm Delete", message="Are you sure you want to delete this maintainer?"):
            self.cursor.execute("DELETE FROM Maintainer WHERE student_id=?", (student_id,))
            self.conn.commit()
            self.load_maintainers()

    def go_back(self):
        try:
            subprocess.Popen([sys.executable, "adminchart.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open adminchart.py\n{e}")

        self.destroy()


# Separate ViewMaintainerRequirements class (used by both versions)
class ViewMaintainerRequirements(ctk.CTkToplevel):
    def __init__(self, parent, student_id):
        super().__init__(parent)
        self.title("Maintainer's Requirements")
        self.geometry("520x380")
        self.resizable(False, False)

        # Center window
        self.update_idletasks()
        w, h = 520, 380
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        # DB
        self.conn = sqlite3.connect("Scholarship.db")
        self.cursor = self.conn.cursor()

        # Load BLOBs from Maintainer_Requirements
        self.cor_blob, self.tor_blob, self.gm_blob = self.load_from_db(student_id)

        ctk.CTkLabel(self, text=f"Requirements for Student ID {student_id}",
                     font=("Arial Black", 20)).pack(pady=20)

        # No files
        if not any([self.cor_blob, self.tor_blob, self.gm_blob]):
            ctk.CTkLabel(self, text="No requirements uploaded.", font=("Arial", 16)).pack(pady=20)
            return

        # Buttons
        if self.cor_blob:
            ctk.CTkButton(self, text="Open COR", width=200,
                command=lambda: self.open_blob_with_loading("COR", self.cor_blob)
            ).pack(pady=10)

        if self.tor_blob:
            ctk.CTkButton(self, text="Open TOR", width=200,
                command=lambda: self.open_blob_with_loading("TOR", self.tor_blob)
            ).pack(pady=10)

        if self.gm_blob:
            ctk.CTkButton(self, text="Open Good Moral", width=200,
                command=lambda: self.open_blob_with_loading("GoodMoral", self.gm_blob)
            ).pack(pady=10)

    def load_from_db(self, student_id):
        try:
            self.cursor.execute("""
                SELECT COR, TOR, Good_Moral
                FROM Maintainer_Requirements
                WHERE maintainer_id = ?
            """, (student_id,))

            row = self.cursor.fetchone()
            if row:
                return row[0], row[1], row[2]
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

        return None, None, None

    def open_blob_file(self, name, blob_data):
        if not blob_data:
            return

        # Detect file type (default PDF)
        ext = ".pdf"
        if blob_data[:4] == b"\xFF\xD8\xFF\xE0":
            ext = ".jpg"
        elif blob_data[:8] == b"\x89PNG\r\n\x1a\n":
            ext = ".png"

        temp_path = os.path.join(tempfile.gettempdir(), f"{name}{ext}")

        with open(temp_path, "wb") as f:
            f.write(blob_data)

        try:
            if sys.platform.startswith("win"):
                os.startfile(temp_path)
            elif sys.platform.startswith("darwin"):
                subprocess.call(["open", temp_path])
            else:
                subprocess.call(["xdg-open", temp_path])
        except Exception as e:
            messagebox.showerror("Open Error", str(e))

    def open_blob_with_loading(self, name, blob_data):
        loading = ctk.CTkLabel(self, text="Opening file...", font=("Arial", 14))
        loading.pack(pady=10)

        def task():
            self.open_blob_file(name, blob_data)
            loading.destroy()

        threading.Thread(target=task, daemon=True).start()


# ------------------ RUN ------------------ #
if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")
    
    # Create hidden root window to avoid extra Tk window
    root = ctk.CTk()
    root.withdraw()  # Hide the root window
    
    # Create the dashboard as a Toplevel
    app = MaintainersDashboard(parent=root)
    
    # When dashboard closes, also close the hidden root
    def on_closing():
        root.destroy()
    
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()