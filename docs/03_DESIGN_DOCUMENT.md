# Design Document (UI + Code Structure)

This document says exactly what each screen looks like and what each file/function must contain. Follow it literally.

## 1. Visual Theme (matches our presentation)

Put these in `config.py`:

| Constant | Value | Use |
|---|---|---|
| `COLOR_BG` | `"#EEEEE6"` | Window background (cream) |
| `COLOR_CARD` | `"#F8F8F2"` | Entry/panel background |
| `COLOR_INK` | `"#2B2D2F"` | Main text |
| `COLOR_MUTED` | `"#5A5C5E"` | Secondary text |
| `COLOR_ACCENT` | `"#8B5CF6"` | Buttons, headings accent (purple) |
| `COLOR_SUCCESS` | `"#2E7D32"` | Success status text |
| `COLOR_ERROR` | `"#C62828"` | Error/full status text |
| `FONT_TITLE` | `("Georgia", 20)` | Window title label |
| `FONT_BODY` | `("Helvetica", 11)` | Labels, entries |
| `FONT_BOLD` | `("Helvetica", 11, "bold")` | Buttons, headings |
| `FONT_MONO` | `("Courier", 10)` | Activity log |

Button style: `bg=COLOR_ACCENT, fg="white", font=FONT_BOLD, relief="flat", padx=14, pady=6`. Secondary (Clear): `bg=COLOR_CARD, fg=COLOR_INK`.
Only core `tkinter` widgets and attributes (sizes, fonts, colours). No `ttk`.

## 2. Client Window: `ClientApp`

Size `480x560`, `resizable(False, False)`, title `"DCSRN - Admission Desk"`.

```
┌──────────────────────────────────────────────┐
│  Student Registration Desk                    │ header_frame
│  Distributed Client-Server Registration       │
├──────────────────────────────────────────────┤
│  Server IP  [ 127.0.0.1            ]          │ server_frame
├──────────────────────────────────────────────┤
│  Student Name   [____________________]        │
│  Roll Number    [____________________]        │ form_frame
│  Email          [____________________]        │ (grid layout)
│  Course         [ CSE3011 Python Prog.  v ]   │
│                 Seats left: 4                 │
├──────────────────────────────────────────────┤
│  [ Submit ]  [ Clear ]  [ Refresh Seats ]     │ button_frame
├──────────────────────────────────────────────┤
│  Status: Ready                                │ status_frame
└──────────────────────────────────────────────┘
```

### Widget tree (nested frames)

```
root (Tk)
└── main_frame (Frame, padding 20)
    ├── header_frame
    │   ├── title_label      (FONT_TITLE)
    │   └── subtitle_label   (FONT_BODY, muted)
    ├── server_frame
    │   ├── Label "Server IP"
    │   └── ip_entry         (StringVar ip_var, default DEFAULT_SERVER_IP)
    ├── form_frame           (use .grid(row, column))
    │   ├── Label + Entry    name_entry    (name_var)
    │   ├── Label + Entry    roll_entry    (roll_var)
    │   ├── Label + Entry    email_entry   (email_var)
    │   ├── Label + OptionMenu course_menu (course_var, values = list(COURSES))
    │   └── seats_label      ("Seats left: ?")
    ├── button_frame
    │   ├── submit_button    command=self.on_submit_click
    │   ├── clear_button     command=self.on_clear_click
    │   └── refresh_button   command=self.on_refresh_click
    └── status_frame
        └── status_label     (text + colour change)
```

Use `pack()` for frames (top to bottom) and `grid()` inside `form_frame`. Do not mix `pack` and `grid` in the same parent.

### Client class spec (`client_gui.py`)

```
class ClientApp:
    __init__(self, root)            # create StringVars, call build_* methods, then refresh seats once
    build_header(self, parent)
    build_server_row(self, parent)
    build_form(self, parent)
    build_buttons(self, parent)
    build_status(self, parent)

    on_submit_click(self)           # validate -> disable button -> run_in_background(request, "REGISTER")
    on_clear_click(self)            # empty name/roll/email, reset status
    on_refresh_click(self)          # run_in_background({"action":"GET_COURSES"}, "COURSES")
    on_course_change(self, value)   # update seats_label from self.seats_info (no network)

    run_in_background(self, request, kind)   # sets self.result=None, self.pending_kind=kind,
                                             # starts daemon Thread(target=self.worker), then after(100, check_result)
    worker(self, request)                    # [worker thread] self.result = send_request(ip, request)
    check_result(self)                       # [main thread] if self.result is None: after(100, check_result) again
                                             #  else call handle_register_reply / handle_courses_reply
    handle_register_reply(self, reply)       # dialogs + status colour + re-enable Submit + refresh seats
    handle_courses_reply(self, reply)        # store dict in self.seats_info, update seats_label
    set_status(self, text, color)
```

Entry point:
```
if __name__ == "__main__":
    root = tk.Tk()
    ClientApp(root)
    root.mainloop()
```

### Client events

| Event | Handler | What happens |
|---|---|---|
| Window opens | `__init__` | Builds UI, requests seat counts in background |
| Click **Submit** | `on_submit_click` | `validate_fields()`: error → `showwarning`; OK → disable button, status "Sending...", background REGISTER |
| Reply arrives (poll finds `self.result`) | `check_result` | OK → `showinfo`; DUPLICATE/FULL/INVALID/BAD_COURSE → `showwarning`; others → `showerror`. Re-enable Submit. Refresh seats |
| Click **Clear** | `on_clear_click` | Fields emptied, status "Ready" |
| Click **Refresh Seats** | `on_refresh_click` | Background GET_COURSES, seats label updates |
| Change course in dropdown | `on_course_change` | Seats label updates from stored info |

### Client dialogs (exact text)

| Case | Function | Title | Message |
|---|---|---|---|
| Validation error | `showwarning` | `Check your input` | message from `validate_fields` |
| Success | `showinfo` | `Registration successful` | `Registered {roll} in {course}.\nSeats left: {n}` |
| Duplicate | `showwarning` | `Already registered` | `Roll number {roll} is already registered.` |
| Full | `showwarning` | `Course full` | `No seats left in {course}.` |
| Network error | `showerror` | `Cannot reach server` | `Could not connect to {ip}:{port}.\nIs the server running?` |
| Other server error | `showerror` | `Server error` | server's `message` |

### Validation rules (`validation.py`: used by client AND server)

`validate_fields(name, roll_number, email, course)` returns `""` if OK, otherwise an error message string.

| Field | Rule | Message |
|---|---|---|
| Name | 2–50 characters after `.strip()`, no comma | `Name must be 2-50 characters (no commas).` |
| Roll number | 5–15 characters, letters and digits only (`.isalnum()`), upper-cased before saving | `Roll number must be 5-15 letters/digits.` |
| Email | ≤ 60 chars, no spaces, no comma, has `@`, and a `.` after the `@` | `Enter a valid email address.` |
| Course | Not empty | `Please select a course.` |

Only plain string methods (`strip`, `isalnum`, `in`, `find`, `len`). No regular expressions.

## 3. Server Dashboard: `ServerDashboard`

Size `720x600`, title `"DCSRN - Server Dashboard"`.

```
┌────────────────────────────────────────────────────────┐
│  Registration Server Dashboard                          │ header_frame
├────────────────────────────────────────────────────────┤
│  Status: ● Running      Address: 192.168.1.5 : 5050     │ info_frame
│  Total registrations: 7                                 │
├────────────────────────────────────────────────────────┤
│  Course                          Taken / Total   Left   │ courses_frame
│  CSE3011 Python Programming         3 / 5         2     │ (one row per course)
│  CSE2001 Data Structures            3 / 3         0     │
│  CSE2005 Database Systems           1 / 4         3     │
├────────────────────────────────────────────────────────┤
│  Activity log                                           │ log_frame
│  ┌────────────────────────────────────────────────┐    │ (Text + Scrollbar)
│  │ 14:32:10 24BCE10354 registered in CSE3011 ...  │    │
│  │ 14:32:11 FULL: CSE2001 rejected 25BOE10105     │    │
│  └────────────────────────────────────────────────┘    │
├────────────────────────────────────────────────────────┤
│  [ Start Server ]   [ Reset Data ]   [ Quit ]           │ button_frame
└────────────────────────────────────────────────────────┘
```

Rows with `Left = 0` show the "Left" number in `COLOR_ERROR`; others in `COLOR_SUCCESS`.

### Widget tree
```
root
└── main_frame
    ├── header_frame      title_label
    ├── info_frame        status_label, address_label, total_label
    ├── courses_frame     header row + one row per course (name_label, taken_label, left_label), stored in self.course_rows (dict)
    ├── log_frame         log_text (Text, state="disabled", height 12), scrollbar
    └── button_frame      start_button, reset_button, quit_button
```

### Dashboard class spec (`server_gui.py`)

```
class ServerDashboard:
    __init__(self, root)          # create RegistrationServer, build UI
    build_header / build_info / build_courses / build_log / build_buttons

    on_start_click(self)          # server.start() in try/except -> showerror if port busy; disable Start; call refresh()
    on_reset_click(self)          # askyesno -> server.reset_data()
    on_quit_click(self)           # root.destroy()
    refresh(self)                 # snapshot = server.get_snapshot(); update labels; append NEW log lines; root.after(REFRESH_MS, self.refresh)
    append_log(self, line)        # enable Text -> insert -> see("end") -> disable
    get_my_ip(self)               # simple helper to show the LAN IP (socket.gethostbyname(socket.gethostname()))
```

`get_snapshot()` returns a dict: `{"running": bool, "seats_left": {...}, "total": int, "log": [...]}`, all copies made inside the lock. The dashboard remembers how many log lines it already printed (`self.log_shown`) and only appends the new ones.

## 4. File-by-File Code Spec

### `config.py`
Only constants (see System Design §8 and the theme table above). No functions.

### `validation.py`
- `validate_fields(name, roll_number, email, course)`: returns `""` or message.
- (Optional helper) `clean_roll_number(roll_number)`: `.strip().upper()`.

### `storage.py` [Unit 4]
- `ensure_data_file()`: `os.makedirs(DATA_FOLDER, exist_ok=True)`; if file missing, create empty file.
- `append_registration(roll, name, email, course)`: builds line with `time.strftime("%Y-%m-%d %H:%M:%S")`, `with open(DATA_FILE, "a") as f: f.write(line + "\n")`. May raise `OSError`.
- `load_registrations()`: returns a list of lists, one per non-empty line (`line.strip().split(",")`); skips malformed lines (fewer than 5 fields).
- `clear_registrations()`: opens file with `"w"` to empty it.

### `server.py` [Unit 5: sockets + threads]
```
class RegistrationServer:
    __init__(self)                 # seats_left (copy of COURSES), roll_numbers=set(), activity_log=[], total=0, lock=Lock(), running=False, server_socket=None
    load_existing_data(self)       # uses storage.load_registrations()
    start(self)                    # ensure file, load data, create/bind/listen socket, start listener thread
    accept_loop(self)              # while True: conn, addr = accept(); Thread(target=self.handle_client, args=(conn, addr), daemon=True).start()
    handle_client(self, conn, addr)# recv -> json.loads -> process_request -> json.dumps -> sendall -> close. try/except/finally
    process_request(self, request) # dispatch on request["action"]
    get_courses(self)              # with lock: reply with seats_left copy
    register(self, request)        # lock or no lock depending on USE_LOCK
    check_and_save(self, request)  # the 6-step sequence from System Design §5
    add_log(self, text)            # timestamp + append (caller already holds the lock when needed)
    get_snapshot(self)             # with lock: copies
    reset_data(self)               # with lock: clear file, restore seats, clear set, log
```
Helper to build replies: `make_error(code, message)` returns `{"status":"ERROR","code":code,"message":message}`.

Careful: `add_log` is called from inside locked sections, so it must **not** acquire the lock itself (deadlock). Add a comment saying so.

### `client_net.py` [Unit 5: client socket]
```
def send_request(server_ip, request):
    # create socket, settimeout(TIMEOUT), connect((server_ip, PORT)),
    # sendall((json.dumps(request) + "\n").encode()),
    # data = sock.recv(BUFFER_SIZE).decode(), return json.loads(data)
    # except (OSError, ValueError): return {"status": "ERROR", "code": "NETWORK", "message": ...}
    # finally: close
```

### `test_race.py`
```
Settings at top: COURSE_TO_TEST, NUMBER_OF_CLIENTS = 10, SERVER_IP = "127.0.0.1"
def try_to_register(number, results):     # one thread: send REGISTER with roll "RACE" + 5-digit number; append status/code to results list
def main():                               # start all threads, join, count OK / FULL / DUPLICATE, ask server for seats left, print verdict
```
Prints e.g.: `Seats available: 3 | Accepted: 3 | Rejected(FULL): 7 -> PASS` or `Accepted: 6 -> OVERBOOKED (race condition!)`. Remind the user in the printed output to press **Reset Data** before the next run.

## 5. Accessibility / UX Details

- Pressing **Enter** in any entry does nothing special (keep simple); Tab order follows the form order.
- After a successful submit, clear name/roll/email automatically (course stays) so the next student can be entered fast.
- Status label colours: success green, errors red, normal ink.
- All text in English, short and direct.
