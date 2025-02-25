import socket
import time

#פונקציה ראשית לclient
def client():
    client_socket = initialize_client()
    max_msg_size, window_size = request_server_parameters(client_socket)
    timeout = get_timeout_value()
    message = input("Enter message for the server: ").encode('utf-8')
    chunks = split_message_into_chunks(message, max_msg_size)
    send_message(client_socket, chunks, window_size, timeout)
    client_socket.close()
    print("The connection is closed")

#פותח סוקט לקליינט ומתחבר עם פרוטוקול TCP
def initialize_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 8080))
    print("Connected to the server")
    return client_socket

#מבקש מהשרת את גודל החלון הזזה וגודל ההודעה המקסימלי
def request_server_parameters(client_socket):
    client_socket.send("GET_MAX_MSG_SIZE".encode())
    max_msg_size = int(client_socket.recv(1024).decode())
    print(f"Maximum message size from server: {max_msg_size} bytes")

    client_socket.send("GET_WINDOW_SIZE".encode())
    window_size = int(client_socket.recv(1024).decode())
    print(f"Window size from server: {window_size} bytes")

    return max_msg_size, window_size

#מבקש מהלקוח timeout
def get_timeout_value():
    option = int(input("To send input for the timeout press (1). To read from the file press (2): "))
    if option == 1:
        try:
            return int(input("Enter timeout: "))
        except ValueError:
            print("Invalid input. Using timeout from the file")
    return get_value_from_file("a.txt", "timeout")


def get_value_from_file(file_name, variable_name):
    with open(file_name, 'r') as file:
        for line in file:
            if line.startswith(f"{variable_name}:"):
                value = line.strip().split(":", 1)[1]
                return int(value.strip()) if value.isdigit() else value.strip()
    return None

#מחלק את ההודעה לחבילות בגודל של המקסימלי + header
def split_message_into_chunks(message, max_msg_size):
    chunks = []
    for i in range(0, len(message), max_msg_size):
        chunk_content = message[i:i + max_msg_size]
        header = f"{i // max_msg_size:04d}".encode('utf-8')
        chunks.append(header + chunk_content)
    return chunks


def send_message(client_socket, chunks, window_size, timeout):
    num_chunks = len(chunks)
    base, next_seq_num, max_ack = 0, 0, -1
    acks_received = set()
    timer_start = None

    #כל עוד כל החבילות לא נשלחו
    while base < num_chunks:

        while next_seq_num < base + window_size and next_seq_num < num_chunks:
            client_socket.send(chunks[next_seq_num])
            if timer_start is None:
                timer_start = time.time()
            print(f"Sent chunk {next_seq_num}: {chunks[next_seq_num][4:].decode('utf-8')}")
            next_seq_num += 1

        try:
            client_socket.settimeout(timeout - (time.time() - timer_start))
            ack_data = client_socket.recv(1024).decode('utf-8')
            for ack_msg in ack_data.strip().split("\n"):
                if ack_msg.startswith("ACK:"):
                    try:
                        ack_num = int(ack_msg[4:])
                        print(f"Received ACK for chunk {ack_num}")
                        acks_received.add(ack_num)
                        max_ack = max(max_ack, ack_num)
                    except ValueError:
                        print(f"Invalid ACK message: {ack_msg}")

            while base in acks_received:
                base += 1
        except socket.timeout:5
            #קיבל את האק הכי גדול
            if max_ack >= base:
                timer_start = time.time()
                base = max_ack + 1
                continue

            print("Timeout occurred. Resending unacknowledged chunks...")
            for i in range(base, next_seq_num):
                if i not in acks_received:
                    client_socket.send(chunks[i])
                    print(f"Resent chunk {i}: {chunks[i][4:].decode('utf-8')}")
            timer_start = time.time()


if __name__ == "__main__":
    client()
