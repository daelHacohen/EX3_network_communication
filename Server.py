import socket

def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 12345))
    server_socket.listen()
    print("Server is listening...")

    #.....................max message size......................

    option = int(input("To send input with the max message size press (1). To read from the file press (2): "))

    if option==1:
        try:
            max_message_size = int(input("Enter max message size for the server: "))
        except ValueError:
            print("Invalid input. Using max message size from the file")
            max_message_size = get_value_from_file("a.txt", "maximum_msg_size")
    elif option==2:
        max_message_size = get_value_from_file("a.txt", "maximum_msg_size")
    else:
        print("Invalid input. Using max message size from the file")
        max_message_size = get_value_from_file("a.txt", "maximum_msg_size")

    #..............................................................
    # .....................window size......................

    option = int(input("To send input with the window size press (1). To read from the file press (2): "))

    if option == 1:
        try:
            window_size = int(input("Enter window size: "))
        except ValueError:
            print("Invalid input. Using window size from the file")
            window_size = get_value_from_file("a.txt", "window_size")
    elif option == 2:
        window_size = get_value_from_file("a.txt", "window_size")
    else:
        print("Invalid input. Using window size from the file")
        window_size = get_value_from_file("a.txt", "window_size")
    # ..............................................................

    while True:
        client_socket, address = server_socket.accept()
        print(f"Connection established with {address}")

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
        #
        all_the_message = ""
        expected_seq = 0
        while True:
            chunk = client_socket.recv(max_message_size + 4).decode('utf-8')  # מקבל מקטע
            if not chunk:
                break
            # print(chunk.strip("'b"))
            seq_num, data = chunk.split(":", 1)  # חלוקה למספר סידורי ולתוכן
            seq_num = int(seq_num)

            if seq_num == expected_seq:  # בדיקה אם המספר הסידורי תואם
                print(f"Received chunk {seq_num}: {data.strip('b')}")
                client_socket.send(f"ACK:{seq_num}\n".encode('utf-8')) # שולח ack
                all_the_message += data.strip("'b")
                expected_seq += 1
            else:
                print(f"Unexpected sequence number. Expected {expected_seq}, got {seq_num}")
        print(all_the_message)

        client_socket.close()
        print("the connected is closed")



def get_value_from_file(file_name, variable_name):
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

