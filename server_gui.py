import tkinter as tk
from tkinter import messagebox
import socket
import config
from server import RegistrationServer

class ServerDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("DCSRN - Server Dashboard")
        self.root.geometry("720x600")
        self.root.configure(bg=config.COLOR_BG)
        
        self.server = RegistrationServer()
        self.log_shown = 0
        self.course_rows = {}
        
        # Build UI
        self.main_frame = tk.Frame(root, bg=config.COLOR_BG, padx=20, pady=20)
        self.main_frame.pack(fill="both", expand=True)
        
        self.build_header(self.main_frame)
        self.build_info(self.main_frame)
        self.build_courses(self.main_frame)
        self.build_log(self.main_frame)
        self.build_buttons(self.main_frame)

    def build_header(self, parent):
        frame = tk.Frame(parent, bg=config.COLOR_BG)
        frame.pack(fill="x", pady=(0, 15))
        lbl = tk.Label(frame, text="Registration Server Dashboard", font=config.FONT_TITLE, bg=config.COLOR_BG, fg=config.COLOR_INK)
        lbl.pack(anchor="w")

    def build_info(self, parent):
        frame = tk.Frame(parent, bg=config.COLOR_CARD, padx=10, pady=10, relief="flat")
        frame.pack(fill="x", pady=(0, 15))
        
        ip = self.get_my_ip()
        self.status_label = tk.Label(frame, text="Status: Stopped", font=config.FONT_BODY, bg=config.COLOR_CARD, fg=config.COLOR_ERROR)
        self.status_label.grid(row=0, column=0, sticky="w", padx=(0, 20))
        
        address_label = tk.Label(frame, text=f"Address: {ip} : {config.PORT}", font=config.FONT_BODY, bg=config.COLOR_CARD, fg=config.COLOR_INK)
        address_label.grid(row=0, column=1, sticky="w", padx=(0, 20))
        
        self.total_label = tk.Label(frame, text="Total registrations: 0", font=config.FONT_BODY, bg=config.COLOR_CARD, fg=config.COLOR_INK)
        self.total_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))

    def build_courses(self, parent):
        frame = tk.Frame(parent, bg=config.COLOR_CARD, padx=10, pady=10, relief="flat")
        frame.pack(fill="x", pady=(0, 15))
        
        # Headers
        tk.Label(frame, text="Course", font=config.FONT_BOLD, bg=config.COLOR_CARD, fg=config.COLOR_INK, width=30, anchor="w").grid(row=0, column=0, sticky="w")
        tk.Label(frame, text="Taken / Total", font=config.FONT_BOLD, bg=config.COLOR_CARD, fg=config.COLOR_INK, width=15).grid(row=0, column=1)
        tk.Label(frame, text="Left", font=config.FONT_BOLD, bg=config.COLOR_CARD, fg=config.COLOR_INK, width=10).grid(row=0, column=2)
        
        row_idx = 1
        for cname, total in config.COURSES.items():
            name_lbl = tk.Label(frame, text=cname, font=config.FONT_BODY, bg=config.COLOR_CARD, fg=config.COLOR_INK, width=30, anchor="w")
            name_lbl.grid(row=row_idx, column=0, sticky="w", pady=2)
            
            taken_lbl = tk.Label(frame, text=f"0 / {total}", font=config.FONT_BODY, bg=config.COLOR_CARD, fg=config.COLOR_INK, width=15)
            taken_lbl.grid(row=row_idx, column=1, pady=2)
            
            left_lbl = tk.Label(frame, text=str(total), font=config.FONT_BODY, bg=config.COLOR_CARD, fg=config.COLOR_SUCCESS, width=10)
            left_lbl.grid(row=row_idx, column=2, pady=2)
            
            self.course_rows[cname] = (taken_lbl, left_lbl)
            row_idx += 1

    def build_log(self, parent):
        frame = tk.Frame(parent, bg=config.COLOR_BG)
        frame.pack(fill="both", expand=True, pady=(0, 15))
        
        tk.Label(frame, text="Activity log", font=config.FONT_BOLD, bg=config.COLOR_BG, fg=config.COLOR_INK).pack(anchor="w", pady=(0, 5))
        
        text_frame = tk.Frame(frame)
        text_frame.pack(fill="both", expand=True)
        
        self.log_text = tk.Text(text_frame, font=config.FONT_MONO, height=12, state="disabled", bg=config.COLOR_CARD, fg=config.COLOR_INK, relief="flat", padx=5, pady=5)
        self.log_text.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(text_frame, command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)

    def build_buttons(self, parent):
        frame = tk.Frame(parent, bg=config.COLOR_BG)
        frame.pack(fill="x")
        
        self.start_btn = tk.Button(frame, text="Start Server", command=self.on_start_click, bg=config.COLOR_ACCENT, fg="white", font=config.FONT_BOLD, relief="flat", padx=14, pady=6)
        self.start_btn.pack(side="left", padx=(0, 10))
        
        self.reset_btn = tk.Button(frame, text="Reset Data", command=self.on_reset_click, bg=config.COLOR_CARD, fg=config.COLOR_INK, font=config.FONT_BOLD, relief="flat", padx=14, pady=6)
        self.reset_btn.pack(side="left", padx=(0, 10))
        
        quit_btn = tk.Button(frame, text="Quit", command=self.on_quit_click, bg=config.COLOR_CARD, fg=config.COLOR_INK, font=config.FONT_BOLD, relief="flat", padx=14, pady=6)
        quit_btn.pack(side="right")

    def get_my_ip(self):
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"

    def on_start_click(self):
        try:
            self.server.start()
            self.start_btn.config(state="disabled")
            self.status_label.config(text="Status: ● Running", fg=config.COLOR_SUCCESS)
            self.refresh()
        except OSError:
            messagebox.showerror("Error", f"Port {config.PORT} is already in use.\nClose any other server instance.")

    def on_reset_click(self):
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to clear all registrations? This cannot be undone."):
            self.server.reset_data()

    def on_quit_click(self):
        self.root.destroy()

    def refresh(self):
        # [Unit 5: Tkinter] main thread polls for updates
        snapshot = self.server.get_snapshot()
        
        # Update total
        self.total_label.config(text=f"Total registrations: {snapshot['total']}")
        
        # Update courses
        for cname, left in snapshot["seats_left"].items():
            if cname in self.course_rows:
                total = config.COURSES[cname]
                taken = total - left
                taken_lbl, left_lbl = self.course_rows[cname]
                
                taken_lbl.config(text=f"{taken} / {total}")
                left_lbl.config(text=str(left))
                
                if left <= 0:
                    left_lbl.config(fg=config.COLOR_ERROR)
                else:
                    left_lbl.config(fg=config.COLOR_SUCCESS)
        
        # Update log
        logs = snapshot["log"]
        if len(logs) > self.log_shown:
            for line in logs[self.log_shown:]:
                self.append_log(line)
            self.log_shown = len(logs)
            
        # Schedule next refresh
        self.root.after(config.REFRESH_MS, self.refresh)

    def append_log(self, line):
        self.log_text.config(state="normal")
        self.log_text.insert("end", line + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerDashboard(root)
    root.mainloop()
