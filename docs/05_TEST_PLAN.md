# Test Plan

Run these after Phase 8 (T1-T22) and Phase 9 (T23-T26). Tick each box. Assume demo config: `COURSES = {"CSE3011 Python Programming": 5, "CSE2001 Data Structures": 3, "CSE2005 Database Systems": 4}`. Use **Reset Data** between groups.

## A. Validation (client side, no server needed)

| ID | Steps | Expected | ✔ |
|---|---|---|---|
| T1 | Submit with all fields empty | Warning "Check your input", nothing sent | ☐ |
| T2 | Name = `A` | Warning about name length | ☐ |
| T3 | Name = `Asmi, Chakne` (comma) | Warning about commas | ☐ |
| T4 | Roll = `24 BCE` (space) | Warning about roll number | ☐ |
| T5 | Email = `asmi.example.com` (no @) | Warning about email | ☐ |
| T6 | Valid data, press **Clear** | All three fields empty, status "Ready" | ☐ |

## B. Single-client registration

| ID | Steps | Expected | ✔ |
|---|---|---|---|
| T7 | Valid student, Python course | "Registration successful" dialog; seats label drops by 1; name/roll/email cleared | ☐ |
| T8 | Dashboard after T7 | Total = 1, course shows 1 / 5, log line appears within ~1 s | ☐ |
| T9 | `data/registrations.csv` | Exactly one line with 5 comma-separated fields | ☐ |
| T10 | Register the same roll number again | "Already registered" warning; file unchanged | ☐ |
| T11 | Fill Data Structures (3 seats) with 3 students, then a 4th | 4th gets "Course full"; file has 3 lines for that course | ☐ |
| T12 | Roll `24bce10354` (lowercase) then `24BCE10354` | Second is DUPLICATE (roll numbers are upper-cased) | ☐ |

## C. Server and client robustness

| ID | Steps | Expected | ✔ |
|---|---|---|---|
| T13 | Start client with server not running; press Submit | "Cannot reach server" dialog within ~5 s; no crash | ☐ |
| T14 | Wrong IP typed in Server IP | Same friendly error | ☐ |
| T15 | Stop the server (close dashboard) while a client is open, then Submit | Friendly error; client still usable | ☐ |
| T16 | Send garbage text to the port (small script) | Server replies BAD_REQUEST, keeps running | ☐ |
| T17 | Start second server on same port | Error dialog, no crash | ☐ |
| T18 | Register 2 students, close and restart the server | Dashboard shows same totals and seat counts (data reloaded) | ☐ |
| T19 | Add a temporary `DEMO_DELAY = 1` on the server, press Submit on client, then drag/click the client window | Window stays responsive while waiting | ☐ |

## D. Multiple clients

| ID | Steps | Expected | ✔ |
|---|---|---|---|
| T20 | Open 3 client windows; submit different students from each | All appear on the dashboard; no errors | ☐ |
| T21 | Two clients race for the last seat (click Submit at nearly the same moment) | Exactly one success, the other "Course full" | ☐ |
| T22 | Two machines on the LAN (server + client on separate laptops) | Registration works with the server's LAN IP | ☐ |

## E. Race-condition proof (the headline test)

| ID | Config | Steps | Expected | ✔ |
|---|---|---|---|---|
| T23 | `USE_LOCK=False`, `DEMO_DELAY=0.2`, restart server | Reset Data, run `python test_race.py` (10 clients, 3-seat course) | **Accepted > 3** → "OVERBOOKED". File has more than 3 lines for the course | ☐ |
| T24 | `USE_LOCK=True`, `DEMO_DELAY=0.2`, restart server | Reset Data, run `python test_race.py` | **Accepted = 3**, 7 rejected FULL → PASS | ☐ |
| T25 | `USE_LOCK=True`, `DEMO_DELAY=0.0` | Same test | Accepted = 3 (normal speed also correct) | ☐ |
| T26 | Same-roll variant (optional): 5 threads send the *same* roll number | Exactly 1 OK, 4 DUPLICATE with lock on | ☐ |

## F. Code-quality checks

| ID | Check | Expected | ✔ |
|---|---|---|---|
| T27 | List all `import` lines in all `.py` files | Only `tkinter`, `tkinter.messagebox`, `socket`, `threading`, `json`, `time`, `os` and project files | ☐ |
| T28 | Search for `lambda`, `global`, `ttk`, `->`, `pip` | None found | ☐ |
| T29 | Every function has a docstring and syllabus tag where relevant | Yes | ☐ |
| T30 | `CODE_WALKTHROUGH.md` covers every function | Yes | ☐ |
| T31 | Each teammate explains 3 random functions without notes | Pass | ☐ |

## Defect log

| # | Test ID | What happened | Fixed? |
|---|---|---|---|
| | | | |
