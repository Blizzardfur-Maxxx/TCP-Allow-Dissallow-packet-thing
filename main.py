import socket
import threading

def handle_incoming(client_socket, remote_socket):
    while True:
        data = client_socket.recv(4096)
        if not data:
            break
        print("[Received from server]", data)

        # Wait for user input to approve the packet
        print("Approve this packet? (Press Enter for default 'y')")
        approve = input().strip().lower()
        if approve == '' or approve == 'y':
            remote_socket.send(data)
        else:
            print("Packet not approved.")
            continue

        remote_data = remote_socket.recv(4096)
        if not remote_data:
            break
        print("[Received from server]", remote_data)
        client_socket.send(remote_data)

def proxy_server(local_host, local_port, remote_host, remote_port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((local_host, local_port))
    server.listen(5)

    print(f"[*] Listening on {local_host}:{local_port}")

    while True:
        client_socket, addr = server.accept()
        print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
        
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect((remote_host, remote_port))

        proxy_thread = threading.Thread(target=handle_incoming, args=(client_socket, remote_socket))
        proxy_thread.start()

if __name__ == "__main__":
    remote_host = input("Enter remote server IP: ")
    remote_port = int(input("Enter remote server port: "))
    proxy_server('127.0.0.1', 25575, remote_host, remote_port)
