import tkinter as tk
import config

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DCSRN - Admission Desk")
        self.root.geometry("480x560")
        self.root.resizable(False, False)
        self.root.configure(bg=config.COLOR_BG)

        # Variables
        self.ip_var = tk.StringVar(value=config.DEFAULT_SERVER_IP)
        self.name_var = tk.StringVar()
        self.roll_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.course_var = tk.StringVar(value=list(config.COURSES.keys())[0])

        # Main frame
        self.main_frame = tk.Frame(root, bg=config.COLOR_BG, padx=20, pady=20)
        self.main_frame.pack(fill="both", expand=True)

        self.build_header(self.main_frame)
        self.build_server_row(self.main_frame)
        self.build_form(self.main_frame)
        self.build_buttons(self.main_frame)
        self.build_status(self.main_frame)

    def build_header(self, parent):
        frame = tk.Frame(parent, bg=config.COLOR_BG)
        frame.pack(fill="x", pady=(0, 20))
        tk.Label(frame, text="Student Registration Desk", font=config.FONT_TITLE, bg=config.COLOR_BG, fg=config.COLOR_INK).pack(anchor="w")
        tk.Label(frame, text="Distributed Client-Server Registration", font=config.FONT_BODY, bg=config.COLOR_BG, fg=config.COLOR_MUTED).pack(anchor="w")

    def build_server_row(self, parent):
        frame = tk.Frame(parent, bg=config.COLOR_CARD, padx=15, pady=15, relief="flat")
        frame.pack(fill="x", pady=(0, 20))
        tk.Label(frame, text="Server IP", font=config.FONT_BOLD, bg=config.COLOR_CARD, fg=config.COLOR_INK).pack(side="left", padx=(0, 10))
        tk.Entry(frame, textvariable=self.ip_var, font=config.FONT_BODY, width=20).pack(side="left")

    def build_form(self, parent):
        frame = tk.Frame(parent, bg=config.COLOR_CARD, padx=15, pady=15, relief="flat")
        frame.pack(fill="x", pady=(0, 20))

        # Using grid inside the form frame
        tk.Label(frame, text="Student Name", font=config.FONT_BODY, bg=config.COLOR_CARD, fg=config.COLOR_INK).grid(row=0, column=0, sticky="w", pady=10)
        tk.Entry(frame, textvariable=self.name_var, font=config.FONT_BODY, width=25).grid(row=0, column=1, pady=10, padx=(10, 0))

        tk.Label(frame, text="Roll Number", font=config.FONT_BODY, bg=config.COLOR_CARD, fg=config.COLOR_INK).grid(row=1, column=0, sticky="w", pady=10)
        tk.Entry(frame, textvariable=self.roll_var, font=config.FONT_BODY, width=25).grid(row=1, column=1, pady=10, padx=(10, 0))

        tk.Label(frame, text="Email", font=config.FONT_BODY, bg=config.COLOR_CARD, fg=config.COLOR_INK).grid(row=2, column=0, sticky="w", pady=10)
        tk.Entry(frame, textvariable=self.email_var, font=config.FONT_BODY, width=25).grid(row=2, column=1, pady=10, padx=(10, 0))

        tk.Label(frame, text="Course", font=config.FONT_BODY, bg=config.COLOR_CARD, fg=config.COLOR_INK).grid(row=3, column=0, sticky="w", pady=10)
        courses = list(config.COURSES.keys())
        course_menu = tk.OptionMenu(frame, self.course_var, *courses, command=self.on_course_change)
        course_menu.config(font=config.FONT_BODY, bg=config.COLOR_CARD, fg=config.COLOR_INK)
        course_menu.grid(row=3, column=1, sticky="ew", pady=10, padx=(10, 0))

        self.seats_label = tk.Label(frame, text="Seats left: ?", font=config.FONT_BODY, bg=config.COLOR_CARD, fg=config.COLOR_INK)
        self.seats_label.grid(row=4, column=1, sticky="w", padx=(10, 0))

    def build_buttons(self, parent):
        frame = tk.Frame(parent, bg=config.COLOR_BG)
        frame.pack(fill="x", pady=(0, 20))
        
        self.submit_button = tk.Button(frame, text="Submit", command=self.on_submit_click, bg=config.COLOR_ACCENT, fg="white", font=config.FONT_BOLD, relief="flat", padx=14, pady=6)
        self.submit_button.pack(side="left", padx=(0, 10))
        
        self.clear_button = tk.Button(frame, text="Clear", command=self.on_clear_click, bg=config.COLOR_CARD, fg=config.COLOR_INK, font=config.FONT_BOLD, relief="flat", padx=14, pady=6)
        self.clear_button.pack(side="left", padx=(0, 10))
        
        self.refresh_button = tk.Button(frame, text="Refresh Seats", command=self.on_refresh_click, bg=config.COLOR_CARD, fg=config.COLOR_INK, font=config.FONT_BOLD, relief="flat", padx=14, pady=6)
        self.refresh_button.pack(side="right")

    def build_status(self, parent):
        frame = tk.Frame(parent, bg=config.COLOR_BG)
        frame.pack(fill="x")
        self.status_label = tk.Label(frame, text="Status: Ready", font=config.FONT_BODY, bg=config.COLOR_BG, fg=config.COLOR_INK)
        self.status_label.pack(anchor="w")

    def on_submit_click(self):
        print("Submit button clicked")
        self.set_status("Submit clicked", config.COLOR_INK)

    def on_clear_click(self):
        print("Clear button clicked")
        self.name_var.set("")
        self.roll_var.set("")
        self.email_var.set("")
        self.set_status("Ready", config.COLOR_INK)

    def on_refresh_click(self):
        print("Refresh Seats button clicked")
        self.set_status("Refresh clicked", config.COLOR_INK)

    def on_course_change(self, value):
        print(f"Course changed to {value}")
        self.seats_label.config(text="Seats left: ?")

    def set_status(self, text, color):
        self.status_label.config(text=f"Status: {text}", fg=color)

# TEMP TEST: remove in Phase 10
if __name__ == "__main__":
    def test_client_layout():
        root = tk.Tk()
        app = ClientApp(root)
        
        def run_tests():
            print("Simulating UI interactions...")
            app.name_var.set("Test Name")
            app.roll_var.set("12345")
            app.email_var.set("test@example.com")
            print(f"Fields populated: {app.name_var.get()}, {app.roll_var.get()}, {app.email_var.get()}")
            
            app.on_submit_click()
            app.on_refresh_click()
            app.course_var.set(list(config.COURSES.keys())[1])
            app.on_course_change(app.course_var.get())
            app.on_clear_click()
            
            print(f"Fields after clear: Name='{app.name_var.get()}', Roll='{app.roll_var.get()}', Email='{app.email_var.get()}'")
            root.destroy()
            
        root.after(500, run_tests)
        root.mainloop()

    test_client_layout()
