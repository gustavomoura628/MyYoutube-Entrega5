#distributed database
import uuid
import os
import pickle

# Create or load global variable metadata
# TODO: Currently the way this is handled can cause race conditions
metadata = {}
if os.path.exists("metadata_pickle.pyc"):
    metadata_pickle = open("metadata_pickle.pyc", "rb")
    metadata = pickle.load(metadata_pickle)
    metadata_pickle.close()

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

def printDictionary(dictionary):
    for k,v in dictionary.items():
        print("'{}': {}".format(k, v))
    print()

def idAlreadyExists(id):
    return id in metadata

def genId():
    id = str(uuid.uuid4())
    while idAlreadyExists(id):
        id = str(uuid.uuid4())
    return id

def upload(file_metadata, file_generator):
    # metadata has the format: { name: "Name" }
    id = genId()
    metadata[id] = file_metadata
    updateMetadataFile()

    file = open("files/{}".format(id), "wb")
    for chunk in file_generator:
        file.write(chunk)
    file.close()


# returns a generator
def download(id):
    file = open(id, "rb")
    while True:
        chunk = file.read(2**20)
        if not chunk:
            break
        yield chunk
    file.close()

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
