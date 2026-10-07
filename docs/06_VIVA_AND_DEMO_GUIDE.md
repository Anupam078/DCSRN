# Viva and Demo Guide

## 1. The 60-Second Pitch

> "During admission rush, many desks register students at the same time. Standalone apps create scattered data, double-book seats, and freeze the screen. Our DCSRN has Tkinter clients that send registrations over TCP sockets to one multi-threaded server. The server handles each desk in its own thread, and a lock makes the seat check-and-save atomic, so a course is never overbooked. The server saves everything to a file and shows a live dashboard. We can prove the lock works by turning it off and showing overbooking."

## 2. Syllabus Mapping (say this when asked "where is the syllabus?")

| Syllabus topic (Unit 5 unless noted) | Where in our project |
|---|---|
| GUI, event-driven paradigm | Both windows: button click → handler; `mainloop()` |
| `tkinter` module, buttons, labels, entry fields | `client_gui.py`, `server_gui.py` |
| Dialogs | `messagebox.showinfo / showwarning / showerror / askyesno` |
| Widget attributes: sizes, fonts, colours, layouts | `config.py` theme, `pack`/`grid` |
| Nested frames | header/server/form/button/status frames |
| Multithreading | Thread per client on server, worker thread on client, `Lock` |
| Networks, client/server programming | `socket` in `server.py` and `client_net.py` |
| Unit 4: file handling, IO exceptions, directories | `storage.py` (`open`, `"a"`, `os.makedirs`), `try/except OSError` |
| Unit 2: collections, standard modules, exceptions | `dict` (seats), `set` (roll numbers), `list` (log), `json`, `time` |
| Unit 3: classes, methods, exception handling | `RegistrationServer`, `ServerDashboard`, `ClientApp` |

## 3. File-by-File Cheat Sheet

| File | One-sentence purpose | Key thing to say |
|---|---|---|
| `config.py` | All constants in one place | Change port, seats, colours without touching logic |
| `validation.py` | Checks name/roll/email/course | Used by both client and server; server never trusts client |
| `storage.py` | Reads and appends the data file | `"a"` appends, `split(",")` parses |
| `server.py` | The brain: sockets, threads, lock, rules | `accept()` loop → thread per client → `with self.lock` |
| `server_gui.py` | Live dashboard | Uses `after()` to refresh; threads never touch widgets |
| `client_net.py` | Sends one request, gets one reply | JSON over TCP, timeout, returns error dict instead of crashing |
| `client_gui.py` | The admission-desk window | Click → validate → background thread → poll result → dialog |
| `test_race.py` | Proves concurrency safety | 10 threads fight for 3 seats |

## 4. Demo Script (about 6 minutes)

**Setup before you start:** server on laptop A (`USE_LOCK=True`, `DEMO_DELAY=0.0`), 2-3 client windows ready, data reset, courses with small seat counts.

1. **Show the dashboard** (30 s): "This is the central server. It is listening on port 5050."
2. **Register from two clients** (60 s): submit different students from desk 1 and desk 2; point at the dashboard updating live; open `registrations.csv` and show the lines. *Single source of truth.*
3. **Validation and duplicate** (45 s): submit a bad email (warning dialog), then a repeated roll (rejected).
4. **Fill a course** (45 s): register until "Course full" appears. Dashboard shows Left = 0 in red.
5. **No freezing** (30 s): with `DEMO_DELAY=1` temporarily set on the server (restart it first), press Submit on a client and drag the client window while the request is pending. It stays responsive because the request runs in a worker thread. Set the delay back to `0.0` afterwards.
6. **Stop the server** (30 s): submit again → friendly "Cannot reach server" dialog. Restart server → data reloaded.
7. **The race condition** (2 min), the headline:
   - Set `USE_LOCK=False`, `DEMO_DELAY=0.2`, restart server, **Reset Data**, run `python test_race.py` → **overbooked** (e.g. 6 accepted for 3 seats). Explain the timeline table (check-then-act).
   - Set `USE_LOCK=True`, restart, **Reset Data**, run again → **exactly 3 accepted**, 7 rejected. "The lock lets one thread at a time through the check-and-save."
8. **Close:** "Centralised data, no double-booking, responsive UI, all with Module 5 concepts."

Backup plan: if the network fails, run everything on one laptop with `127.0.0.1`.

## 5. Likely Questions and Short Answers

**Q1. What is a socket?**
An endpoint for two programs to exchange data over a network. The server `bind`s to a port and `listen`s; the client `connect`s.

**Q2. Why TCP, not UDP?**
TCP is reliable and ordered. A registration must not be lost or arrive scrambled.

**Q3. Why a thread per client?**
So one slow client does not block the others. `accept()` returns a new connection and we hand it to its own thread.

**Q4. What does `daemon=True` do?**
The thread is a background thread: when the main program ends, it is stopped automatically and does not keep the program alive.

**Q5. What is a race condition? Show it.**
When the result depends on the timing of threads. Two threads both read "1 seat left", both book, and seats become −1. Our `test_race.py` with `USE_LOCK=False` shows this live.

**Q6. How does the lock fix it?**
`with self.lock:` lets only one thread run the check-and-save at a time. The next thread waits and then sees the updated seat count.

**Q7. Why is the file write inside the lock?**
So the file, the seat count and the roll-number set always change together. No thread can see a half-finished update.

**Q8. Why does `DEMO_DELAY` exist? Is that cheating?**
It widens the gap between check and act so the race shows reliably in a short demo. The bug is real without it, just rarer. The fix is the same.

**Q9. Why can't a thread update the Tkinter window directly?**
Tkinter is not thread-safe. Only the main thread should touch widgets. Our worker thread saves the reply in a variable and the main thread picks it up using `after()`.

**Q10. What does `after()` do?**
Schedules a function to run on the main thread after N milliseconds without freezing the GUI. We use it to poll for results and to refresh the dashboard.

**Q11. What does "event-driven" mean here?**
The program waits in `mainloop()` and runs our handler functions when events happen, such as a button click.

**Q12. How do you stop the GUI from freezing?**
Network calls happen in a worker thread, so the main thread keeps handling window events.

**Q13. Why JSON?**
Human-readable and two simple calls: `json.dumps` to send, `json.loads` to receive.

**Q14. Why a file and not a database?**
Our syllabus focus is sockets, threads, GUI, and file handling. A file keeps setup trivial and the code explainable. A database (MySQL, Unit 4) is a natural upgrade.

**Q15. What if the server crashes during a write?**
We write the file first and update memory second, and the server reloads the file at startup, so state is rebuilt from the file. Worst case, one partial last line is skipped as malformed.

**Q16. Is it secure?**
Input is validated on both sides and the server never trusts the client. It is not encrypted and has no login; TLS and authentication would be future work.

**Q17. How many clients can it handle?**
Comfortable at classroom or office scale (tens of desks). Thread-per-connection would need replacing for thousands.

**Q18. What if two desks register the same roll number at once?**
The duplicate check is inside the same lock, so exactly one succeeds and the other gets DUPLICATE.

**Q19. How did you avoid advanced features?**
We kept to the syllabus: classes, dict/set/list, `socket`, `threading`, `json`, `open()`, plain Tkinter widgets, `try/except`.

**Q20. What would you add next?**
TLS and login, MySQL storage, an HTML/CGI web dashboard, edit and cancel registration.

## 6. Roles for Presenting (suggested)

| Teammate | Explains | Also be ready for |
|---|---|---|
| Asmi | Problem, GUI (`client_gui.py`, `server_gui.py`), events, dialogs | Race demo explanation |
| Niharika | Server, sockets, threads, lock, storage, `test_race.py` | GUI basics |

Both must be able to run the full demo alone.
