import socket

def server():
    server_socket = initialize_server()
    max_message_size = get_max_message_size()
    window_size = get_window_size()

    while True:
        client_socket, address = server_socket.accept()
        print(f"Connection established with {address}")

        handle_client(client_socket, max_message_size, window_size)
        client_socket.close()
        print("The connection is closed")


def initialize_server():
    """Initializes and starts the server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 8080))
    server_socket.listen()
    print("Server is listening...")
    return server_socket


def get_max_message_size():
    """Gets the maximum message size from the user or file."""
    option = int(input("To send input with the max message size press (1). To read from the file press (2): "))

    if option == 1:
        try:
            return int(input("Enter max message size for the server: "))
        except ValueError:
            print("Invalid input. Using max message size from the file")
    return get_value_from_file("a.txt", "maximum_msg_size")


def get_window_size():
    """Gets the window size from the user or file."""
    option = int(input("To send input with the window size press (1). To read from the file press (2): "))

    if option == 1:
        try:
            return int(input("Enter window size: "))
        except ValueError:
            print("Invalid input. Using window size from the file")
    return get_value_from_file("a.txt", "window_size")


def handle_client(client_socket, max_message_size, window_size):
    """Handles a connected client."""
    request = client_socket.recv(1024).decode()
    if request == "GET_MAX_MSG_SIZE":
        client_socket.send(str(max_message_size).encode())
        print(f"max message size: {max_message_size}")
    else:
        print(f"Unknown request: {request}")

    request = client_socket.recv(1024).decode()
    if request == "GET_WINDOW_SIZE":
        client_socket.send(str(window_size).encode())
        print(f"window size: {window_size}")
    else:
        print(f"Unknown request: {request}")

    process_chunks(client_socket, max_message_size)


def process_chunks(client_socket, max_message_size):
    """Processes incoming chunks from the client."""
    all_the_message = ""
    expected_seq = 0
    received_chunks = {}  # Store chunks by sequence number

    while True:
        chunk = client_socket.recv(max_message_size + 4).decode('utf-8')  # Receive chunk
        if not chunk:
            break

        # Split chunk into header (sequence number) and content
        seq_num = int(chunk[:4])  # First 4 characters are the sequence number
        data = chunk[4:]  # Remaining is the content

        if seq_num == expected_seq:  # Sequence matches
            print(f"Received chunk {seq_num}: {data}")
            all_the_message += data
            expected_seq += 1

            # Check for out-of-order chunks that can now be processed
            while expected_seq in received_chunks:
                all_the_message += received_chunks.pop(expected_seq)
                print(f"Processing out-of-order chunk {expected_seq}")
                expected_seq += 1
            #שולח hack על החבילה הכי גדולה
            client_socket.send(f"ACK:{expected_seq - 1:04d}\n".encode('utf-8'))

        #אם התקבלה חבילה מחוץ לסדר
        elif seq_num > expected_seq:  # Out-of-order chunk
            print(f"Out-of-order chunk {seq_num}: storing for later")
            received_chunks[seq_num] = data
            client_socket.send(f"ACK:{expected_seq-1:04d}\n".encode('utf-8'))

        else:  # Duplicate or late chunk
            print(f"Duplicate or late chunk {seq_num}, ignoring")
            client_socket.send(f"ACK:{seq_num:04d}\n".encode('utf-8'))

    print(f"Full message: {all_the_message}")


def get_value_from_file(file_name, variable_name):
    """Reads a value from a file based on a variable name."""
    with open(file_name, 'r') as file:
        for line in file:
            if line.startswith(f"{variable_name}:"):
                value = line.strip().split(":", 1)[1]
                if value.isdigit():
                    return int(value.strip())
                return value.strip()
    return None

if __name__ == "__main__":
   server()
