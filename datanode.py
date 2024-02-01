#distributed database
import os
import rpyc
import rpyc_helper

datanode_name = None
if os.path.exists("datanode_name.txt"):
    print("Datanode Service Name already exists, fetching from disk...")
    datanode_name_file = open("datanode_name.txt", "r")
    datanode_name = datanode_name_file.read()
    datanode_name_file.close()
    print("Datanode Service Name =",datanode_name)
else:
    print("Datanode Service Name does not exist, fetching from NameService...")
    name_service = rpyc_helper.connect("NameService")
    datanode_name = name_service.get_name()
    datanode_name_file = open("datanode_name.txt", "w")
    datanode_name_file.write(datanode_name)
    datanode_name_file.close()
    print("Datanode Service Name =",datanode_name)


# Assert that the folder files exists
if os.path.isdir("files"):
    print("Folder 'files' has been created already")
    pass
elif os.path.exists("files"):
    print("ERROR: 'files' FOLDER COULD NOT BE CREATED BECAUSE A FILE EXISTS WITH THE SAME NAME")
    exit(1)
else:
    os.makedirs("files")
    print("Folder 'files' did not exist, but has been created")

import rpyc
import rpyc_helper
monitor = rpyc_helper.connect("Monitor")
print("Connected to Monitor service")

monitor.register(datanode_name)

class FileProxy():
    def __init__(self, path, arg):
        monitor.increment_connections_counter(datanode_name)
        monitor.increment_file_counter(datanode_name)
        self.file_descriptor = open(path, arg)
    def write(self, data):
        self.file_descriptor.write(data)
    def close(self):
        # Gambiarra
        monitor.decrement_connections_counter(datanode_name)
        self.file_descriptor.close()

class DatanodeService(rpyc.Service):
    ALIASES = ["Datanode"]
    def on_connect(self, conn):
        pass
    def on_disconnect(self, conn):
        pass

    def exposed_file(self, id):
        return file(id)

    def exposed_delete(self, id):
        monitor.decrement_file_counter(datanode_name)
        return delete(id)

    def exposed_upload(self, id, chunk_generator):
        return upload(id, chunk_generator)

    def exposed_getWriteFileProxy(self, id):
        print("Getting Write File Proxy {}".format(id))
        return FileProxy("files/{}".format(id), "wb")

def file(id):
    monitor.increment_connections_counter(datanode_name)
    print("Downloading {}".format(id))
    file = open("files/{}".format(id), "rb")
    while True:
        chunk = file.read(2**20)
        if not chunk:
            break
        yield chunk
    file.close()
    monitor.decrement_connections_counter(datanode_name)

def delete(id):
    print("Removing {}".format(id))
    os.remove("files/{}".format(id))

def upload(id, chunk_generator):
    monitor.increment_connections_counter(datanode_name)
    print("Uploading {}".format(id))

    file = open("files/{}".format(id), "wb")
    for chunk in chunk_generator:
        file.write(chunk)
    file.close()

    monitor.decrement_connections_counter(datanode_name)
    return id


import threading
import time

def periodicallyPingMonitor():
    while True:
        monitor.ping(datanode_name)
        time.sleep(7)


# Initialize remote object server and register it to name service
if __name__ == "__main__":
    periodicallyPingMonitorThread = threading.Thread(target=periodicallyPingMonitor)
    periodicallyPingMonitorThread.start()

    from rpyc.utils.server import ThreadedServer

    DatanodeService.ALIASES = ["Datanode", datanode_name]

    t = ThreadedServer(DatanodeService, auto_register=True, protocol_config = {"allow_public_attrs" : True})
    t.start()
