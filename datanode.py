#distributed database
import uuid
import os
import pickle

def printDictionary(dictionary):
    for k,v in dictionary.items():
        print("'{}': {}".format(k, v))
    print()

# Assert that the folder files exists
if os.path.isdir("files"):
    pass
elif os.path.exists("files"):
    print("ERROR: 'files' FOLDER COULD NOT BE CREATED BECAUSE A FILE EXISTS WITH THE SAME NAME")
    exit(1)
else:
    os.makedirs("files")

def upload(id, file_generator):
    print("Uploading")

    file = open("files/{}".format(id), "wb")
    for chunk in file_generator:
        file.write(chunk)
    file.close()

    print("Uploaded")

    return id


# returns a generator
def download(id):
    file = open("files/{}".format(id), "rb")
    while True:
        chunk = file.read(2**20)
        if not chunk:
            break
        yield chunk
    file.close()

# deletes file
def delete(id):
    os.remove("files/{}".format(id))

def getLength(id):
    file_length = os.path.getsize("files/{}".format(id))
    return file_length

# Handling http requests

import socket
import threading
import http_parser

def handle_http_request(conn,addr):
    print("\n\n\n")
    print(f"Connected by {addr}")
    request = http_parser.http_parser(conn)

    header = request.get_header()
    printDictionary(header)

    DEBUG_PRINT = True
    if(DEBUG_PRINT): print("Header = ",header)

    if header['method'] == "GET":
        if header['url'] == "/file":
            id = header['id']
            file_length = getLength(id)
            print("id = ",id," size = ",file_length)

            conn.sendall("POST /upload HTTP/1.1 200 OK\r\n".encode())
            conn.sendall("Content-Length: {}\r\n".format(file_length).encode())
            conn.sendall("\r\n".encode())

            for chunk in download(id):
                conn.sendall(chunk)

    if header['method'] == "GET":
        if header['url'] == "/delete":
            id = header['id']
            delete(id)

    if header['method'] == "POST":
        if header['url'] == "/upload":
            id = header['id']
            upload(id, request.get_file_chunks())

HOST = ""
PORT = 8082

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("", PORT))
    s.listen()

    print(f"Listening on {HOST}:{PORT}")

    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_http_request, args=(conn,addr)).start()
