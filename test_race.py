import threading
import time
import config
import client_net

COURSE_TO_TEST = "CSE2005 Database Systems"
NUMBER_OF_CLIENTS = 10
SERVER_IP = "127.0.0.1"

def try_to_register(number, results):
    # one thread: send REGISTER with roll "RACE" + 5-digit number
    roll = f"RACE{number:05d}"
    request = {
        "action": "REGISTER",
        "name": "Race Tester",
        "roll_number": roll,
        "email": f"test{number}@example.com",
        "course": COURSE_TO_TEST
    }
    reply = client_net.send_request(SERVER_IP, request)
    status = reply.get("status")
    code = reply.get("code", "OK")
    results.append((roll, status, code))

def main():
    print(f"=== Race Condition Test ===")
    print(f"USE_LOCK in config.py is: {config.USE_LOCK}")
    
    if config.USE_LOCK:
        print("WARNING: USE_LOCK is True. You will likely NOT see a race condition.")
        print("Set config.USE_LOCK = False to demonstrate the flaw.")
    
    print(f"\nFetching initial seats for {COURSE_TO_TEST}...")
    reply = client_net.send_request(SERVER_IP, {"action": "GET_COURSES"})
    if reply.get("status") != "OK":
        print("Server not running or error fetching courses!")
        return
        
    initial_seats = reply["courses"].get(COURSE_TO_TEST)
    print(f"Initial seats available: {initial_seats}")
    
    print(f"\nSpawning {NUMBER_OF_CLIENTS} threads to register at the exact same time...")
    
    results = []
    threads = []
    
    for i in range(NUMBER_OF_CLIENTS):
        t = threading.Thread(target=try_to_register, args=(i, results))
        threads.append(t)
        
    # Start all threads
    for t in threads:
        t.start()
        
    # Wait for all threads to finish
    for t in threads:
        t.join()
        
    accepted = sum(1 for _, status, code in results if status == "OK")
    rejected_full = sum(1 for _, status, code in results if code == "FULL")
    rejected_other = len(results) - accepted - rejected_full
    
    print("\nFetching final seats...")
    reply = client_net.send_request(SERVER_IP, {"action": "GET_COURSES"})
    final_seats = reply["courses"].get(COURSE_TO_TEST)
    
    print("\n=== VERDICT ===")
    print(f"Initial seats: {initial_seats} | Threads sent: {NUMBER_OF_CLIENTS}")
    print(f"Accepted: {accepted} | Rejected(FULL): {rejected_full} | Rejected(Other): {rejected_other}")
    
    if accepted > initial_seats:
        print(f"-> OVERBOOKED! (race condition successfully demonstrated!)")
    elif accepted == initial_seats:
        print(f"-> EXACT MATCH. (Locking works, no overbooking!)")
    else:
        print(f"-> UNDERBOOKED. (Only {accepted} managed to register, {initial_seats} were available)")
        
    print(f"\nFinal seats left on server: {final_seats}")
    print("\n[!] Remind: Please press 'Reset Data' on the server dashboard before your next run.")

if __name__ == "__main__":
    main()
