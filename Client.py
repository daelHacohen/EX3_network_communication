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

    # ---------------------מחלק את ההודעה ל-chunks עם Header----------------------------
    chunks = []  # רשימה ריקה לאחסון החתיכות
    for i in range(0, len(message_for_the_server), max_msg_size):
        chunk_content = message_for_the_server[i:i + max_msg_size]  # חותכים מקטע מהמחרוזת
        header = f"{i // max_msg_size:04d}"  # יוצרים Header עם מספר סידורי בפורמט 4 ספרות
        chunk_with_header = header.encode('utf-8') + chunk_content  # מחברים את ה-Header לתוכן
        chunks.append(chunk_with_header)  # מוסיפים את החתיכה עם ה-Header לרשימה

    num_chunks = len(chunks)
    base = 0  # תחילת החלון
    next_seq_num = 0  # המספר הסידורי הבא לשליחה
    acks_received = set()  # רשימת ה-ACK שהתקבלו

    # ---------------------שליחת החתיכות לשרת----------------------------
    while base < num_chunks:
        # שליחת הודעות במסגרת חלון ההזזה
        while next_seq_num < base + window_size and next_seq_num < num_chunks:
            client_socket.send(chunks[next_seq_num])  # שולחים את החתיכה (כבר כוללת Header)
            print(f"Sent chunk {next_seq_num}: {chunks[next_seq_num][4:].decode('utf-8')}")
            next_seq_num += 1

        ack_data = client_socket.recv(1024).decode('utf-8')  # קבלת הנתונים מהשרת
        ack_messages = ack_data.strip().split("\n")  # פיצול ההודעות לפי קו מפריד '\n'
        for ack_msg in ack_messages:  # עיבוד כל הודעת ACK בנפרד
            if ack_msg.startswith("ACK:"):  # בדיקה אם ההודעה מתחילה ב-"ACK:"
                try:
                    ack_num = int(ack_msg[4:])  # שליפת המספר הסידורי מתוך ההודעה
                    print(f"Received ACK for chunk {ack_num}")
                    acks_received.add(ack_num)  # הוספת המספר הסידורי לרשימת ה-ACKs שהתקבלו
                except ValueError:
                    print(f"Invalid ACK message: {ack_msg}")  # טיפול במקרה שבו ההודעה לא תקינה

        # דכון הבסיס (base) לחלון ההזזה
        while base in acks_received:
            base += 1


    client_socket.close()
    print("the connected is closed")

if __name__ == "__main__":
   client()