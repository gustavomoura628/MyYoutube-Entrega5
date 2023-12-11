import rpyc
datanode = rpyc.connect_by_service("Datanode").root

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

    #REMOTE SERVICE CALL
    datanode.upload(id, file_generator)

    updateMetadataFile()

    print("Uploaded")

    return id


# returns a generator
def download(id):
    return datanode.file(id)

# deletes file
def delete(id):
    datanode.delete(id)

    metadata.pop(id)

    updateMetadataFile()

def getLength(id):
    return metadata[id]['size']

def getList():
    list = {}
    for k,v in metadata.items():
        print("[{}]: {}".format(k,v))
        list[k] = v['name']
    return list

import rpyc
class DatabaseService(rpyc.Service):
    def on_connect(self, conn):
        pass
    def on_disconnect(self, conn):
        pass

    def exposed_file(self, id):
        print("Downloading {}".format(id))
        return download(id)

    def exposed_list(self):
        print("List")
        return getList()

    def exposed_metadata(self, id):
        print("Metadata {}".format(id))
        return metadata[id]

    def exposed_delete(self, id):
        print("Delete {}".format(id))
        delete(id)

    def exposed_upload(self, name, size, chunk_generator):
        print("Upload {}, {}".format(name, size))
        id = upload({ 'name': name, 'size': size }, chunk_generator)
        return id

# Initialize remote object server and register it to name service
if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(DatabaseService, port=8081, auto_register=True, protocol_config = {"allow_public_attrs" : True})
    t.start()
