import socket
import os

HOST = "192.168.0.14"
PORT = 1234

def send_file(conn, file_path, file_type):
    with open(file_path, "rb") as file:
        file_data = file.read()
        response = "HTTP/1.1 200 OK\r\n"
        response += "Content-Length: {}\r\n".format(len(file_data))
        response += "Content-Type: {}\r\n".format(file_type)
        response += "\r\n"
        conn.sendall(response.encode())
        conn.sendall(file_data)


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(("", PORT))
    s.listen()
    
    print(f"Listening on {HOST}:{PORT}")
    
    while True:
        conn, addr = s.accept()
        print(f"Connected by {addr}")
        request = conn.recv(1024).decode()
        print("Request = \n",request)
        
        if request.startswith("GET /video "):
            send_file(conn, "video.mp4", "video/mp4")

        elif request.startswith("GET /list "):
            os.system("ls > list.txt")
            send_file(conn, "list.txt", "text/html")


        elif request.startswith("GET / "):
            send_file(conn, "index.html", "text/html")
        
        conn.close()
