import socket
def client():
    client_socket =socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 12345))
    print("connected to the server")

    client_socket.send("GET_MAX_MSG_SIZE".encode())#מבקש את גודל ההודעה המקסימלי
    max_msg_size = int(client_socket.recv(1024).decode())
    print(f"Maximum message size from server: {max_msg_size} bytes")

    message_for_the_server = input("Enter message for the server: ")#צריך להשלים
    client_socket.send(message_for_the_server.encode())#צריך להשלים


    client_socket.close()
    print("the connected is closed")

if __name__ == "__main__":
   client()