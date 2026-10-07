import time
import threading
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

    def get_courses(self):
        with self.lock:
            return {"status": "OK", "courses": dict(self.seats_left)}

    def register(self, request):
        if config.USE_LOCK:
            # [Unit 5: Multithreading] one thread at a time in here
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
    print("Testing server logic...")
    storage.ensure_data_file()
    storage.clear_registrations()
    
    srv = RegistrationServer()
    srv.load_existing_data()
    
    # 1. Success
    r1 = srv.register({"name": "Asmi", "roll_number": "24BCE1000", "email": "a@x.com", "course": "CSE3011 Python Programming"})
    print("1. Success:", r1["status"])
    
    # 2. Duplicate roll
    r2 = srv.register({"name": "Asmi 2", "roll_number": "24BCE1000", "email": "a@x.com", "course": "CSE2001 Data Structures"})
    print("2. Duplicate:", r2["code"])
    
    # 3. Bad course
    r3 = srv.register({"name": "Niharika", "roll_number": "24BCE1001", "email": "n@x.com", "course": "Unknown Course"})
    print("3. Bad Course:", r3["code"])
    
    # 4. Invalid field
    r4 = srv.register({"name": "", "roll_number": "24BCE1002", "email": "n@x.com", "course": "CSE2001 Data Structures"})
    print("4. Invalid:", r4["code"])
    
    # 5. Full course (CSE2001 has 3 seats. Fill it.)
    srv.register({"name": "S1", "roll_number": "24BCE1003", "email": "x@x.com", "course": "CSE2001 Data Structures"})
    srv.register({"name": "S2", "roll_number": "24BCE1004", "email": "x@x.com", "course": "CSE2001 Data Structures"})
    srv.register({"name": "S3", "roll_number": "24BCE1005", "email": "x@x.com", "course": "CSE2001 Data Structures"})
    
    r5 = srv.register({"name": "S4", "roll_number": "24BCE1006", "email": "x@x.com", "course": "CSE2001 Data Structures"})
    print("5. Full Course:", r5["code"])
    
    print("\nLog:")
    for line in srv.activity_log:
        print(line)
        
    print("\nRestarting server to test load...")
    srv2 = RegistrationServer()
    srv2.load_existing_data()
    print("Seats left after reload:", srv2.get_courses()["courses"])
