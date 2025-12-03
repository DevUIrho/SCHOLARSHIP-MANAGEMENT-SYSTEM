import customtkinter as ctk
from tkinter import filedialog, messagebox
import sqlite3
import os
import subprocess
import tkinter as tk


# ------------------------- CONFIG -------------------------
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

uploaded_files = {}
entry_fields = {}


# ------------------------- FUNCTIONS -------------------------
def pdf_to_blob(file_path):
    with open(file_path, "rb") as f:
        return f.read()


def browse_file(doc_field):
    file_path = filedialog.askopenfilename(
        title=f"Select {doc_field} File",
        filetypes=[("PDF Files", "*.pdf")]
    )
    if file_path:
        entry_fields[doc_field].delete(0, "end")
        entry_fields[doc_field].insert(0, os.path.basename(file_path))

        uploaded_files[doc_field] = file_path
        document_list.insert("end", f"{doc_field} - {os.path.basename(file_path)}")


def remove_selected():
    selected = document_list.curselection()
    if not selected:
        messagebox.showerror("Error", "Select a document to remove.")
        return

    item = document_list.get(selected[0])
    doc_field = item.split(" - ")[0]

    if doc_field in uploaded_files:
        del uploaded_files[doc_field]

    document_list.delete(selected[0])
    entry_fields[doc_field].delete(0, "end")


def submit_application():
    required_docs = ["COR", "TOR", "Good_Moral"]
    missing = [d for d in required_docs if d not in uploaded_files]

    if missing:
        messagebox.showerror("Error", f"Please upload: {', '.join(missing)}")
        return

    try:
        conn = sqlite3.connect("Scholarship.db")
        c = conn.cursor()

        # GET LAST REGISTERED APPLICANT ID
        c.execute("SELECT MAX(Applicant_id) FROM Applicants")
        applicant_id = c.fetchone()[0]

        if applicant_id is None:
            messagebox.showerror("Error", "No applicant found.")
            return

        cor_blob = pdf_to_blob(uploaded_files["COR"])
        tor_blob = pdf_to_blob(uploaded_files["TOR"])
        gm_blob = pdf_to_blob(uploaded_files["Good_Moral"])

        c.execute("""
            INSERT INTO Applicant_Requirements 
            (applicants_id, COR, "TOR", Good_Moral)
            VALUES (?, ?, ?, ?)
        """, (applicant_id, cor_blob, tor_blob, gm_blob))

        conn.commit()
        conn.close()

        messagebox.showinfo("Success", "PDF documents submitted successfully!")

        reset_form()

        subprocess.Popen(["python", "submit.py"])
        win.destroy()

    except sqlite3.Error as e:
        messagebox.showerror("Database Error", str(e))


def reset_form():
    for field in entry_fields.values():
        field.delete(0, "end")

    document_list.delete(0, "end")
    uploaded_files.clear()


# ------------------------- UI -------------------------
win = ctk.CTk()
win.title("Upload Scholarship Documents")

# 🔥 EXACT FIX — SAME AS LOGIN WINDOW
win.after(50, lambda: win.state("zoomed"))

win.configure(fg_color="white")


# ------------------------- HEADER -------------------------
header = ctk.CTkFrame(win, fg_color="#6F0000", height=110, corner_radius=0)
header.pack(fill="x")

ctk.CTkLabel(
    header,
    text="BATANGAS STATE UNIVERSITY",
    font=("Arial Black", 34),
    text_color="white"
).pack(pady=(10, 0))

ctk.CTkLabel(
    header,
    text="SCHOLARSHIP MANAGEMENT SYSTEM",
    font=("Arial", 18),
    text_color="white"
).pack(pady=(0, 10))


# ------------------------- CONTENT -------------------------
content = ctk.CTkFrame(win, fg_color="white")
content.pack(fill="both", expand=True, padx=20, pady=10)

heading = ctk.CTkLabel(
    content,
    text="II. UPLOAD REQUIRED DOCUMENTS",
    font=("Arial", 26, "bold"),
    text_color="#800000"
)
heading.pack(pady=(10, 20))


# ------------------------- DOCUMENT FIELDS -------------------------
doc_fields = ["COR", "TOR", "Good_Moral"]

for doc in doc_fields:
    frame = ctk.CTkFrame(content, fg_color="white")
    frame.pack(pady=10)

    ctk.CTkLabel(
        frame, text=doc,
        font=("Arial", 16, "bold"), text_color="#800000"
    ).pack(anchor="w", padx=10)

    entry = ctk.CTkEntry(
        frame,
        width=350, height=40,
        border_color="#800000",
        border_width=2,
        corner_radius=20,
        text_color="black",
        font=("Arial", 13)
    )
    entry.pack(side="left", padx=(10, 10))

    entry_fields[doc] = entry

    btn = ctk.CTkButton(
        frame,
        text="Browse",
        fg_color="#800000",
        hover_color="#A52A2A",
        width=110, height=40,
        corner_radius=20,
        command=lambda d=doc: browse_file(d)
    )
    btn.pack(side="left", padx=(5, 0))


# ------------------------- LISTBOX -------------------------
list_frame = ctk.CTkFrame(content, fg_color="white")
list_frame.pack(pady=20)

document_list = tk.Listbox(
    list_frame,
    width=80, height=8,
    bg="white", fg="black",
    font=("Arial", 12),
    selectbackground="#800000",
    selectforeground="white",
    highlightbackground="#800000",
    highlightthickness=2,
    relief="flat"
)
document_list.pack()


# ------------------------- FOOTER BUTTONS -------------------------
footer = ctk.CTkFrame(win, fg_color="white")
footer.pack(fill="x", side="bottom", pady=10)

remove_btn = ctk.CTkButton(
    footer,
    text="Remove Selected",
    fg_color="#800000",
    hover_color="#A52A2A",
    width=200, height=45,
    corner_radius=25,
    font=("Arial", 14, "bold"),
    command=remove_selected
)
remove_btn.pack(side="left", padx=80, pady=10)

submit_btn = ctk.CTkButton(
    footer,
    text="Submit Documents",
    fg_color="#800000",
    hover_color="#A52A2A",
    width=240, height=45,
    corner_radius=25,
    font=("Arial", 14, "bold"),
    command=submit_application
)
submit_btn.pack(side="right", padx=80, pady=10)


win.mainloop()
