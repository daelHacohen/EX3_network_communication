import socket
def client():
    client_socket =socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 12345))
    print("connected to the server")

    client_socket.send("GET_MAX_MSG_SIZE".encode())#מבקש את גודל ההודעה המקסימלי
    max_msg_size = int(client_socket.recv(1024).decode())
    print(f"Maximum message size from server: {max_msg_size} bytes")

    client_socket.send("GET_WINDOW_SIZE".encode())
    window_size = int(client_socket.recv(1024).decode())
    print(f"Window size from server: {window_size} bytes")

    message_for_the_server = input("Enter message for the server: ").encode('utf-8')

    for i in range(0, len(message_for_the_server), max_msg_size):
        chunk = message_for_the_server[i:i + max_msg_size]
        seq_num = i // max_msg_size  # חישוב מספר סידורי
        packet = f"{seq_num}:{chunk}"  # שילוב מספר סידורי ותוכן

        client_socket.send(packet.encode('utf-8'))  # שליחת המקטע
        print(f"Sent chunk {seq_num}: {chunk}")

        while True:
            ack = client_socket.recv(1024).decode('utf-8').strip()
            if ack == f"ACK:{seq_num}":
                print(f"Received ACK for packet {seq_num}")
                break  # יציאה מהלולאה אם התקבל ACK מתאים

    client_socket.close()
    print("the connected is closed")

if __name__ == "__main__":
   client()