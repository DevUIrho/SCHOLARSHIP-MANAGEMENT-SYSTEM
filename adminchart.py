import customtkinter as ctk
from tkinter import messagebox
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import subprocess
import sys

# Set appearance mode and color theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Import your custom modules
from New_Applicants import NewApplicantsDashboard
from Maintainers import MaintainersDashboard

class ScholarshipManagementSystem(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Batangas State University - Scholarship Management System")
        
        # Get screen dimensions and maximize
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}+0+0")
        
        # Configure database connection
        self.conn = sqlite3.connect("Scholarship.db", timeout=10)
        self.cursor = self.conn.cursor()
        
        # Create header
        self.create_header()
        
        # Create main container
        self.create_main_container()
        
        # Show dashboard by default
        self.show_dashboard()
        
        # Try to maximize after everything loads
        self.after(100, lambda: self.state('zoomed'))
    
    def create_header(self):
        header_height = 110
        header = ctk.CTkFrame(self, fg_color="#6F0000", height=header_height, corner_radius=0)
        header.pack(side="top", fill="x")
        header.grid_propagate(False)
        
        ctk.CTkLabel(header, text="BATANGAS STATE UNIVERSITY", 
                     font=("Arial Black", 34), text_color="white").pack(pady=(20, 0))
        ctk.CTkLabel(header, text="SCHOLARSHIP MANAGEMENT SYSTEM", 
                     font=("Arial", 18), text_color="white").pack()
    
    def create_main_container(self):
        # Main container
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Sidebar
        sidebar = ctk.CTkFrame(self.main_frame, fg_color="#6F0000", width=250, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        # Sidebar title
        ctk.CTkLabel(sidebar, text="Admin Dashboard", 
                     font=("Arial Black", 20), text_color="white").pack(pady=30)
        
        # Menu buttons
        self.create_menu_button(sidebar, "Dashboard", self.show_dashboard)
        self.create_menu_button(sidebar, "New Applicants List", self.open_new_applicants)
        self.create_menu_button(sidebar, "Maintainers List", self.open_maintainers)
        
        # Logout button at bottom
        logout_btn = ctk.CTkButton(sidebar, text="Logout", font=("Arial", 14), 
                                   fg_color="white", text_color="black",
                                   hover_color="#f0f0f0", corner_radius=25,
                                   height=50, command=self.logout)
        logout_btn.pack(side="bottom", fill="x", padx=15, pady=20)
        
        # Content area (changes based on selection)
        self.content_area = ctk.CTkFrame(self.main_frame, fg_color="white")
        self.content_area.pack(side="right", fill="both", expand=True)
    
    def create_menu_button(self, parent, text, command):
        btn = ctk.CTkButton(parent, text=text, font=("Arial", 14), 
                           fg_color="white", text_color="black",
                           hover_color="#f0f0f0", corner_radius=25,
                           height=50, command=command)
        btn.pack(fill="x", padx=15, pady=8)
    
    # ----- BUTTON FUNCTIONS -----
    def open_new_applicants(self):
        self.withdraw()
        subprocess.Popen([sys.executable, 'New_Applicants.py'])
        

    def open_maintainers(self):
        self.withdraw()
        subprocess.Popen([sys.executable, 'Maintainers.py'])

    
    def logout(self):
        """Handle logout functionality"""
        confirm = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if confirm:
            self.destroy()
            subprocess.Popen(["python", "login.py"])
    
    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        self.clear_content()
        
        # Main content frame with padding
        content = ctk.CTkScrollableFrame(self.content_area, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Title
        title_frame = ctk.CTkFrame(content, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(title_frame, text="Dashboard Overview", 
                     font=("Arial Black", 28), text_color="black").pack()
        
        # Get counts from database
        try:
            self.cursor.execute("SELECT COUNT(*) FROM Applicants")
            applicants_count = self.cursor.fetchone()[0]
        except:
            applicants_count = 0
            
        try:
            self.cursor.execute("SELECT COUNT(*) FROM Maintainer")
            maintainers_count = self.cursor.fetchone()[0]
        except:
            maintainers_count = 0
        
        # Get status counts - check for various possible status values
        try:
            # Get all distinct statuses first to debug
            self.cursor.execute("SELECT DISTINCT Status FROM Applicants")
            all_statuses = self.cursor.fetchall()
            print("Available statuses:", all_statuses)  # Debug print
            
            # Count accepted (try different variations)
            self.cursor.execute("SELECT COUNT(*) FROM Applicants WHERE LOWER(Status) IN ('accepted', 'approve', 'approved')")
            accepted_count = self.cursor.fetchone()[0]
        except:
            accepted_count = 0
            
        try:
            # Count pending (try different variations)
            self.cursor.execute("SELECT COUNT(*) FROM Applicants WHERE LOWER(Status) IN ('pending', 'waiting', 'in progress')")
            pending_count = self.cursor.fetchone()[0]
        except:
            pending_count = 0
            
        try:
            # Count rejected (try different variations)
            self.cursor.execute("SELECT COUNT(*) FROM Applicants WHERE LOWER(Status) IN ('rejected', 'declined', 'denied')")
            rejected_count = self.cursor.fetchone()[0]
        except:
            rejected_count = 0
        
        # Stats container - 5 cards in a row
        stats_container = ctk.CTkFrame(content, fg_color="transparent")
        stats_container.pack(fill="x", pady=20)
        
        # Configure grid for 5 columns
        for i in range(5):
            stats_container.grid_columnconfigure(i, weight=1)
        
        # Statistics cards
        self.create_stat_card(stats_container, "Total New Applicants", 
                             applicants_count, "#1f6aa5", 0)
        self.create_stat_card(stats_container, "Total Maintainers", 
                             maintainers_count, "#2b8a3e", 1)
        self.create_stat_card(stats_container, "Accepted", 
                             accepted_count, "#28a745", 2)
        self.create_stat_card(stats_container, "Pending", 
                             pending_count, "#ffc107", 3)
        self.create_stat_card(stats_container, "Rejected", 
                             rejected_count, "#dc3545", 4)
        
        # Graphs container
        graphs_container = ctk.CTkFrame(content, fg_color="transparent")
        graphs_container.pack(fill="both", expand=True, pady=20)
        
        # Configure grid - Left side for bar graphs, right side for pie graph
        graphs_container.grid_columnconfigure(0, weight=1)
        graphs_container.grid_columnconfigure(1, weight=1)
        
        # Left column for bar graphs
        left_column = ctk.CTkFrame(graphs_container, fg_color="transparent")
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Applicants Bar Graph
        self.create_applicants_bar_graph(left_column)
        
        # Maintainers Bar Graph
        self.create_maintainers_bar_graph(left_column)
        
        # Right column for pie graph
        right_column = ctk.CTkFrame(graphs_container, fg_color="transparent")
        right_column.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # Pie Graph
        self.create_status_pie_graph(right_column, accepted_count, pending_count, rejected_count)
    
    def create_applicants_bar_graph(self, parent):
        # Container
        graph_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        graph_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Title
        ctk.CTkLabel(graph_frame, text="Applicants Bar Graph", 
                     font=("Arial Black", 18), text_color="black").pack(pady=10)
        
        # Get data by course
        try:
            self.cursor.execute("SELECT Course, COUNT(*) FROM Applicants GROUP BY Course")
            course_data = self.cursor.fetchall()
            courses = [row[0] if row[0] else "Unknown" for row in course_data]
            counts = [row[1] for row in course_data]
        except:
            courses = ["No Data"]
            counts = [0]
        
        # Create figure
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # Create horizontal bar chart with courses on y-axis and counts on x-axis
        y_pos = range(len(courses))
        ax.barh(y_pos, counts, color='#1f6aa5')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(courses)
        ax.set_xlabel('Count')
        ax.set_ylabel('Courses')
        ax.invert_yaxis()  # Invert y-axis to have first course at top
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_maintainers_bar_graph(self, parent):
        # Container
        graph_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        graph_frame.pack(fill="both", expand=True)
        
        # Title
        ctk.CTkLabel(graph_frame, text="Maintainers Bar Graph", 
                     font=("Arial Black", 18), text_color="black").pack(pady=10)
        
        # Get data by course
        try:
            self.cursor.execute("SELECT course, COUNT(*) FROM Maintainer GROUP BY course")
            course_data = self.cursor.fetchall()
            courses = [row[0] if row[0] else "Unknown" for row in course_data]
            counts = [row[1] for row in course_data]
        except:
            courses = ["No Data"]
            counts = [0]
        
        # Create figure
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # Create horizontal bar chart with courses on y-axis and counts on x-axis
        y_pos = range(len(courses))
        ax.barh(y_pos, counts, color='#2b8a3e')
        ax.set_yticks(y_pos)
        ax.set_yticklabels(courses)
        ax.set_xlabel('Count')
        ax.set_ylabel('Courses')
        ax.invert_yaxis()  # Invert y-axis to have first course at top
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_status_pie_graph(self, parent, accepted, pending, rejected):
        # Container
        graph_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        graph_frame.pack(fill="both", expand=True)
        
        # Title
        ctk.CTkLabel(graph_frame, text="Accepted, Pending, Rejected Pie Graph", 
                     font=("Arial Black", 18), text_color="black").pack(pady=10)
        
        # Data
        labels = ['Accepted', 'Pending', 'Rejected']
        sizes = [accepted, pending, rejected]
        colors = ['#28a745', '#ffc107', '#dc3545']
        
        # Create figure
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        # Only show pie if there's data
        if sum(sizes) > 0:
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
        else:
            ax.text(0.5, 0.5, 'No Data Available', horizontalalignment='center',
                   verticalalignment='center', transform=ax.transAxes, fontsize=14)
            ax.axis('off')
        
        fig.tight_layout()
        
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_stat_card(self, parent, title, value, color, col):
        # Card frame - smaller height for 5 cards
        card = ctk.CTkFrame(parent, fg_color=color, width=180, height=120, corner_radius=10)
        card.grid(row=0, column=col, padx=10, pady=10, sticky="nsew")
        card.grid_propagate(False)
        
        # Value
        ctk.CTkLabel(card, text=str(value), font=("Arial Black", 36), 
                     text_color="white").pack(expand=True, pady=(20, 0))
        
        # Title
        ctk.CTkLabel(card, text=title, font=("Arial", 12), 
                     text_color="white").pack(expand=True, pady=(0, 15))

if __name__ == "__main__":
    app = ScholarshipManagementSystem()
    app.mainloop()