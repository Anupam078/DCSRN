# START HERE: DCSRN Agentic Coding Pack

## What is in this pack

| File | Purpose |
|---|---|
| `GEMINI.md` (project root) | Rules the AntiGravity agent must follow: syllabus-only code, simplicity, thread rules, workflow |
| `docs/01_PRD.md` | What we are building and why (requirements, scope, acceptance) |
| `docs/02_SYSTEM_DESIGN.md` | Architecture, threads, protocol, race-condition design |
| `docs/03_DESIGN_DOCUMENT.md` | Screens, widget trees, file-by-file function specs, dialog texts |
| `docs/04_IMPLEMENTATION_PLAN.md` | 11 phases with copy-paste agent prompts and checks |
| `docs/05_TEST_PLAN.md` | Every test case to pass before submission |
| `docs/06_VIVA_AND_DEMO_GUIDE.md` | Pitch, demo script, likely viva questions and answers |
| `docs/CODE_WALKTHROUGH.md` | *Created by the agent as it works*: plain-English explanation of every function |

## Folder layout to create

```
dcsrn-project/
├── GEMINI.md
├── docs/            (all the .md files above)
└── (the agent creates the .py files phase by phase)
```

## Decisions already locked

| Topic | Decision |
|---|---|
| Server storage | Plain text/CSV file `data/registrations.csv` (Unit 4 file handling) |
| Seat model | Multiple courses, each with a fixed seat limit (set in `config.py`) |
| Server UI | Small Tkinter dashboard: live registrations, seats left, activity log |
| Protocol | TCP, one JSON line per request, one reply per connection, port 5050 |
| Concurrency | Thread per client (daemon) + one `threading.Lock` around check-and-save |
| Allowed modules | `tkinter`, `tkinter.messagebox`, `socket`, `threading`, `json`, `time`, `os` |

## Fill these in before Phase 1

- [ ] Final course names and seat counts for `config.py` (keep seats small, e.g. 3-5, so the demo hits "full" quickly)
- [ ] Which laptop will be the server on demo day
- [ ] Python version on every machine (3.8+) and `python -m tkinter` works on each
- [ ] Both teammates have a copy of the repo (Git or shared drive)

## How to start in AntiGravity

1. Open the `dcsrn-project` folder as your workspace so the agent sees `GEMINI.md` at the root.
2. Send the **Phase 0 first prompt** from `04_IMPLEMENTATION_PLAN.md` (read everything, write no code, summarise and ask questions).
3. If your AntiGravity build offers a planning-style mode, use it: you want the agent to show its plan before editing files. If not, the "state your plan first" rule in `GEMINI.md` does the same job.
4. Then run Phases 1 to 10 one at a time using the prompts in the plan.
5. After every phase: run the code yourself, read the diff, commit.

## Tips so you can actually explain the code

- Read each file the agent writes **before** moving on. Ask: *"Explain lines X to Y like I'm a first-year student."*
- Keep `CODE_WALKTHROUGH.md` growing. It becomes your viva notes.
- If code feels clever, ask the agent to simplify it. Simpler always wins.
- Split the explaining: e.g. one teammate owns client + Tkinter, the other owns server + threads/lock, but **both** must understand the race-condition demo.

## Honest notes for your presentation

- Say "prototype that demonstrates concurrency control", not "production-ready". Real production would add encryption, login and a database.
- Traffic is not encrypted. If asked, answer: *validated input, server re-validates; TLS and authentication are future work.*
- The proposal's "daemon thread per client" and "no UI freezing" are both implemented exactly as described.

## Quick glossary

| Term | Meaning |
|---|---|
| Socket | An endpoint for sending/receiving data over the network |
| TCP | Reliable, ordered connection protocol |
| Thread | A separate flow of execution inside one program |
| Daemon thread | Background thread that ends automatically when the program exits |
| Race condition | Wrong result because threads interleave unsafely |
| Lock | A "one at a time" gate (`threading.Lock`) |
| Event-driven | Code runs in response to events such as button clicks |
| `after()` | Tkinter method that schedules a function to run later on the main thread |
