#import rpyc
#datanode = rpyc.connect_by_service("Datanode").root
import rpyc
import rpyc_helper

monitor = rpyc_helper.connect("Monitor")
load_balancer = rpyc_helper.connect("LoadBalancer")

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
    id = "FILE_"+str(uuid.uuid4())
    while idAlreadyExists(id):
        id = str(uuid.uuid4())
    return id


def upload(file_metadata, file_generator):
    print("Uploading")
    printDictionary(file_metadata)

    # metadata has the format: { name: "Name" }
    id = genId()
    metadata[id] = file_metadata

    replication_factor = 1
    #datanode_list = monitor.list_alive()
    datanode_list = load_balancer.get_nodes_to_store(replication_factor)
    
    # error handling
    if len(datanode_list) == 0:
        print("ERROR: NO DATANODES ALIVE")
    elif len(datanode_list) < replication_factor:
        print("ERROR: NOT ENOUGH DATANODES ALIVE FOR REPLICATION FACTOR")
        exit(1)

    #datanodes = random.sample(datanode_list, replication_factor)
    datanodes = datanode_list
    print("Datanodes list = ",datanodes)
    file_descriptors = []
    for datanode in datanodes:
        print(f'Uploading from {datanode}')
        #REMOTE SERVICE CALL
        datanode_ip, datanode_port = datanode.split(":")
        datanode_service = rpyc.connect(datanode_ip, datanode_port)
        datanode_service._config['sync_request_timeout'] = None
        datanode_service = datanode_service.root
        file_descriptors.append(datanode_service.getWriteFileProxy(id))

        ##TODO: THIS BREAKS EVERYTHING
        #datanode_service.upload(id, file_generator)

        if not 'datanode_list' in metadata[id]:
            metadata[id]['datanode_list'] = []
        metadata[id]['datanode_list'].append(datanode)

    for chunk in file_generator:
        for file in file_descriptors:
            file.write(chunk)

    for file in file_descriptors:
        file.close()

    updateMetadataFile()
    print("Uploaded")
    return id


# returns a generator
def download(id):
    list = metadata[id]['datanode_list']
    print(f'list = {list}')
    datanode = load_balancer.get_node_to_retrieve(list)
    #aliveList = monitor.aliveFromList(list)
    #print(f'alivelist = {aliveList}')
    #datanode = random.choice(aliveList)
    print(f'Downloading from {datanode}')
    datanode_ip, datanode_port = datanode.split(":")
    datanode_service = rpyc.connect(datanode_ip, datanode_port)
    datanode_service._config['sync_request_timeout'] = None
    datanode_service = datanode_service.root
    return datanode_service.file(id)

# deletes file
def delete(id):
    for datanode in metadata[id]['datanode_list']:
        print(f'Deleting from {datanode}')
        datanode_ip, datanode_port = datanode.split(":")
        datanode_service = rpyc.connect(datanode_ip, datanode_port)
        datanode_service._config['sync_request_timeout'] = None
        datanode_service = datanode_service.root
        datanode_service.delete(id)

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
    t = ThreadedServer(DatabaseService, auto_register=True, protocol_config = {"allow_public_attrs" : True})
    t.start()
