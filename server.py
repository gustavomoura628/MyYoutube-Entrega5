import socket
import os

import generate_player_html
import generate_list_html
import generate_index_html
import generate_404_html

import http_parser


HOST = ""
PORT = 8080


def send_bytes_of_file(conn, file_data, file_type):
    response = "HTTP/1.1 200 OK\r\n"
    response += "Content-Length: {}\r\n".format(len(file_data))
    response += "Content-Type: {}\r\n".format(file_type)
    response += "\r\n"
    conn.sendall(response.encode())
    conn.sendall(file_data)

def send_file(conn, file_path, file_type):
    file_length = os.path.getsize(file_path)

    response = "HTTP/1.1 200 OK\r\n"
    response += "Content-Length: {}\r\n".format(file_length)
    response += "Content-Type: {}\r\n".format(file_type)
    response += "\r\n"
    conn.sendall(response.encode())

    with open(file_path, "rb") as file:
        while True:
            read_bytes = file.read(2**20)
            if not read_bytes:
                break
            conn.sendall(read_bytes)

def get_body(request_data):
    header_end = request_data.find(b"\r\n\r\n")+4
    body = request_data[header_end:]
    return body


def remove_quotes(string):
    return string[1:len(string)-1]


def print_dictionary(table):
    for key in table:
        print(key, " = ", table[key])

import threading

def handle_http_request(conn, addr):
    print("\n\n\n")
    print(f"Connected by {addr}")
    request = http_parser.http_parser(conn)

    header = request.get_header()
    print_dictionary(header)

    DEBUG_PRINT = False
    if(DEBUG_PRINT): print("Header = ",header)

    if header['method'] == "GET":
        if header['url'].startswith("/video"):
            video_name = header['url'][len("/video/"):]
            # Replace %20 with spaces
            parts = video_name.split("%20")
            video_name = " ".join(parts)
            send_file(conn, "uploads/"+video_name, "video/mp4")

        elif header['url'] == "/list":
            list_html = generate_list_html.generate('uploads', host = header['Host'])
            send_bytes_of_file(conn, list_html, "text/html")

        elif header['url'].startswith("/watch"):
            video_name = header['url'][len("/watch/"):]
            video_player_html = generate_player_html.generate(video_name, host = header['Host'])
            send_bytes_of_file(conn, video_player_html, "text/html")

        elif header['url'] == "/favicon.ico":
            send_file(conn, "favicon.ico", "image/avif")

        elif header['url'] == "/":
            index_html = generate_index_html.generate(host = header['Host'])
            send_bytes_of_file(conn, index_html, "text/html")

        else:
            not_found_html = generate_404_html.generate(host = header['Host'])
            send_bytes_of_file(conn, not_found_html, "text/html")
    if header['method'] == "POST":
        if header['url'] == "/upload":
            DEBUG_PRINT = False
            content_type = http_parser.parse_line_of_value(header['Content-Type'])
            if(DEBUG_PRINT): print("Content Type Table = ",content_type)
            if content_type['main'] == "multipart/form-data": 
                sub_header = request.get_multipart_header()

                if(DEBUG_PRINT): print("sub Header = ",sub_header)

                content_disposition = http_parser.parse_line_of_value(sub_header['Content-Disposition'])
                if(DEBUG_PRINT): print("\n\n\ncontent_disposition = ",content_disposition)
                file_path = "uploads/"
                video_name = remove_quotes(content_disposition['filename'])
                file_path += video_name

                #sub_body_data = request.get_multipart_body_data()
                #if(DEBUG_PRINT): print("\n\n\nsub Body = ",sub_body_data)
                #with open(file_path, "wb") as file:
                #    file.write(sub_body_data)
                #request.write_until_content_length_to_file(file_path)

                file = open(file_path, "wb")
                for chunk in request.get_file_chunks():
                    file.write(chunk)
                file.close()


                video_player_html = generate_player_html.generate(video_name, host = header['Host'])
                send_bytes_of_file(conn, video_player_html, "text/html")

    else:
        not_found_html = generate_404_html.generate(host = header['Host'])
        send_bytes_of_file(conn, not_found_html, "text/html")

    conn.close()



# Make sure that uploads folder exists
if not os.path.exists("uploads"):
    os.makedirs("uploads")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("", PORT))
    s.listen()

    print(f"Listening on {HOST}:{PORT}")

    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_http_request, args=(conn,addr)).start()
