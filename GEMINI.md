# GEMINI.md: Project Rules for DCSRN

**Project:** Distributed Client-Server Registration Network (DCSRN)
**Course:** CSE3011 Python Programming, Module 5 (GUI, Networking, Multithreading)
**What it is:** Many Tkinter "admission desk" clients send student registrations over TCP sockets to one multi-threaded server. The server saves them to a file and shows a live Tkinter dashboard. A lock stops two desks from booking the same last seat.

---

## 0. Prime Directive

> **The student must be able to explain every single line of this code in a viva.**

Simple, boring, readable code always beats clever, short, or "professional" code. If you are choosing between two ways to write something, pick the one a second-year student would understand on first read.

## 1. Read These First (in this order)

1. `docs/01_PRD.md` (what we build)
2. `docs/02_SYSTEM_DESIGN.md` (how it works, protocol, locking)
3. `docs/03_DESIGN_DOCUMENT.md` (screens, files, functions)
4. `docs/04_IMPLEMENTATION_PLAN.md` (the phases you will follow)

If anything conflicts, the order above wins. If something is unclear or missing, **ask me. Do not guess.**

## 2. Allowed Tools (Syllabus Whitelist)

Python 3.8+ **standard library only. Never run `pip install`.**

| Allowed | Used for | Syllabus |
|---|---|---|
| `tkinter` (`tk.Tk`, `Frame`, `Label`, `Entry`, `Button`, `OptionMenu`, `Text`, `Scrollbar`, `StringVar`) | GUI | Unit 5 |
| `tkinter.messagebox` (`showinfo`, `showwarning`, `showerror`, `askyesno`) | Dialogs | Unit 5 |
| `socket` | TCP client/server | Unit 5 |
| `threading` (`Thread`, `Lock`) | Concurrency | Unit 5 |
| `json` | Serialize request/response | Unit 2 (standard modules) |
| `time` | Timestamp, demo delay | Unit 2 (standard modules) |
| `os`, `os.path` | Create folder, check file | Unit 4 |
| Plain `open()` with `with` | Read/append the data file | Unit 4 |
| `try / except` | Handle network and IO errors | Unit 2, 3, 4 |
| Classes, methods, `__init__`, `self` | Structure | Unit 3 |
| `list`, `dict`, `set`, `tuple` | Data | Unit 2 |
| `if/else`, `for`, `while`, functions, constants | Logic | Unit 1, 2 |

## 3. Forbidden (do not use, even if "better")

`pip` packages, `ttk`, `sqlite3`, `csv` module, `asyncio`, `queue`, `select`/`selectors`, `multiprocessing`, `concurrent.futures`, `ssl`, `re`, `logging`, `argparse`, `dataclasses`, `typing` / type hints, decorators, `lambda`, generators / `yield`, `async`/`await`, `match` statements, walrus `:=`, nested comprehensions, `global` keyword, inheritance (not needed here), web frameworks, ORMs.

Simple list comprehensions are tolerated only if a plain `for` loop would be silly. Prefer the plain loop.

## 4. Code Style Rules

- **One function does one thing, max ~20 lines.** One file max ~150 lines (`server.py` and `client_gui.py` may reach ~200).
- **Names are plain English:** `seats_left`, `roll_number`, `send_request`, not `s`, `rn`, `sr`.
- **Every function gets a one-line docstring** saying what it does in simple words.
- **Tag syllabus links in comments:** e.g. `# [Unit 5: Multithreading] one thread per client`. Put tags where the concept actually appears.
- **Comment the "why", in plain English,** above any block that is not obvious (locks, `after()`, `daemon=True`).
- **No magic numbers or strings.** Ports, colours, fonts, course list, file path all live in `config.py`.
- **Buttons use `command=self.method_name`.** Never `lambda`.
- **Max 3 classes in the whole project:** `RegistrationServer`, `ServerDashboard`, `ClientApp`.
- **Use `with open(...)`** for files and `with self.lock:` for the lock.
- **Return values over globals.** No `global` keyword. Shared server state lives on `self` inside `RegistrationServer`.
- Use f-strings for text. Keep lines under ~90 characters.

## 5. The Two Golden Technical Rules

### Rule A: Tkinter is touched by the main thread ONLY
Worker threads (network, client send thread) must **never** create, change, or read widgets, and must never open a dialog. Instead:
1. The worker thread puts its result in a plain variable (e.g. `self.result`).
2. The main thread polls it with `self.root.after(100, self.check_result)` and updates the GUI there.

### Rule B: All shared server data is changed inside the lock
`seats_left`, `roll_numbers`, `activity_log` and the data file are shared by many threads. Any code that checks-then-changes them runs inside `with self.lock:`. This is the race-condition fix and the main point of the project. Do not weaken it, split it, or remove it.
(Exception: the `USE_LOCK = False` demo flag in `config.py`, which exists on purpose to show the race.)

## 6. How to Work (Workflow Rules)

1. **One phase at a time** from `docs/04_IMPLEMENTATION_PLAN.md`. Never start the next phase on your own.
2. **Plan before code.** At the start of each phase, state in plain English what files you will create or change. Wait for my OK if the plan differs from the docs.
3. **Do only what the phase says.** No extra features, no refactors, no "improvements" outside the PRD.
4. **Run the phase's acceptance check** and show me the real output. Do not claim success without running it.
5. **After each phase, append to `docs/CODE_WALKTHROUGH.md`:** for each new function, 1–2 plain sentences on what it does and 1 sentence on which syllabus concept it shows. I will use this to prepare for the viva.
6. **End each phase with a short summary:** files changed, how to run it, and "How I would explain this" (3 bullets). Then **stop and wait** for "go ahead".
7. **Do not edit files in `docs/` or this file** unless I ask. If a doc looks wrong, tell me instead.
8. If you hit a bug, explain the cause in simple words before fixing.
9. Prefer small, reviewable changes. Suggest a git commit message at the end of each phase.

## 7. Project Layout (do not add files outside this)

```
dcsrn-project/
├── GEMINI.md
├── docs/                     (documentation, read-only for you except CODE_WALKTHROUGH.md)
├── data/
│   └── registrations.csv     (created automatically by the server)
├── config.py                 constants, courses, flags, colours
├── validation.py             shared field checks (client AND server use it)
├── storage.py                read/append the data file
├── server.py                 RegistrationServer: sockets, threads, lock, logic
├── server_gui.py             ServerDashboard (run this to start the server)
├── client_net.py             send_request(): one TCP request, one reply
├── client_gui.py             ClientApp (run this to start a desk)
└── test_race.py              many threads fight for the same seats
```

## 8. Run Commands

```
python server_gui.py        # starts dashboard + server (port from config.py)
python client_gui.py        # starts one admission desk (run several times)
python test_race.py         # concurrency demo / test (server must be running)
python -m tkinter           # quick check that Tkinter is installed
```

## 9. Definition of Done (whole project)

- All Must requirements in `docs/01_PRD.md` work.
- Every case in `docs/05_TEST_PLAN.md` passes.
- `test_race.py` shows **overbooking with `USE_LOCK=False`** and **exactly the seat count with `USE_LOCK=True`**.
- No forbidden module is imported anywhere (`grep` the imports to prove it).
- `docs/CODE_WALKTHROUGH.md` covers every function.

## 10. Never Do This

- Never `pip install` anything or add a dependency.
- Never block the Tkinter main thread with network or file waits. Use a background thread.
- Never trust the client. The server re-validates everything.
- Never swallow errors silently (`except: pass`). Catch specific errors and show/log a clear message.
- Never rewrite the whole project in one go. Phases only.
