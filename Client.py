import socket
def client():
    client_socket =socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 12345))
    print("connected to the server")
    client_socket.close()
    print("the connected us closed")

if __name__ == "__main__":
   client()