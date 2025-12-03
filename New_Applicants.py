import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import subprocess, sys, os, tempfile, threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ------------------ EMAIL CONFIGURATION ------------------ #
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "bsu.smsoffice@gmail.com",
    "sender_password": "eltk hyar kjve dbhu",  # Your app password
    "sender_name": "BSU Scholarship Office"
}

# ------------------ EMAIL SENDING FUNCTIONS ------------------ #
def send_acceptance_email(recipient_email, recipient_name, student_id):
    """Send acceptance email to the applicant (plain text only)"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg["Subject"] = "Scholarship Application Accepted - Batangas State University"
        msg["From"] = f"{EMAIL_CONFIG['sender_name']} <{EMAIL_CONFIG['sender_email']}>"
        msg["To"] = recipient_email

        # Plain text email body
        text_body = f"""
BATANGAS STATE UNIVERSITY
Scholarship Management System

Congratulations, {recipient_name}!

We are pleased to inform you that your scholarship application has been ACCEPTED.

Student ID: {student_id}
Status: ✓ Accepted

Your account has been upgraded to Scholar (Maintainer) status. You can now log in to the Scholarship Management System using your existing credentials.

Next Steps:
1. Log in to the scholarship portal using your username and password
2. Review your scholarship details and requirements
3. Keep your documents up to date
4. Contact the scholarship office if you have any questions

IMPORTANT: Please keep this email for your records.

If you have any questions or concerns, please don't hesitate to contact us.

Best regards,
Batangas State University
Scholarship Office

---
This is an automated message. Please do not reply to this email.
© 2025 Batangas State University. All rights reserved.
        """

        # Attach plain text only
        msg.attach(MIMEText(text_body, "plain"))

        # Send email
        with smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
            server.starttls()
            server.login(EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["sender_password"])
            server.send_message(msg)
        
        print(f"✓ Acceptance email sent to: {recipient_email}")
        return True

    except Exception as e:
        print(f"✗ Failed to send email to {recipient_email}: {str(e)}")
        return False


def send_decline_email(recipient_email, recipient_name, student_id):
    """Send decline email to the applicant (plain text only)"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg["Subject"] = "Scholarship Application Status - Batangas State University"
        msg["From"] = f"{EMAIL_CONFIG['sender_name']} <{EMAIL_CONFIG['sender_email']}>"
        msg["To"] = recipient_email

        # Plain text email body
        text_body = f"""
BATANGAS STATE UNIVERSITY
Scholarship Management System

Dear {recipient_name},

Thank you for your interest in the scholarship program at Batangas State University.

After careful review of your application, we regret to inform you that your scholarship application has not been approved at this time.

Student ID: {student_id}
Status: ✗ Not Approved

We understand this may be disappointing news. Please note that this decision does not reflect on your academic abilities or potential. Due to limited scholarship slots and high competition, we are unable to accommodate all qualified applicants.

We encourage you to:
• Explore other scholarship opportunities available at the university
• Reapply in future scholarship cycles
• Contact the scholarship office for feedback on your application

If you have any questions or would like to discuss other financial assistance options, please feel free to contact our office.

Thank you again for your application, and we wish you the best in your academic endeavors.

Best regards,
Batangas State University
Scholarship Office

---
This is an automated message. Please do not reply to this email.
© 2025 Batangas State University. All rights reserved.
        """

        # Attach plain text only
        msg.attach(MIMEText(text_body, "plain"))

        # Send email
        with smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
            server.starttls()
            server.login(EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["sender_password"])
            server.send_message(msg)
        
        print(f"✓ Decline email sent to: {recipient_email}")
        return True

    except Exception as e:
        print(f"✗ Failed to send email to {recipient_email}: {str(e)}")
        return False


# ------------------ VIEW REQUIREMENTS WINDOW ------------------ #
class ViewRequirementsWindow(ctk.CTkToplevel):
    def __init__(self, student_id):
        super().__init__()
        self.title(f"Requirements for Student ID {student_id}")
        self.geometry("520x380")
        self.resizable(False, False)

        # Center window
        self.update_idletasks()
        w, h = 520, 380
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        # DB connection
        self.conn = sqlite3.connect("Scholarship.db")
        self.cursor = self.conn.cursor()

        # Load BLOBs from Applicant_Requirements
        self.cor_blob, self.tor_blob, self.gm_blob = self.load_from_db(student_id)

        ctk.CTkLabel(self, text=f"Requirements for Student ID {student_id}",
                     font=("Arial Black", 20)).pack(pady=20)

        # No files
        if not any([self.cor_blob, self.tor_blob, self.gm_blob]):
            ctk.CTkLabel(self, text="No requirements uploaded.", font=("Arial", 16)).pack(pady=20)
            return

        # Buttons to open each document
        if self.cor_blob:
            ctk.CTkButton(self, text="Open COR", width=200,
                fg_color="#2b8a3e", hover_color="#1e6a2d",
                command=lambda: self.open_blob_with_loading("COR", self.cor_blob)).pack(pady=10)

        if self.tor_blob:
            ctk.CTkButton(self, text="Open TOR", width=200,
                fg_color="#2b8a3e", hover_color="#1e6a2d",
                command=lambda: self.open_blob_with_loading("TOR", self.tor_blob)).pack(pady=10)

        if self.gm_blob:
            ctk.CTkButton(self, text="Open Good Moral", width=200,
                fg_color="#2b8a3e", hover_color="#1e6a2d",
                command=lambda: self.open_blob_with_loading("GoodMoral", self.gm_blob)).pack(pady=10)

    # ---------------- LOAD BLOB FROM TABLE ---------------- #
    def load_from_db(self, student_id):
        try:
            # First, get the Applicant_id from Applicants table using StudentID
            self.cursor.execute("""
                SELECT Applicant_id FROM Applicants WHERE StudentID = ?
            """, (student_id,))
            
            applicant_row = self.cursor.fetchone()
            
            if not applicant_row:
                return None, None, None
            
            applicant_id = applicant_row[0]
            
            # Now get the requirements using the Applicant_id
            self.cursor.execute("""
                SELECT COR, TOR, Good_Moral
                FROM Applicant_Requirements
                WHERE applicants_Id = ?
            """, (applicant_id,))

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


# ------------------ NEW APPLICANTS DASHBOARD ------------------ #
class NewApplicantsDashboard(ctk.CTkToplevel):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

        # Database connection
        self.conn = sqlite3.connect("Scholarship.db", timeout=10)
        self.cursor = self.conn.cursor()

        self.title("New Applicants Dashboard")
        try:
            self.state("zoomed")
        except:
            pass

        # ---------------- HEADER ---------------- #
        header = ctk.CTkFrame(self, fg_color="#6F0000", height=110, corner_radius=0)
        header.pack(side="top", fill="x")
        header.grid_propagate(False)

        ctk.CTkLabel(header, text="BATANGAS STATE UNIVERSITY",
                     font=("Arial Black", 34), text_color="white").pack(pady=(10, 0))
        ctk.CTkLabel(header, text="SCHOLARSHIP MANAGEMENT SYSTEM",
                     font=("Arial", 18), text_color="white").pack()

        # ---------------- MAIN CONTENT ---------------- #
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=40, pady=(5, 20))

        # --------- BACK BUTTON --------- #
        top_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        top_frame.pack(fill="x", pady=(0, 10))

        back_btn = ctk.CTkButton(top_frame, text="← Back", width=120, height=40,
                                 fg_color="#4a0000", hover_color="#7c0a02",
                                 command=self.go_back)
        back_btn.pack(side="left")

        # Title
        title_label = ctk.CTkLabel(main_frame, text="New Applicants List",
                                   font=("Arial Black", 26), text_color="black")
        title_label.pack(pady=(0, 10))

        # ---------------- TABLE ---------------- #
        table_container = ctk.CTkFrame(main_frame, fg_color="#f2f2f2", corner_radius=10)
        table_container.pack(fill="both", expand=True)
        table_container.pack_propagate(False)

        table_frame = ctk.CTkScrollableFrame(table_container, fg_color="white")
        table_frame.pack(fill="both", expand=True)

        headers = ["StudentID", "Name", "Username", "Email", "Status", "Action"]
        for col, header in enumerate(headers):
            label = ctk.CTkLabel(table_frame, text=header, font=("Arial Black", 16),
                                 fg_color="#7c0a02", text_color="white",
                                 width=250, height=40)
            label.grid(row=0, column=col, padx=1, pady=1, sticky="nsew")

        # Load applicants
        self.cursor.execute("SELECT StudentID, Name, Username, Email, Status FROM Applicants")
        applicants = self.cursor.fetchall()

        for row, entry in enumerate(applicants, start=1):
            user_id = entry[0]
            for col, value in enumerate(entry):
                cell = ctk.CTkLabel(table_frame, text=value, font=("Arial", 14),
                                    width=250, height=40, fg_color="white", anchor="center")
                cell.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")

            action_frame = ctk.CTkFrame(table_frame, fg_color="white")
            action_frame.grid(row=row, column=5, padx=1, pady=1, sticky="nsew")
            action_frame.grid_columnconfigure(0, weight=1)
            action_frame.grid_columnconfigure(1, weight=1)
            action_frame.grid_columnconfigure(2, weight=1)

            # Accept button
            ctk.CTkButton(action_frame, text="Accept", width=70, height=30,
                          fg_color="#1f6aa5", hover_color="#174f7c",
                          command=lambda uid=user_id: self.accept_user(uid)).grid(row=0, column=0, padx=5)

            # View button
            ctk.CTkButton(action_frame, text="View", width=70, height=30,
                          fg_color="#2b8a3e", hover_color="#1e6a2d",
                          command=lambda uid=user_id: ViewRequirementsWindow(uid)).grid(row=0, column=1, padx=5)

            # Delete button
            ctk.CTkButton(action_frame, text="Delete", width=70, height=30,
                          fg_color="#7c0a02", hover_color="#580703",
                          command=lambda uid=user_id: self.delete_applicant(uid)).grid(row=0, column=2, padx=5)

        for col in range(len(headers)):
            table_frame.grid_columnconfigure(col, weight=1)

    # ---------------- ACCEPT FUNCTION WITH EMAIL AUTOMATION ---------------- #
    def accept_user(self, user_id):
        self.cursor.execute("""
            SELECT StudentID, Name, Username, Password, Email, School, Course,
                Year_Level, Phone_Number, GWA, Status
            FROM Applicants WHERE StudentID = ?
        """, (user_id,))
        user = self.cursor.fetchone()

        if not user:
            messagebox.showerror("Error", "Applicant not found.")
            return

        # Extract user details for email
        student_id, name, username, password, email = user[0], user[1], user[2], user[3], user[4]

        try:
            # Get the Applicant_id for this StudentID
            self.cursor.execute("SELECT Applicant_id FROM Applicants WHERE StudentID = ?", (user_id,))
            applicant_row = self.cursor.fetchone()
            
            if not applicant_row:
                messagebox.showerror("Error", "Applicant ID not found.")
                return
                
            applicant_id = applicant_row[0]
            
            # Get requirements from Applicant_Requirements
            self.cursor.execute("""
                SELECT COR, TOR, Good_Moral 
                FROM Applicant_Requirements 
                WHERE applicants_id = ?
            """, (applicant_id,))
            requirements = self.cursor.fetchone()
            
            # Transfer requirements if they exist
            if requirements:
                self.cursor.execute("""
                    INSERT INTO Maintainer_Requirements (maintainer_id, COR, TOR, GOOD_MORAL)
                    VALUES (?, ?, ?, ?)
                """, (user_id, requirements[0], requirements[1], requirements[2]))
                
                # Delete old requirements
                self.cursor.execute("DELETE FROM Applicant_Requirements WHERE applicants_id = ?", (applicant_id,))

            # Insert into Maintainer
            self.cursor.execute("""
                INSERT INTO Maintainer (
                    student_id, name, username, password, email, school, course,
                    yearlevel, phone_number, gwa, status
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, user)

            # Delete applicant record
            self.cursor.execute("DELETE FROM Applicants WHERE StudentID = ?", (user_id,))

            # Commit all database changes
            self.conn.commit()
            
            # Send acceptance email in a separate thread (non-blocking)
            def send_email_async():
                email_sent = send_acceptance_email(email, name, student_id)
                if email_sent:
                    print(f"✓ Acceptance notification sent to {name} ({email})")
                else:
                    print(f"✗ Failed to send email to {name} ({email})")
            
            # Start email sending in background
            threading.Thread(target=send_email_async, daemon=True).start()
            
            # Show success message
            messagebox.showinfo("Success", 
                f"✓ {name} has been accepted as Scholar!\n\n"
                f"📧 An acceptance email is being sent to:\n{email}\n\n"
                f"The applicant can now log in with their credentials.")

            # Refresh page
            self.destroy()
            NewApplicantsDashboard(self.parent)

        except sqlite3.Error as e:
            self.conn.rollback()
            messagebox.showerror("Database Error", str(e))

    # ---------------- DELETE FUNCTION WITH EMAIL AUTOMATION ---------------- #
    def delete_applicant(self, user_id):
        """Delete applicant and send decline notification email"""
        confirm = messagebox.askyesno("Confirm Delete", 
            "Are you sure you want to decline this applicant?\n\n"
            "This will permanently remove their application and send them a decline notification email.")
        
        if confirm:
            try:
                # Get applicant details for email before deletion
                self.cursor.execute("""
                    SELECT StudentID, Name, Email 
                    FROM Applicants 
                    WHERE StudentID = ?
                """, (user_id,))
                
                applicant_data = self.cursor.fetchone()
                
                if not applicant_data:
                    messagebox.showerror("Error", "Applicant not found.")
                    return
                
                student_id, name, email = applicant_data
                
                # Get applicant_id for requirements deletion
                self.cursor.execute("SELECT Applicant_id FROM Applicants WHERE StudentID = ?", (user_id,))
                applicant_row = self.cursor.fetchone()
                
                if applicant_row:
                    applicant_id = applicant_row[0]
                    # Delete requirements first
                    self.cursor.execute("DELETE FROM Applicant_Requirements WHERE applicants_id = ?", (applicant_id,))
                
                # Delete applicant
                self.cursor.execute("DELETE FROM Applicants WHERE StudentID = ?", (user_id,))
                self.conn.commit()
                
                # Send decline email in background
                def send_email_async():
                    email_sent = send_decline_email(email, name, student_id)
                    if email_sent:
                        print(f"✓ Decline notification sent to {name} ({email})")
                    else:
                        print(f"✗ Failed to send decline email to {name} ({email})")
                
                # Start email sending in background
                threading.Thread(target=send_email_async, daemon=True).start()
                
                # Show success message
                messagebox.showinfo("Application Declined", 
                    f"✓ {name}'s application has been declined.\n\n"
                    f"📧 A decline notification is being sent to:\n{email}\n\n"
                    f"The applicant and their requirements have been removed.")
                
                # Refresh page
                self.destroy()
                NewApplicantsDashboard(self.parent)
                
            except sqlite3.Error as e:
                self.conn.rollback()
                messagebox.showerror("Database Error", str(e))

    # ---------------- BACK FUNCTION ---------------- #
    def go_back(self):
        try:
            subprocess.Popen([sys.executable, "adminchart.py"])
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open adminchart.py\n{e}")
        self.destroy()


# ------------------ MAIN ------------------ #
if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")
    
    # Create hidden root window to avoid extra Tk window
    root = ctk.CTk()
    root.withdraw()  # Hide the root window
    
    # Create the dashboard as a Toplevel
    app = NewApplicantsDashboard(parent=root)
    
    # When dashboard closes, also close the hidden root
    def on_closing():
        root.destroy()
    
    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()