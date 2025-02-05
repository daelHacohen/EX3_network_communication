import socket
import time


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
#----------------------------------------------------------------------------------------------------
    option = int(input("To send input for the timeout press (1). To read from the file press (2): "))

    if option == 1:
        try:
            timeout = int(input("Enter timeout: "))
        except ValueError:
            print("Invalid input. Using timeout from the file")
            timeout = get_value_from_file("a.txt", "timeout")
    elif option == 2:
        timeout = get_value_from_file("a.txt", "timeout")
    else:
        print("Invalid input. Using timeout from the file")
        timeout = get_value_from_file("a.txt", "timeout")
#-----------------------------------------------------------------------------------------------
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
    timer_start = None  # התחלת הטיימר
    max_ack = -1

    # ---------------------שליחת החתיכות לשרת----------------------------
    while base < num_chunks:
        # שליחת הודעות במסגרת חלון ההזזה
        while next_seq_num < base + window_size and next_seq_num < num_chunks:
            client_socket.send(chunks[next_seq_num])  # שולחים את החתיכה (כבר כוללת Header)
            if timer_start is None:  # התחלת טיימר אם זו ההודעה הראשונה
                timer_start = time.time()
            print(f"Sent chunk {next_seq_num}: {chunks[next_seq_num][4:].decode('utf-8')}")
            next_seq_num += 1

        try:
            client_socket.settimeout(timeout - (time.time() - timer_start))
            ack_data = client_socket.recv(1024).decode('utf-8')  # קבלת הנתונים מהשרת
            ack_messages = ack_data.strip().split("\n")  # פיצול ההודעות לפי קו מפריד '\n'



            for ack_msg in ack_messages:  # עיבוד כל הודעת ACK בנפרד
                if ack_msg.startswith("ACK:"):  # בדיקה אם ההודעה מתחילה ב-"ACK:"
                    try:
                        ack_num = int(ack_msg[4:])  # שליפת המספר הסידורי מתוך ההודעה
                        print(f"Received ACK for chunk {ack_num}")
                        acks_received.add(ack_num)  # הוספת המספר הסידורי לרשימת ה-ACKs שהתקבלו

                        if ack_num > max_ack:
                            max_ack = ack_num

                    except ValueError:
                        print(f"Invalid ACK message: {ack_msg}")  # טיפול במקרה שבו ההודעה לא תקינה

            # דכון הבסיס (base) לחלון ההזזה
            while base in acks_received:
                base += 1


        except socket.timeout:

            if max_ack >= base:
                timer_start = time.time()  # לא נחשב timeout מחדש
                base= max_ack+1
                continue

            print("Timeout occurred. Resending unacknowledged chunks...")
            for i in range(base, next_seq_num):
                if i not in acks_received:
                    client_socket.send(chunks[i])
                    print(f"Resent chunk {i}: {chunks[i][4:].decode('utf-8')}")
            timer_start = time.time()  # הפעלת טיימר מחדש לאחר שליחה מחדש

    client_socket.close()
    print("the connected is closed")

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
   client()