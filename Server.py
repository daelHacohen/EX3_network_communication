import socket

def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 12345))
    server_socket.listen()
    print("Server is listening...")

    while True:
        client_socket, address = server_socket.accept()
        print(f"Connection established with {address}")
        client_socket.close()
        print("the connected us closed")

if __name__ == "__main__":
    run_server()

