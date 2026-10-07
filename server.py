import time
import threading
import socket
import json
import config
import validation
import storage

def make_error(code, message):
    return {"status": "ERROR", "code": code, "message": message}

class RegistrationServer:
    def __init__(self):
        # Initialize seats left by copying from config.COURSES
        self.seats_left = dict(config.COURSES)
        self.roll_numbers = set()
        self.activity_log = []
        self.total_registered = 0
        self.lock = threading.Lock()
        self.running = False
        self.server_socket = None

    def load_existing_data(self):
        # Read from file to reconstruct state
        records = storage.load_registrations()
        for rec in records:
            if len(rec) >= 5:
                roll, name, email, course, timestamp = rec[:5]
                # upper-case the roll number just in case
                roll = roll.upper()
                self.roll_numbers.add(roll)
                if course in self.seats_left:
                    self.seats_left[course] -= 1
                self.total_registered += 1
        self.add_log(f"Loaded {self.total_registered} past registrations.")

    def start(self):
        storage.ensure_data_file()
        self.load_existing_data()
        
        # [Unit 5: sockets] create, bind, and listen
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((config.HOST, config.PORT))
        self.server_socket.listen()
        
        self.running = True
        self.add_log(f"Server started on port {config.PORT}")
        
        # [Unit 5: multithreading] start listener daemon thread
        listener_thread = threading.Thread(target=self.accept_loop, daemon=True)
        listener_thread.start()

    def accept_loop(self):
        while self.running:
            try:
                # [Unit 5: sockets] accept new connections
                conn, addr = self.server_socket.accept()
                # [Unit 5: multithreading] create one daemon thread per client
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True)
                client_thread.start()
            except OSError:
                break

    def handle_client(self, conn, addr):
        try:
            # [Unit 5: sockets] read JSON request
            data = conn.recv(config.BUFFER_SIZE).decode()
            if not data:
                return
                
            try:
                request = json.loads(data)
            except json.JSONDecodeError:
                reply = make_error("BAD_REQUEST", "Malformed JSON")
                conn.sendall((json.dumps(reply) + "\n").encode())
                return
                
            reply = self.process_request(request)
            
            # [Unit 5: sockets] send JSON reply
            conn.sendall((json.dumps(reply) + "\n").encode())
            
        except OSError:
            self.add_log(f"Connection error with {addr}")
        finally:
            # [Unit 5: sockets] always close the connection
            conn.close()

    def process_request(self, request):
        action = request.get("action")
        if action == "GET_COURSES":
            return self.get_courses()
        elif action == "REGISTER":
            return self.register(request)
        else:
            return make_error("BAD_REQUEST", "Unknown action")

    def get_courses(self):
        with self.lock:
            return {"status": "OK", "courses": dict(self.seats_left)}

    def register(self, request):
        if config.USE_LOCK:
            # [Unit 5: multithreading] one thread at a time in here
            with self.lock:
                return self.check_and_save(request)
        else:
            return self.check_and_save(request)

    def check_and_save(self, request):
        # 1. Validate fields
        name = request.get("name", "")
        roll = request.get("roll_number", "")
        email = request.get("email", "")
        course = request.get("course", "")
        
        err = validation.validate_fields(name, roll, email, course)
        if err:
            return make_error("INVALID", err)
            
        roll = roll.strip().upper()

        # 2. Check if course exists
        if course not in self.seats_left:
            return make_error("BAD_COURSE", f"Course not found: {course}")

        # 3. Check duplicate roll number
        if roll in self.roll_numbers:
            return make_error("DUPLICATE", f"Roll number {roll} is already registered.")

        # 4. Check seats left
        if self.seats_left[course] <= 0:
            self.add_log(f"FULL: {course} rejected {roll}")
            return make_error("FULL", f"No seats left in {course}")

        # Optional delay for demo
        if config.DEMO_DELAY > 0:
            time.sleep(config.DEMO_DELAY)

        # 5. Save to file
        try:
            storage.append_registration(roll, name, email, course)
        except OSError as e:
            return make_error("SERVER", "Failed to write to file.")

        # 6. Update memory (decrement seats, add roll, log)
        self.seats_left[course] -= 1
        self.roll_numbers.add(roll)
        self.total_registered += 1
        
        self.add_log(f"{roll} registered in {course}")
        
        return {
            "status": "OK",
            "message": f"Registered {roll} in {course}",
            "seats_left": self.seats_left[course]
        }

    def add_log(self, text):
        # Note: Must NOT acquire self.lock here, because caller might already hold it (deadlock)
        timestamp = time.strftime("%H:%M:%S")
        self.activity_log.append(f"{timestamp} {text}")

    def get_snapshot(self):
        with self.lock:
            return {
                "running": self.running,
                "seats_left": dict(self.seats_left),
                "total": self.total_registered,
                "log": list(self.activity_log)
            }

    def reset_data(self):
        with self.lock:
            storage.clear_registrations()
            self.seats_left = dict(config.COURSES)
            self.roll_numbers.clear()
            self.total_registered = 0
            self.activity_log.clear()
            self.add_log("Data reset.")

# TEMP TEST: remove in Phase 10
if __name__ == "__main__":
    print("Starting server... Press Ctrl+C to stop.")
    srv = RegistrationServer()
    srv.start()
    
    try:
        last_log_count = 0
        while True:
            snapshot = srv.get_snapshot()
            current_log = snapshot["log"]
            if len(current_log) > last_log_count:
                for line in current_log[last_log_count:]:
                    print(line)
                last_log_count = len(current_log)
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping server.")
        srv.running = False
        if srv.server_socket:
            srv.server_socket.close()
