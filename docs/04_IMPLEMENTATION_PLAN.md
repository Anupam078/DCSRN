# Step-by-Step Implementation Plan

Eleven small phases. **One phase at a time.** After each phase the agent must: run the acceptance check, append to `docs/CODE_WALKTHROUGH.md`, give a short summary + "How I would explain this", and **stop**. You review, run it yourself, commit, then say "go ahead".

Phase map:

| Phase | Builds | Main concept |
|---|---|---|
| 0 | Setup & environment check | Python, Tkinter |
| 1 | `config.py`, `validation.py` | Constants, functions, string methods |
| 2 | `storage.py` | Unit 4 file handling |
| 3 | `server.py` logic (no network yet) | Classes, dict/set, **lock** |
| 4 | `server.py` network layer | Sockets, daemon threads |
| 5 | `client_net.py` | Client socket, JSON, exceptions |
| 6 | `server_gui.py` | Tkinter dashboard, `after()` |
| 7 | `client_gui.py` layout | Nested frames, widgets |
| 8 | `client_gui.py` behaviour | Events, dialogs, background thread |
| 9 | `test_race.py` + race demo | Race condition proof |
| 10 | Multi-machine test, polish, docs | LAN run, final checks |

---

## Phase 0: Setup

**Goal:** a clean folder and a working Python + Tkinter.
**Tasks (you, not the agent):**
1. Create the folder `dcsrn-project`, copy in `GEMINI.md` and the `docs/` folder. Open the folder as the workspace in AntiGravity.
2. In a terminal run `python --version` (3.8+) and `python -m tkinter` (a small test window must open).
3. `git init`, first commit `"docs: add project documentation"`.
4. Fill in the open items in `docs/00_START_HERE.md` (course names, seat counts).

**First prompt to the agent:**
> Read GEMINI.md and every file in docs/. Do NOT write any code. Reply with: (1) the project in 5 sentences, (2) the list of phases, (3) any questions or contradictions you noticed. Then wait.

**Done when:** the agent summarises correctly and asks only sensible questions.

---

## Phase 1: Config and Validation

**Files:** `config.py`, `validation.py`
**Agent prompt:**
> Do Phase 1 only. Create config.py with every constant from docs/02_SYSTEM_DESIGN.md §8 and the theme table in docs/03_DESIGN_DOCUMENT.md §1. Create validation.py with validate_fields() using the rules in the Design Document and only plain string methods. Add a tiny `if __name__ == "__main__":` block in validation.py that tests 6 good/bad inputs and prints results. Follow GEMINI.md.

**Done when:** `python validation.py` prints correct results for: valid input, 1-char name, roll with a space, email without `@`, name with a comma, empty course.
**Explain it:** constants in one place; one function that checks fields; why client *and* server both call it.
**Commit:** `phase 1: config and validation`

---

## Phase 2: Storage (File Handling, Unit 4)

**File:** `storage.py`
**Agent prompt:**
> Do Phase 2 only. Create storage.py with ensure_data_file, append_registration, load_registrations, clear_registrations as specified in docs/03_DESIGN_DOCUMENT.md §4. Use plain open() with `with`. Add a small `__main__` test that appends 2 fake lines, loads them back and prints them, then clears the file.

**Done when:** running `python storage.py` creates `data/registrations.csv`, prints two parsed records, then the file is empty. Open the file in a text editor after the append step to see the format.
**Explain it:** write mode `"a"` vs `"w"` vs read `"r"`; `split(",")`; why `with` closes the file.
**Commit:** `phase 2: file storage`

---

## Phase 3: Server Logic (no network yet)

**File:** `server.py` (class `RegistrationServer`, without `start/accept_loop/handle_client` yet)
**Agent prompt:**
> Do Phase 3 only. In server.py create class RegistrationServer with __init__, load_existing_data, get_courses, register, check_and_save, add_log, get_snapshot, reset_data, make_error. Follow the 6-step sequence and locking rules in docs/02_SYSTEM_DESIGN.md §5. Use USE_LOCK and DEMO_DELAY from config. Do not write any socket code yet. Add a `__main__` test that registers students directly by calling register() with a dict, covering success, duplicate roll, full course, bad course, invalid field.

**Done when:** the test prints the correct code for each case; the file has lines only for successes; a second run (server restarted) shows seat counts reduced because `load_existing_data` read the file.
**Explain it:** check-then-act; why the file write comes before the seat decrement; why `add_log` does not take the lock.
**Commit:** `phase 3: server registration logic with lock`

---

## Phase 4: Server Network Layer (Sockets + Threads)

**File:** `server.py` (add methods)
**Agent prompt:**
> Do Phase 4 only. Add start(), accept_loop(), handle_client(), process_request() to RegistrationServer. start() prepares the file, loads data, creates a TCP socket with SO_REUSEADDR, binds to (HOST, PORT), listens, and starts accept_loop in a daemon thread. accept_loop starts one daemon Thread per client running handle_client. handle_client reads one JSON line, calls process_request, sends the JSON reply, and always closes the connection (try/except/finally). Comment every threading line with a [Unit 5] tag. Add a `__main__` that starts the server and keeps the main thread alive with a simple `while True: time.sleep(1)` loop, and prints each log line as it appears.

**Done when:** with the server running, a quick manual test works. For example in another terminal run a 3-line Python snippet (the agent writes it into the answer, not into the project) that connects and sends `{"action":"GET_COURSES"}`, and gets the seat dict back. Sending garbage returns `BAD_REQUEST` and the server stays alive.
**Explain it:** `socket()`, `bind`, `listen`, `accept`; why a new thread per client; what `daemon=True` means.
**Commit:** `phase 4: server sockets and threads`

---

## Phase 5: Client Network Helper

**File:** `client_net.py`
**Agent prompt:**
> Do Phase 5 only. Create client_net.py with send_request(server_ip, request) exactly as specified in docs/03_DESIGN_DOCUMENT.md §4. It must never raise; on failure it returns the NETWORK error dict. Add a `__main__` test that fetches courses, registers one student, tries the same roll again, and tries a wrong IP/closed server.

**Done when:** against the running server you see OK, then DUPLICATE; with the server stopped you see a NETWORK error dict in under ~5 s (not a crash).
**Explain it:** client side `connect`, `sendall`, `recv`; JSON `dumps`/`loads`; timeout; why return an error dict instead of raising.
**Commit:** `phase 5: client network helper`

---

## Phase 6: Server Dashboard (Tkinter)

**File:** `server_gui.py`
**Agent prompt:**
> Do Phase 6 only. Create server_gui.py with class ServerDashboard following the widget tree and class spec in docs/03_DESIGN_DOCUMENT.md §3 and the theme in §1. Use pack/grid, nested frames, labels, a Text widget with a Scrollbar, and three buttons. refresh() must use root.after(REFRESH_MS, self.refresh) and read data only via server.get_snapshot(). Reset Data must use messagebox.askyesno. Do not touch any widget from a non-main thread.

**Done when:** `python server_gui.py` opens the dashboard; **Start Server** starts listening (status turns "Running"); using `client_net.py`'s test from Phase 5 makes counts and the log update within about a second; **Reset Data** asks for confirmation and clears everything; a second server on the same port shows an error dialog, not a crash.
**Explain it:** event-driven programming (button → handler), `mainloop`, `after()` polling, why threads don't touch widgets.
**Commit:** `phase 6: server dashboard`

---

## Phase 7: Client Window Layout

**File:** `client_gui.py` (layout only, buttons print to console)
**Agent prompt:**
> Do Phase 7 only. Create client_gui.py with class ClientApp that builds the window exactly as in docs/03_DESIGN_DOCUMENT.md §2: nested frames, labels, entry fields with StringVar, OptionMenu for the course (values from config.COURSES), three buttons, status label, seats label. Button handlers for now only update the status label with the button name. No networking yet.

**Done when:** the window matches the wireframe and theme; typing works; Clear really empties the three fields; changing the course changes the dropdown; resizing is disabled.
**Explain it:** frames inside frames, `pack` vs `grid`, `StringVar`, `command=self.method`.
**Commit:** `phase 7: client layout`

---

## Phase 8: Client Behaviour (Events, Dialogs, Background Thread)

**File:** `client_gui.py` (complete it)
**Agent prompt:**
> Do Phase 8 only. Finish client_gui.py per docs/03_DESIGN_DOCUMENT.md §2: on_submit_click validates with validation.validate_fields and shows messagebox.showwarning on error; otherwise it disables Submit and calls run_in_background. run_in_background starts a daemon Thread running worker(), which stores the reply in self.result by calling client_net.send_request. check_result polls with root.after(100, ...) on the main thread and then shows the correct dialog from the dialog table. Add Refresh Seats and automatic seat refresh on startup and course change. Golden Rule A in GEMINI.md: no widget access inside worker().

**Done when:** with the server running, a full registration works and the dashboard shows it; Submit on a full course shows the "Course full" dialog; duplicate roll shows "Already registered"; with the server stopped you get "Cannot reach server" and the window does not freeze; while waiting (add a temporary `DEMO_DELAY=1` on the server) you can still drag and click in the client window.
**Explain it:** why a background thread; why `self.result` + `after()` instead of calling dialogs from the thread; the full life of one click.
**Commit:** `phase 8: client behaviour`

---

## Phase 9: Race Condition Test and Demo

**File:** `test_race.py`
**Agent prompt:**
> Do Phase 9 only. Create test_race.py as specified in docs/03_DESIGN_DOCUMENT.md §4. Then give me exact step-by-step instructions for running the two demos: (A) USE_LOCK=False with DEMO_DELAY=0.2, (B) USE_LOCK=True. Do not change any other file.

**Done when:**
- **Demo A (lock off):** after Reset Data, `python test_race.py` shows *more* accepted than seats, and the file contains extra lines (overbooked), with the dashboard "Left" going negative or showing wrong.
- **Demo B (lock on):** after Reset Data, exactly the seat count is accepted, the rest are FULL.
Remember to set `USE_LOCK=True`, `DEMO_DELAY=0.0` again afterwards and restart the server (config is read at start).
**Explain it:** the timeline table in System Design §5; this is the headline demo.
**Commit:** `phase 9: race condition test`

---

## Phase 10: Multi-Machine Test, Polish, Final Checks

**Tasks:**
1. **LAN test:** server on laptop 1, clients on laptop 2 (and 3). Use the server's LAN IP. Fix firewall/port issues.
2. **Run the whole `docs/05_TEST_PLAN.md`** and tick every case.
3. **Import audit.** Ask the agent:
   > Do Phase 10. List every import in every .py file and confirm each is on the allowed list in GEMINI.md. Report any function longer than 25 lines or any use of lambda/global/type hints. Fix only what you report. Then check docs/CODE_WALKTHROUGH.md covers every function.
4. **Viva rehearsal:** read `docs/06_VIVA_AND_DEMO_GUIDE.md`, and for each file practise explaining it aloud using `CODE_WALKTHROUGH.md`.
5. Add a short `README.md` (how to run). Tag the final commit.

**Done when:** all items in the test plan pass, the import audit is clean, and both teammates can explain each file without notes.

---

## Working Agreement (every phase)

1. You paste the phase prompt. The agent states its plan; you approve.
2. The agent codes, runs the check, shows real output.
3. **You run it yourself** and read the code. If you cannot explain a line, ask the agent: *"Explain lines X-Y as if I'm a first-year student and simplify them if possible."*
4. Update `CODE_WALKTHROUGH.md`, commit, then continue.

## If the agent goes off-track

- Too fancy → *"This violates GEMINI.md section 3/4. Rewrite it using only allowed features, in a simpler way."*
- Does extra work → *"Revert everything outside Phase N and stop."*
- Claims it works without proof → *"Run the acceptance check and paste the real output."*
