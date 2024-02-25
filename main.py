import socket
import threading
import argparse
import binascii

def handle_client(client_socket, remote_socket, manual_approval_client, decode_packets):
    while True:
        try:
            data = client_socket.recv(4096)
            if not data:
                break
            decoded_data = ""
            if decode_packets:
                try:
                    decoded_data = data.decode('utf-8')
                except UnicodeDecodeError:
                    pass
            else:
                decoded_data = binascii.hexlify(data).decode('utf-8')
            if decoded_data:
                print("[Received from client]", decoded_data)

            if manual_approval_client:
                print("Approve this packet from client to server? (Press Enter for default 'y')")
                approve = input().strip().lower()
                if approve == '' or approve == 'y':
                    remote_socket.send(data)
                else:
                    print("Packet not approved.")
                    continue
            else:
                remote_socket.send(data)

            remote_data = remote_socket.recv(4096)
            if not remote_data:
                break
            decoded_remote_data = ""
            if decode_packets:
                try:
                    decoded_remote_data = remote_data.decode('utf-8')
                except UnicodeDecodeError:
                    pass
            else:
                decoded_remote_data = binascii.hexlify(remote_data).decode('utf-8')
            if decoded_remote_data:
                print("[Sent from client]", decoded_remote_data)
            client_socket.send(remote_data)
        except Exception as e:
            print(f"An error occurred: {e}")
            break


def handle_server(client_socket, remote_socket, manual_approval_server, decode_packets):
    while True:
        remote_data = remote_socket.recv(4096)
        if not remote_data:
            break
        decoded_remote_data = ""
        if decode_packets:
            try:
                decoded_remote_data = remote_data.decode('utf-8')
            except UnicodeDecodeError:
                pass
        else:
            decoded_remote_data = binascii.hexlify(remote_data).decode('utf-8')
        if decoded_remote_data:
            print("[Received from server]", decoded_remote_data)

        if manual_approval_server:
            print("Approve this packet from server to client? (Press Enter for default 'y')")
            approve = input().strip().lower()
            if approve == '' or approve == 'y':
                client_socket.send(remote_data)
            else:
                print("Packet not approved.")
                continue
        else:
            client_socket.send(remote_data)

def proxy_server(local_host, local_port, remote_host, remote_port, manual_approval_client, manual_approval_server, decode_packets):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((local_host, local_port))
    server.listen(5)

    print(f"[*] Listening on {local_host}:{local_port}")

    while True:
        client_socket, addr = server.accept()
        print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
        
        remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_socket.connect((remote_host, remote_port))

        if manual_approval_client:
            proxy_thread = threading.Thread(target=handle_client, args=(client_socket, remote_socket, True, decode_packets))
        else:
            proxy_thread = threading.Thread(target=handle_server, args=(client_socket, remote_socket, manual_approval_server, decode_packets))
        proxy_thread.start()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Proxy Server")
    parser.add_argument("remote_host", type=str, nargs='?', help="Remote server IP")
    parser.add_argument("remote_port", type=int, nargs='?', help="Remote server port")
    parser.add_argument("--client", action="store_true", help="Enable manual approval mode for packets from client to server")
    parser.add_argument("--server", action="store_true", help="Enable manual approval mode for packets from server to client")
    parser.add_argument("--decode", action="store_true", help="Decode packet contents as UTF-8")
    args = parser.parse_args()

    if not args.remote_host or not args.remote_port:
        args.remote_host = input("Enter remote server IP: ")
        args.remote_port = int(input("Enter remote server port: "))

    if not args.client and not args.server:
        print("Choose mode:")
        print("1. Manual approval for packets from client to server")
        print("2. Manual approval for packets from server to client")
        choice = input("Enter your choice: ").strip()
        if choice == '1':
            args.client = True
        elif choice == '2':
            args.server = True
        else:
            print("Invalid choice. Using automatic forwarding.")

    manual_approval_client = args.client
    manual_approval_server = args.server
    decode_packets = args.decode

    if not decode_packets:
        decode_choice = input("Decode packet contents? (y/n): ").strip().lower()
        decode_packets = True if decode_choice == 'y' else False

    proxy_server('127.0.0.1', 25567, args.remote_host, args.remote_port, manual_approval_client, manual_approval_server, decode_packets)
