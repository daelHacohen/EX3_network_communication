import socket
import time
import json

def client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 12345))
    print("Connected to the server")

    # בקשת גודל הודעה מקסימלי
    client_socket.send("GET_MAX_MSG_SIZE".encode())
    max_msg_size = int(client_socket.recv(1024).decode())
    print(f"Maximum message size from server: {max_msg_size} bytes")

    # בקשת גודל חלון
    client_socket.send("GET_WINDOW_SIZE".encode())
    window_size = int(client_socket.recv(1024).decode())
    print(f"Window size from server: {window_size} bytes")

    # בקשת timeout
    client_socket.send("GET_TIMEOUT".encode())
    timeout_value = float(client_socket.recv(1024).decode())
    print(f"Timeout value from server: {timeout_value} seconds")

    # קבלת הודעה לשליחה
    message_for_the_server = input("Enter message for the server: ").encode('utf-8')

    # חלוקת ההודעה למקטעים
    chunks = [
        message_for_the_server[i:i + max_msg_size]
        for i in range(0, len(message_for_the_server), max_msg_size)
    ]
    num_chunks = len(chunks)

    # משתנים לניהול חלון הזזה
    base = 0  # תחילת החלון
    next_seq_num = 0  # המספר הסידורי הבא לשליחה
    acks_received = set()  # רשימת ה-ACK שהתקבלו
    timer_start = None  # זמן התחלה של הטיימר

    while base < num_chunks:
        # שליחת הודעות במסגרת חלון ההזזה
        while next_seq_num < base + window_size and next_seq_num < num_chunks:
            packet = f"{next_seq_num}:{chunks[next_seq_num].decode('utf-8')}"
            client_socket.send(packet.encode('utf-8'))
            print(f"Sent chunk {next_seq_num}: {chunks[next_seq_num].decode('utf-8')}")
            if timer_start is None:
                timer_start = time.time()
            next_seq_num += 1

        # קבלת ACKs או בדיקת timeout
        try:
            client_socket.settimeout(timeout_value)
            ack = client_socket.recv(1024).decode('utf-8').strip()
            if ack.startswith("ACK:"):
                ack_num = int(ack.split(":")[1])
                print(f"Received ACK for chunk {ack_num}")
                acks_received.add(ack_num)

                # עדכון תחילת החלון
                while base in acks_received:
                    base += 1
                    timer_start = time.time() if base < next_seq_num else None
        except socket.timeout:
            print("Timeout waiting for ACKs. Resending all unacknowledged messages...")
            for seq in range(base, next_seq_num):
                if seq not in acks_received:
                    packet = f"{seq}:{chunks[seq].decode('utf-8')}"
                    client_socket.send(packet.encode('utf-8'))
                    print(f"Resent chunk {seq}: {chunks[seq].decode('utf-8')}")
            timer_start = time.time()

    print("All chunks sent and acknowledged.")
    client_socket.close()
    print("Connection closed.")

if __name__ == "__main__":
    client()
