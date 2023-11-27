#distributed database
import uuid
import os
import pickle
import random

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

datanode_list = []

datanode_file = open('datanodes.txt', 'r')
for line in datanode_file.readlines():
    ip, port = line.strip().split(' ')
    datanode_list.append((ip,int(port)))

print("datanode list = ",datanode_list)

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


def uploadTo(datanode, id, file_length, file_generator):
    # Sending file to datanode
    datanode_s = socket.socket()
    datanode_s.connect(datanode)

    datanode_s.sendall("POST /upload HTTP/1.1 200 OK\r\n".encode())
    datanode_s.sendall("Content-Length: {}\r\n".format(file_length).encode())
    datanode_s.sendall("id: {}\r\n".format(id).encode())
    datanode_s.sendall("\r\n".encode())

    for chunk in file_generator:
        datanode_s.sendall(chunk)

def uploadToMultiple(datanodes, id, file_length, file_generator):
    # Sending file to datanode
    datanode_s_list = []
    for i, datanode in enumerate(datanodes):
        datanode_s_list.append(socket.socket())
        datanode_s_list[i].connect(datanode)

        datanode_s_list[i].sendall("POST /upload HTTP/1.1 200 OK\r\n".encode())
        datanode_s_list[i].sendall("Content-Length: {}\r\n".format(file_length).encode())
        datanode_s_list[i].sendall("id: {}\r\n".format(id).encode())
        datanode_s_list[i].sendall("\r\n".encode())

    for chunk in file_generator:
        for datanode_s in datanode_s_list:
            datanode_s.sendall(chunk)

def downloadFrom(datanode, id):
        # Asking file to datanode
        datanode_s = socket.socket()
        datanode_s.connect(datanode)

        datanode_s.sendall("GET /file HTTP/1.1 200 OK\r\n".encode())
        datanode_s.sendall("id: {}\r\n".format(id).encode())
        datanode_s.sendall("\r\n".encode())

        datanode_response = http_parser.http_parser(datanode_s)
        datanode_header = datanode_response.get_header()

        for chunk in datanode_response.get_file_chunks():
            yield chunk

def deleteFrom(datanode, id):
    # Asking deletion to datanode
    datanode_s = socket.socket()
    datanode_s.connect(datanode)

    datanode_s.sendall("GET /delete HTTP/1.1 200 OK\r\n".encode())
    datanode_s.sendall("id: {}\r\n".format(id).encode())
    datanode_s.sendall("\r\n".encode())

def upload(file_metadata, file_length, file_generator):
    print("Uploading")
    printDictionary(file_metadata)

    # metadata has the format: { name: "Name" }
    id = genId()
    metadata[id] = file_metadata

    replication_factor = 3

    # error handling
    if len(datanode_list) == 0:
        print("ERROR: NO DATANODES CONFIGURED")
    elif len(datanode_list) < replication_factor:
        print("ERROR: NOT ENOUGH DATANODES FOR REPLICATION FACTOR")
        exit(1)

    datanodes = random.sample(datanode_list, replication_factor)
    uploadToMultiple(datanodes, id, file_length, file_generator)
    for datanode in datanodes:
        if not 'datanode_list' in metadata[id]:
            metadata[id]['datanode_list'] = []

        metadata[id]['datanode_list'].append(datanode)

    updateMetadataFile()


    print("Uploaded")

    return id


# returns a generator
def download(id):
    datanode = random.choice(metadata[id]['datanode_list'])
    return downloadFrom(datanode, id)

# deletes file
def delete(id):
    for datanode in metadata[id]['datanode_list']:
        deleteFrom(datanode, id)

    metadata.pop(id)

    updateMetadataFile()

def getLength(id):
    return metadata[id]['size']

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
        if header['url'] == "/metadata":
            id = header['id']
            print("metadata id: ",id)
            metadata_string = pickle.dumps(metadata[id])
            print("metadata_string: ",metadata_string)
            file_length = len(metadata_string)

            conn.sendall("POST /metadata HTTP/1.1 200 OK\r\n".encode())
            conn.sendall("Content-Length: {}\r\n".format(file_length).encode())
            conn.sendall("\r\n".encode())

            conn.sendall(metadata_string)

    if header['method'] == "GET":
        if header['url'] == "/delete":
            id = header['id']
            delete(id)

            conn.sendall("POST /delete HTTP/1.1 200 OK\r\n".encode())
            conn.sendall("\r\n".encode())


    if header['method'] == "POST":
        if header['url'] == "/upload":
            print("File name = ",header['name'])
            file_length = header['Content-Length']
            id = upload({ 'name': header['name'], 'size': header['Content-Length'] }, file_length, request.get_file_chunks())

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
