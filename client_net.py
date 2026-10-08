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


