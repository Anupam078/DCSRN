import tkinter as tk
from tkinter import messagebox
import threading
import config
import validation
import client_net

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
        
        # Threading state
        self.worker_result = None
        self.current_action = None

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

    def set_buttons_state(self, state):
        self.submit_button.config(state=state)
        self.refresh_button.config(state=state)

    def on_submit_click(self):
        name = self.name_var.get()
        roll = self.roll_var.get()
        email = self.email_var.get()
        course = self.course_var.get()
        ip = self.ip_var.get().strip()

        # Local validation
        err = validation.validate_fields(name, roll, email, course)
        if err:
            messagebox.showerror("Validation Error", err)
            return

        self.set_status("Registering...", config.COLOR_MUTED)
        self.set_buttons_state("disabled")
        
        request = {
            "action": "REGISTER",
            "name": name,
            "roll_number": roll,
            "email": email,
            "course": course
        }
        
        self.current_action = "REGISTER"
        self.worker_result = None
        
        # [Unit 5: multithreading]
        t = threading.Thread(target=self.network_worker, args=(ip, request), daemon=True)
        t.start()
        self.check_worker()

    def on_refresh_click(self):
        ip = self.ip_var.get().strip()
        self.set_status("Fetching courses...", config.COLOR_MUTED)
        self.set_buttons_state("disabled")
        
        request = {"action": "GET_COURSES"}
        self.current_action = "GET_COURSES"
        self.worker_result = None
        
        # [Unit 5: multithreading]
        t = threading.Thread(target=self.network_worker, args=(ip, request), daemon=True)
        t.start()
        self.check_worker()

    def network_worker(self, ip, request):
        # This runs in background thread
        res = client_net.send_request(ip, request)
        self.worker_result = res

    def check_worker(self):
        # [Unit 5: multithreading] main thread polling
        if self.worker_result is None:
            self.root.after(100, self.check_worker)
            return
            
        # Worker finished
        res = self.worker_result
        action = self.current_action
        
        self.set_buttons_state("normal")
        
        if res.get("status") == "ERROR":
            self.set_status(res.get("message", "Unknown error"), config.COLOR_ERROR)
            messagebox.showerror("Error", res.get("message", "Unknown error"))
        else:
            if action == "REGISTER":
                messagebox.showinfo("Success", res.get("message", "Registration successful!"))
                self.set_status("Registration successful!", config.COLOR_SUCCESS)
                self.on_clear_click()
            elif action == "GET_COURSES":
                courses = res.get("courses", {})
                current = self.course_var.get()
                left = courses.get(current, "?")
                self.seats_label.config(text=f"Seats left: {left}")
                self.set_status("Seats refreshed.", config.COLOR_SUCCESS)

    def on_clear_click(self):
        self.name_var.set("")
        self.roll_var.set("")
        self.email_var.set("")
        self.set_status("Ready", config.COLOR_INK)

    def on_course_change(self, value):
        self.seats_label.config(text="Seats left: ?")
        self.set_status("Course changed. Refresh to see seats.", config.COLOR_INK)

    def set_status(self, text, color):
        self.status_label.config(text=f"Status: {text}", fg=color)


if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()
