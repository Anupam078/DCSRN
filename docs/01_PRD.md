# Product Requirements Document (PRD)

**Product:** Distributed Client-Server Registration Network (DCSRN)
**Course / Module:** CSE3011 Python Programming, Module 5
**Version:** 1.0  |  **Date:** October 2026
**Team:** Asmi Chakne (24BCE10354), Niharika Tanwi (25BOE10105)

---

## 1. Overview

DCSRN is a Python application that lets several admission desks register students **at the same time** into one central server. Each desk runs a Tkinter client. One server accepts many clients at once using threads, stores every registration in a file, and shows a live dashboard of registrations and seats left. A lock guarantees that a course is never overbooked, even when desks click Submit in the same instant.

## 2. Problem Statement

During peak admissions, many desks register students at once. Standalone desktop apps fail because of:

1. **Data fragmentation:** records are stuck on separate machines and must be merged by hand.
2. **Race conditions:** two desks can take the last seat of a course at the same moment, causing double-booking.
3. **System latency:** a single-threaded app freezes the screen during disk or network work.

## 3. Goals

| # | Goal |
|---|---|
| G1 | One central server is the single source of truth for all registrations. |
| G2 | Seats are never overbooked and a roll number is never registered twice, even under concurrent requests. |
| G3 | Client screens never freeze while talking to the server. |
| G4 | Code is simple and uses only Module 5 syllabus concepts, so the team can explain it. |
| G5 | The race-condition fix can be **demonstrated live** (lock off vs lock on). |

## 4. Non-Goals (Out of Scope)

User login/passwords, encryption (TLS), databases, a web/HTML interface, editing or deleting a registration from a client, payments, email sending, internet deployment, more than ~20 simultaneous desks.

## 5. Users

| User | Description | Needs |
|---|---|---|
| **Desk Staff** | Admission staff at a client machine | Fast form entry, clear success/failure feedback, no freezing |
| **Admission Coordinator** | Runs the server machine | Live view of registrations and seats left per course |
| **Evaluator / Examiner** | Judges the project | Clear demo of GUI, sockets, threads, race-condition fix |

## 6. User Stories

- As desk staff, I enter a student's details, pick a course and press **Submit**, and I immediately see whether the registration succeeded.
- As desk staff, I see how many seats are left in the selected course before I submit.
- As desk staff, if the course is full or the roll number already exists, I get a clear message instead of a crash.
- As desk staff, the window keeps responding while the request is being sent.
- As a coordinator, I watch the dashboard update live as desks register students.
- As a coordinator, I can reset all data between demos.
- As an examiner, I can run a test that fires many simultaneous requests and see that no seat is double-booked.

## 7. Functional Requirements

Priority: **M** = Must, **S** = Should.

### Client (`client_gui.py`)

| ID | Requirement | Pri | Syllabus |
|---|---|---|---|
| FR-C1 | Window with fields: Server IP, Student Name, Roll Number, Email, and a Course dropdown. | M | Unit 5 GUI |
| FR-C2 | Layout uses **nested frames** (header, server, form, button, status). | M | Unit 5 layouts |
| FR-C3 | **Submit** button validates input locally; on error shows a warning dialog and sends nothing. | M | Unit 5 events/dialogs |
| FR-C4 | On valid input, Submit sends a REGISTER request over TCP **in a background thread**; the GUI stays responsive. | M | Unit 5 threading |
| FR-C5 | The result (success, course full, duplicate roll, invalid, network error) is shown in a dialog and in a status label. | M | Unit 5 dialogs |
| FR-C6 | **Clear** button empties all form fields and resets the status. | M | Unit 5 events |
| FR-C7 | **Refresh Seats** button (and automatic refresh on startup and when the course changes) shows "Seats left: N" for the selected course. | M | Unit 5 |
| FR-C8 | If the server is unreachable or times out, show an error dialog; the app does not crash. | M | Unit 4 IO exceptions |
| FR-C9 | Submit button is disabled while a request is in flight (prevents double-clicks). | S | Unit 5 |

### Server (`server.py`, `server_gui.py`)

| ID | Requirement | Pri | Syllabus |
|---|---|---|---|
| FR-S1 | Server listens on a TCP port (default 5050) on all interfaces. | M | Unit 5 sockets |
| FR-S2 | Every accepted connection is handled in its **own daemon thread**. | M | Unit 5 threading |
| FR-S3 | Supports two requests: `GET_COURSES` and `REGISTER` (see System Design). | M | Unit 5 |
| FR-S4 | Server **re-validates** every field, never trusting the client. | M | Unit 2 |
| FR-S5 | **Seat allocation is atomic:** check duplicate, check seats, save, decrement, all inside one lock. No overbooking, no duplicate roll numbers. | M | Unit 5 threading |
| FR-S6 | Each successful registration is appended to `data/registrations.csv`. On startup the server reloads the file to rebuild seat counts and roll-number set. | M | Unit 4 file handling |
| FR-S7 | Dashboard shows: server status, address:port, total registrations, per-course (total / taken / left), and a live scrolling activity log. | M | Unit 5 GUI |
| FR-S8 | Dashboard refreshes automatically (every ~500 ms) using `after()`; worker threads never touch widgets. | M | Unit 5 event-driven |
| FR-S9 | **Reset Data** button (with a Yes/No confirmation dialog) clears the file and restores all seats. | S | Unit 4 / Unit 5 |
| FR-S10 | A bad or incomplete request never crashes the server; it returns an ERROR reply. | M | Unit 2/3 exceptions |

### Demo / Test support

| ID | Requirement | Pri |
|---|---|---|
| FR-T1 | `config.py` has `USE_LOCK` (True/False) and `DEMO_DELAY` (seconds) flags, so the race condition can be switched on for demonstration. | M |
| FR-T2 | `test_race.py` launches many threads, each trying to register a different student into the same course, then prints how many succeeded vs were rejected and whether seats were overbooked. | M |

## 8. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-1 **Simplicity** | Only syllabus concepts; functions ≤ ~20 lines; code understandable by the team (see `GEMINI.md`). |
| NFR-2 **Responsiveness** | Client GUI never blocks on network; UI actions respond within ~100 ms. |
| NFR-3 **Correctness** | With 10+ simultaneous requests for N remaining seats, exactly N succeed. |
| NFR-4 **Robustness** | Server survives malformed JSON, dropped connections and client crashes. |
| NFR-5 **Portability** | Runs on Windows, macOS, Linux with Python 3.8+ and no extra packages. |
| NFR-6 **Capacity** | Comfortable with ~20 simultaneous desks (thread-per-connection). |

## 9. Data Requirements

A registration contains: roll number, name, email, course, timestamp. Stored one per line, comma-separated, in `data/registrations.csv`. Details in `02_SYSTEM_DESIGN.md`.

## 10. Constraints & Assumptions

- Python standard library only, restricted to the syllabus whitelist in `GEMINI.md`.
- All machines are on the same LAN or the same laptop (`127.0.0.1`) for demos.
- Course names and seat limits are defined in `config.py` and the same `config.py` is copied to every machine.
- Port 5050 is free and not blocked by a firewall.
- Input fields may not contain commas (keeps the file format trivial).

## 11. Success Metrics / Acceptance Criteria

1. Three client windows can register different students at the same time and all appear on the dashboard.
2. Registering into a full course shows "course full" and does **not** add a line to the file.
3. Registering the same roll number twice is rejected.
4. `test_race.py` with `USE_LOCK=True`: accepted count equals seats available, and the file has no extra lines.
5. `test_race.py` with `USE_LOCK=False` and `DEMO_DELAY>0`: overbooking is visible (accepted > seats).
6. Killing the server while a client is open leads to a friendly error dialog, not a crash.
7. Restarting the server keeps previous registrations and correct seat counts.

## 12. Risks

| Risk | Mitigation |
|---|---|
| Tkinter widget updated from a thread causes random crashes | Golden Rule A: threads write to a variable, main thread polls with `after()` |
| Firewall blocks port on another laptop | Test on LAN early (Phase 9); allow Python through firewall or change port |
| Agent writes code that is too fancy to explain | `GEMINI.md` forbids advanced features; `CODE_WALKTHROUGH.md` checks understanding |
| Race condition does not appear in the unlocked demo | `DEMO_DELAY` widens the race window artificially |
| Messages split across TCP packets | Messages are tiny (< 1 KB) and field lengths are capped; one request per connection |

## 12.1 Honest Limitations (be ready to state these)

- Traffic is **not encrypted** (plain TCP, no login). The proposal says "securely"; in this build that means *validated and structured*, and TLS/authentication are listed as future work.
- Thread-per-connection is right for a classroom/office scale, not for thousands of desks.
- The data file is simple text, not a database.

## 13. Future Work (do not build now)

TLS and login, MySQL storage (Unit 4), web dashboard (HTML/CGI, Unit 5), edit/cancel registration, admin export.
