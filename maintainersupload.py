import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
import sqlite3
import sys
import os

# ----------------------- COLORS -----------------------
MAROON       = "#7B1113"
BG           = "#FAFAFA"
TEXT         = "#1E1E1E"
CARD_BORDER  = "#E6E6E6"
ACTIVE_BG    = "#800000"
ACTIVE_HOVER = "#A52A2A"

ctk.set_appearance_mode("light")

# ----------------------- DATABASE -----------------------
DB_FILE = "Scholarship.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def get_maintainer_by_username(username):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT student_id, name FROM Maintainer WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"student_id": row[0], "name": row[1]}
    return None

def get_maintainer_requirements(maintainer_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT COR, TOR, GOOD_MORAL
        FROM Maintainer_requirements
        WHERE maintainer_id=?
    """, (maintainer_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"COR": row[0], "TOR": row[1], "GOOD_MORAL": row[2]}
    else:
        # if no record yet, create one
        conn = get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO Maintainer_requirements (maintainer_id) VALUES (?)", (maintainer_id,))
        conn.commit()
        conn.close()
        return {"COR": None, "TOR": None, "GOOD_MORAL": None}

def upload_document(maintainer_id, doc_type):
    file_path = filedialog.askopenfilename(
        title=f"Select {doc_type} file",
        filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
    )
    if not file_path:
        return
    # optionally, copy file to a local folder
    upload_dir = "uploaded_documents"
    os.makedirs(upload_dir, exist_ok=True)
    dest_file = os.path.join(upload_dir, f"{doc_type}_{maintainer_id}.pdf")
    try:
        with open(file_path, "rb") as src, open(dest_file, "wb") as dst:
            dst.write(src.read())
    except Exception as e:
        messagebox.showerror("Error", f"Failed to copy file: {e}")
        return

    conn = get_connection()
    c = conn.cursor()
    c.execute(f"UPDATE Maintainer_requirements SET {doc_type}=? WHERE maintainer_id=?", (dest_file, maintainer_id))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", f"{doc_type} uploaded successfully!")
    app.show_documents()  # refresh display

# ----------------------- DOCUMENT UPLOAD APP -----------------------
class MaintainerUploadApp(ctk.CTk):
    def __init__(self, maintainer):
        super().__init__()
        self.maintainer = maintainer
        self.title("Document Upload")
        self.geometry("700x500")
        self.configure(fg_color=BG)

        ctk.CTkLabel(self, text=f"Welcome, {self.maintainer['name']}", font=("Arial", 20, "bold"), text_color=MAROON).pack(pady=20)
        
        self.body_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=16, border_width=1, border_color=CARD_BORDER)
        self.body_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.show_documents()

    def show_documents(self):
        for widget in self.body_frame.winfo_children():
            widget.destroy()

        reqs = get_maintainer_requirements(self.maintainer["student_id"])
        
        for i, (doc, path) in enumerate(reqs.items()):
            status = "Uploaded" if path else "Not Uploaded"
            color = "green" if path else "red"

            row_frame = ctk.CTkFrame(self.body_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=10, padx=20)

            ctk.CTkLabel(row_frame, text=doc, font=("Segoe UI", 14, "bold")).pack(side="left", padx=10)
            ctk.CTkLabel(row_frame, text=status, text_color=color, font=("Segoe UI", 12)).pack(side="left", padx=10)

            ctk.CTkButton(row_frame, text=f"Upload {doc}", fg_color=MAROON, hover_color=ACTIVE_HOVER,
                          command=lambda d=doc: upload_document(self.maintainer["student_id"], d)).pack(side="right", padx=10)

# ----------------------- RUN -----------------------
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

    app = MaintainerUploadApp(maintainer)
    app.mainloop()
