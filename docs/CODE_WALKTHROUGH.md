# Code Walkthrough

## Phase 1: Config and Validation

### `config.py`
This file contains no logic or functions, only constant variables used throughout the project (such as the server `PORT`, `COURSES` dictionary, and Tkinter colours). Putting them in one place makes it easy to change settings without digging through logic code.

### `validation.py`
* **`validate_fields(name, roll_number, email, course)`**: Validates user inputs using basic string methods like `strip()`, `isalnum()`, and `find()`. It returns an empty string if all inputs are good, or a specific error message if any field breaks its rules. Both the client and server use this function to ensure invalid data is never sent or saved. [Unit 2: string methods]

## Phase 2: Storage (File Handling)

### `storage.py`
* **`ensure_data_file()`**: Uses `os.makedirs` to safely create the `data/` folder if it doesn't exist, and creates an empty `registrations.csv` file using write mode (`"w"`) if missing. [Unit 4: directories, file handling]
* **`append_registration(roll, name, email, course)`**: Gets the current time as a string, builds a comma-separated line, and saves it using append mode (`"a"`). Append mode guarantees we add to the bottom without deleting old records. [Unit 4: file handling]
* **`load_registrations()`**: Opens the file in read mode (`"r"`), loops through each line, and uses `split(",")` to turn it into a list. It skips any malformed lines that have fewer than 5 parts. [Unit 4: file handling]
* **`clear_registrations()`**: Instantly empties the entire file by opening it in write mode (`"w"`) and immediately closing it.

## Phase 3: Server Logic (No Network)

### `server.py`
* **`RegistrationServer.__init__()`**: Sets up the server's memory, including a dictionary for seats left, a set for duplicate-checking roll numbers, and a single `threading.Lock()` to protect them all.
* **`load_existing_data()`**: Called at startup. It reads the CSV file using `storage.py` and rebuilds the seat counts and roll number set so no data is lost between restarts.
* **`check_and_save(request)`**: The core business logic. It strictly follows a 6-step sequence: validate inputs, check course exists, check duplicate roll, check seats > 0, save to file, and finally update memory. [Unit 2: dict/set logic]
* **`register(request)`**: A wrapper around `check_and_save`. If `USE_LOCK` is True, it runs the entire 6-step sequence inside a `with self.lock:` block. This guarantees that two threads cannot interleave and overbook a seat. [Unit 5: threading lock]
* **`get_snapshot()` & `reset_data()` & `get_courses()`**: Also use `with self.lock:` to ensure the dashboard never reads partially-updated data and reset operations don't clash with incoming requests.

## Phase 4: Server Network Layer (Sockets + Threads)

### `server.py` (Network Layer)
* **`start()`**: Sets up the TCP server. It calls `socket()` to create the socket, `bind()` to attach it to our host and port, and `listen()` to wait for clients. Finally, it launches the `accept_loop` in a background daemon thread so the main thread isn't blocked. [Unit 5: sockets, multithreading]
* **`accept_loop()`**: An infinite loop that calls `accept()` to receive incoming client connections. For each new connection, it spawns a fresh daemon thread running `handle_client`. This way, a slow client doesn't freeze the server for others. [Unit 5: sockets, multithreading]
* **`handle_client(conn, addr)`**: Runs in its own thread. It reads the incoming JSON payload via `conn.recv()`, handles it using `process_request()`, sends back the JSON reply via `conn.sendall()`, and ensures the connection is safely closed in a `finally` block. [Unit 5: sockets]

## Phase 5: Client Network Helper

### `client_net.py`
* **`send_request(server_ip, request)`**: A utility function that opens a TCP socket, connects to the given IP, sends a JSON string, and waits for a reply. It wraps everything in a `try/except` block to ensure that if the server is offline or the connection drops, it simply returns a safe `"NETWORK"` error dictionary instead of crashing the client app. [Unit 5: sockets, Unit 3: exceptions]
