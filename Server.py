import socket

def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 12345))
    server_socket.listen()
    print("Server is listening...")

    #.....................max message size......................

    max_message_size1 = get_value_from_file("a.txt", "maximum_msg_size")
    try:
        max_message_size2 = int(input("Enter max message size for the server: "))
    except ValueError:
        print("Invalid input. Using default max message size: 1024")
        max_message_size2 = max_message_size1
    max_message_size = max(max_message_size1, max_message_size2)
    #..............................................................

    while True:
        client_socket, address = server_socket.accept()
        print(f"Connection established with {address}")

        request = client_socket.recv(1024).decode()
        if request == "GET_MAX_MSG_SIZE":
            client_socket.send(str(max_message_size).encode())
            print(f"max message size: {max_message_size}")
        else:
            print(f"Unknown request: {request}")

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

