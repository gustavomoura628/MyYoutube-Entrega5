#distributed database
import uuid
import os
import pickle

def printDictionary(dictionary):
    for k,v in dictionary.items():
        print("'{}': {}".format(k, v))
    print()

# Create or load global variable metadata
# TODO: Currently the way this is handled can cause race conditions
metadata = {}
if os.path.exists("metadata_pickle.pyc"):
    metadata_pickle = open("metadata_pickle.pyc", "rb")
    metadata = pickle.load(metadata_pickle)
    metadata_pickle.close()

printDictionary(metadata)

# Assert that the folder files exists
if os.path.isdir("files"):
    pass
elif os.path.exists("files"):
    print("ERROR: 'files' FOLDER COULD NOT BE CREATED BECAUSE A FILE EXISTS WITH THE SAME NAME")
    exit(1)
else:
    os.makedirs("files")

def updateMetadataFile():
    metadata_pickle = open("metadata_pickle.pyc", "wb")
    pickle.dump(metadata, metadata_pickle)
    metadata_pickle.close()


def idAlreadyExists(id):
    return id in metadata

def genId():
    id = str(uuid.uuid4())
    while idAlreadyExists(id):
        id = str(uuid.uuid4())
    return id

def upload(file_metadata, file_generator):
    print("Uploading")
    printDictionary(file_metadata)

    # metadata has the format: { name: "Name" }
    id = genId()
    metadata[id] = file_metadata
    updateMetadataFile()

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
    metadata.pop(id)
    updateMetadataFile()

    os.remove("files/{}".format(id))

def getLength(id):
    file_length = os.path.getsize("files/{}".format(id))
    return file_length

#def uploadTo(datanode, Id):
#    pass
#
#def downloadFrom(datanode, Id):
#    pass

def getList():
    list = {}
    for k,v in metadata.items():
        list[k] = v['name']
    return list




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
            #file_length = metadata[id]['size']
            file_length = getLength(id)
            print("id = ",id," size = ",file_length)

            conn.sendall("POST /upload HTTP/1.1 200 OK\r\n".encode())
            conn.sendall("Content-Length: {}\r\n".format(file_length).encode())
            conn.sendall("name: {}\r\n".format(metadata[id]['name']).encode())
            conn.sendall("\r\n".encode())

            for chunk in download(id):
                conn.sendall(chunk)

    if header['method'] == "GET":
        if header['url'] == "/list":
            list_string = pickle.dumps(getList())
            file_length = len(list_string)

            conn.sendall("POST /list HTTP/1.1 200 OK\r\n".encode())
            conn.sendall("Content-Length: {}\r\n".format(file_length).encode())
            conn.sendall("\r\n".encode())

            conn.sendall(list_string)

    if header['method'] == "GET":
        if header['url'] == "/delete":
            id = header['id']
            delete(id)

    if header['method'] == "POST":
        if header['url'] == "/upload":
            print("File name = ",header['name'])
            id = upload({ 'name': header['name'] }, request.get_file_chunks())

            print("Sending response to application")
            conn.sendall("POST /id HTTP/1.1 200 OK\r\n".encode())
            conn.sendall("id: {}\r\n".format(id).encode())
            conn.sendall("\r\n".encode())
            print("Sent")

HOST = ""
PORT = 8081

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("", PORT))
    s.listen()

    print(f"Listening on {HOST}:{PORT}")

    while True:
        conn, addr = s.accept()
        threading.Thread(target=handle_http_request, args=(conn,addr)).start()
