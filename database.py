#import rpyc
#datanode = rpyc.connect_by_service("Datanode").root
import rpyc
import rpyc_helper

monitor = rpyc_helper.connect("Monitor")
load_balancer = rpyc_helper.connect("LoadBalancer")

REPLICATION_FACTOR = 3

#distributed database
import uuid
import os
import pickle
import random
import time

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

def add_datanode_to_file_sources(datanode, id):
    # add to metadata variable
    if not 'datanode_list' in metadata[id]:
        metadata[id]['datanode_list'] = []
    metadata[id]['datanode_list'].append(datanode)
    updateMetadataFile()

def upload(file_metadata, file_generator):
    print("Uploading")
    printDictionary(file_metadata)
    size = file_metadata["size"]

    # metadata has the format: { name: "Name" }
    id = genId()
    metadata[id] = file_metadata

    #datanode_list = monitor.list_alive()
    datanodes = load_balancer.get_nodes_to_store(REPLICATION_FACTOR)
    print("Datanodes selected to store file:",datanodes)

    # error handling
    if len(datanodes) == 0:
        print("ERROR: NO DATANODES ALIVE")
        exit(1)
    elif len(datanodes) < REPLICATION_FACTOR:
        print("Not enough datanodes alive, proceeding upload with only {} out of {} nodes".format(len(datanodes),REPLICATION_FACTOR))

    file_descriptors = {}
    for datanode in datanodes:
        print(f'Getting file descriptor to {datanode}')
        datanode_service = rpyc_helper.connect(datanode)
        file_descriptors[datanode] = datanode_service.getWriteFileProxy(id)


    bytes_sent = 0
    for chunk in file_generator:
        bytes_sent += len(chunk)
        print("Uploading file",file_metadata["name"],":",bytes_sent/size*100,"%")
        for datanode in datanodes:
            try:
                if file_descriptors[datanode] == None:
                    continue
                file_descriptors[datanode].write(chunk)
            except Exception as e:
                print("Error when uploading chunk to {}: {}".format(datanode,e))
                file_descriptors[datanode] = None

    for datanode in datanodes:
        try:
            file_descriptors[datanode].close()
            add_datanode_to_file_sources(datanode, id)
        except Exception as e:
            print("Error when trying to close file on {}: {}".format(datanode, e))

    print("Uploaded")
    return id


# returns a generator
def download(id, from_byte=0):
    while True:
        try:
            list = metadata[id]['datanode_list']
            print(f'list of datanodes with file {id} = {list}')
            datanode = load_balancer.get_node_to_retrieve(list)
            print(f'Downloading from {datanode}')
            datanode_service = rpyc_helper.connect(datanode)
            new_byte = 0
            catching_up = True
            for chunk in datanode_service.file(id):
                if catching_up == True:
                    if new_byte == from_byte:
                        catching_up = False
                    else:
                        new_byte += len(chunk)
                if catching_up == False:
                    from_byte += len(chunk)
                    print("Got chunk, current progress =",from_byte,"/",metadata[id]["size"])
                    yield chunk
            break
        except Exception as e:
            print("Failed while downloading file, trying to connect to another node")

# deletes file
def delete(id):
    for datanode in metadata[id]['datanode_list']:
        print(f'Deleting from {datanode}')
        #datanode_ip, datanode_port = datanode.split(":")
        #datanode_service = rpyc.connect(datanode_ip, datanode_port)
        #datanode_service._config['sync_request_timeout'] = None
        #datanode_service = datanode_service.root
        datanode_service = rpyc_helper.connect(datanode)
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

def regenerate():
    print("Initialized regenerate thread")
    while True:
        try:
            print("ALL ONLINE DATANODES:",monitor.list_alive())
            for file_id in metadata:
                all_datanodes = metadata[file_id]['datanode_list']
                print("All datanodes with the file =",all_datanodes)
                datanodes = monitor.aliveFromList(all_datanodes)
                print("Datanodes with the file that are alive =",datanodes)
                if len(datanodes) < REPLICATION_FACTOR:
                    print("File",file_id," has only",len(datanodes),"out of",REPLICATION_FACTOR,"alive")
                    potential_datanodes = load_balancer.get_nodes_to_store(len(all_datanodes)+1)
                    flag_success = False
                    for potential_datanode in potential_datanodes:
                        if len(datanodes) == 0 or len(potential_datanodes) == 0:
                            print("Not enough datanodes alive to transfer file")
                            break

                        if potential_datanode not in datanodes:
                            print("Found potential_datanode to store it:",potential_datanode)
                            try:
                                source_datanode = load_balancer.get_node_to_retrieve(all_datanodes)
                                destination_datanode = potential_datanode

                                source_datanode_service = rpyc_helper.connect(source_datanode)
                                destination_datanode_service = rpyc_helper.connect(destination_datanode)

                                print("TRYING TO DOWNLOAD FROM",source_datanode,"TO",destination_datanode)
                                file_generator = source_datanode_service.file(file_id)

                                file_descriptor = destination_datanode_service.getWriteFileProxy(file_id)

                                size = metadata[file_id]["size"]
                                name = metadata[file_id]["name"]
                                bytes_sent = 0
                                for chunk in file_generator:
                                    bytes_sent += len(chunk)
                                    print("Regenerating file",name,":",bytes_sent/size*100,"%")
                                    file_descriptor.write(chunk)
                                file_descriptor.close()


                                add_datanode_to_file_sources(destination_datanode,file_id)
                                flag_success = True
                                break
                            except Exception as e:
                                print("ERROR: while trying to regenerate file {} to node {}: {}".format(file_id, potential_datanode, e))

                    if flag_success == True:
                        print("Sucessfully replicated",file_id)
                    else:
                        print("Could not replicate",file_id)
                        pass

        except Exception as e:
            print("Regenerate thread failed")

        time.sleep(3)

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

import threading
# Initialize remote object server and register it to name service
if __name__ == "__main__":
    regenerate_thread = threading.Thread(target=regenerate)
    regenerate_thread.start()

    from rpyc.utils.server import ThreadedServer
    print("Initialized database service")
    t = ThreadedServer(DatabaseService, auto_register=True, protocol_config = {"allow_public_attrs" : True})
    t.start()
