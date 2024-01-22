import rpyc
database = rpyc.connect_by_service("Database").root

import socket
import os

import generate_player_html
import generate_list_html
import generate_index_html
import generate_404_html
import search

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

import time

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
            print(f'/video request')
            video_id = header['url'][len("/video/"):]

            file_length = database.metadata(video_id)['size']

            # Returning file to client
            conn.sendall("HTTP/1.1 200 OK\r\n".encode())
            conn.sendall("Content-Length: {}\r\n".format(file_length).encode())
            conn.sendall("Content-Type: {}\r\n".format("video/mp4").encode())
            conn.sendall("\r\n".encode())

            

            start_time = time.time()
            for chunk in database.file(video_id):
                conn.sendall(chunk)
            total_time = time.time() - start_time

            video_name = database.metadata(video_id)['name']

            print(f'Time to send "{video_name}": {total_time} seconds')

        elif header['url'] == "/list":
            print(f'/list request')
            list = database.list()

            list_html = generate_list_html.generate(list, host = header['Host'])
            send_bytes_of_file(conn, list_html, "text/html")

        elif header['url'].startswith("/watch"):
            print(f'/watch request')
            video_id = header['url'][len("/watch/"):]

            metadata = database.metadata(video_id)

            #TODO: get video metadata
            video_player_html = generate_player_html.generate(video_id, metadata['name'], host = header['Host'])
            send_bytes_of_file(conn, video_player_html, "text/html")

        elif header['url'].startswith("/search"):
            print(f'/search request')
            search_query = header['url'][len("/search?query="):]
            import re
            search_query = re.sub(r"%[0-9]*", " ", search_query)


            list = database.list()
            matches = search.search_strings(list, search_query)
            list_matches = {}
            for id in matches:
                list_matches[id] = list[id]

            print("Results = ",list)

            list_html = generate_list_html.generate(list_matches, host = header['Host'])
            send_bytes_of_file(conn, list_html, "text/html")



        elif header['url'].startswith("/delete"):
            print(f'/delete request')
            video_id = header['url'][len("/delete/"):]
            database.delete(video_id)
            list = database.list()

            list_html = generate_list_html.generate(list, host = header['Host'])
            send_bytes_of_file(conn, list_html, "text/html")

        elif header['url'] == "/favicon.ico":
            print(f'/favicon.ico request')
            send_file(conn, "favicon.ico", "image/avif")

        elif header['url'] == "/":
            print(f'/ request')
            index_html = generate_index_html.generate(host = header['Host'])
            send_bytes_of_file(conn, index_html, "text/html")

        else:
            not_found_html = generate_404_html.generate(host = header['Host'])
            send_bytes_of_file(conn, not_found_html, "text/html")
    elif header['method'] == "POST":
        if header['url'] == "/upload":
            print(f'/upload request')
            DEBUG_PRINT = True
            content_type = http_parser.parse_line_of_value(header['Content-Type'])
            if(DEBUG_PRINT): print("Content Type Table = ",content_type)
            if content_type['main'] == "multipart/form-data": 
                sub_header = request.get_multipart_header()

                if(DEBUG_PRINT): print("sub Header = ",sub_header)

                content_disposition = http_parser.parse_line_of_value(sub_header['Content-Disposition'])
                if(DEBUG_PRINT): print("\n\n\ncontent_disposition = ",content_disposition)
                video_name = remove_quotes(content_disposition['filename'])

                file_length = request.get_content_length_of_file()

                start_time = time.time()
                video_id = database.upload(video_name, file_length, request.get_file_chunks())
                total_time = time.time() - start_time
                print(f'Time to upload "{video_name}": {total_time} seconds')


                video_player_html = generate_player_html.generate(video_id, video_name, host = header['Host'])
                send_bytes_of_file(conn, video_player_html, "text/html")

    else:
        print(f'invalid request')
        not_found_html = generate_404_html.generate(host = header['Host'])
        send_bytes_of_file(conn, not_found_html, "text/html")

    conn.close()



with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("", PORT))
    s.listen()

    print(f"Listening on {HOST}:{PORT}")

    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_http_request, args=(conn,addr)).start()
