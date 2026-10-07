import socket
import json
import config

def send_request(server_ip, request):
    """
    Sends a JSON request to the server and returns the JSON reply.
    Catches all network errors and returns a safe error dictionary.
    """
    sock = None
    try:
        # [Unit 5: sockets]
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(config.TIMEOUT)
        sock.connect((server_ip, config.PORT))
        
        # Send
        payload = json.dumps(request) + "\n"
        sock.sendall(payload.encode())
        
        # Receive
        data = sock.recv(config.BUFFER_SIZE).decode()
        if not data:
            return {"status": "ERROR", "code": "NETWORK", "message": "Empty reply from server."}
            
        return json.loads(data)
        
    except (OSError, ValueError) as e:
        return {
            "status": "ERROR",
            "code": "NETWORK",
            "message": f"Could not connect to {server_ip}:{config.PORT}.\nIs the server running?"
        }
    finally:
        if sock:
            sock.close()

# TEMP TEST: remove in Phase 10
if __name__ == "__main__":
    import sys
    ip = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    
    print(f"Testing client_net.py connecting to {ip}...")
    
    # 1. Fetch courses
    print("\n1. Fetching courses:")
    res = send_request(ip, {"action": "GET_COURSES"})
    print(res)
    
    if res.get("status") == "OK":
        # 2. Register one student
        print("\n2. Registering student:")
        res = send_request(ip, {
            "action": "REGISTER", 
            "name": "Phase 5 Test", 
            "roll_number": "TEST5", 
            "email": "test5@example.com", 
            "course": "CSE3011 Python Programming"
        })
        print(res)
        
        # 3. Try the same roll again
        print("\n3. Duplicate registration:")
        res = send_request(ip, {
            "action": "REGISTER", 
            "name": "Phase 5 Test", 
            "roll_number": "TEST5", 
            "email": "test5@example.com", 
            "course": "CSE3011 Python Programming"
        })
        print(res)
        
        # 4. Try wrong IP (should timeout/fail gracefully)
        print("\n4. Wrong IP test:")
        res = send_request("192.0.2.1", {"action": "GET_COURSES"})
        print(res)
