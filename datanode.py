#distributed database
import os
import rpyc
import rpyc_helper
import threading
import time


# Handle service name
datanode_name = None

if os.path.exists("datanode_name.txt"):
    print("Datanode Service Name already exists, fetching from disk...")

    datanode_name_file = open("datanode_name.txt", "r")
    datanode_name = datanode_name_file.read()

    datanode_name_file.close()

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

# Connect to monitor service
monitor = rpyc_helper.connect("Monitor")
print("Connected to Monitor service")
monitor.register(datanode_name)


# This class is used to wrap file operations to be able to be passed by rpyc
class FileProxy():
    def __init__(self, path, arg):
        monitor.increment_connections_counter(datanode_name)
        monitor.increment_file_counter(datanode_name)
        self.file_descriptor = open(path, arg)

    def write(self, data):
        self.file_descriptor.write(data)

    def close(self):
        self.file_descriptor.close()
        monitor.decrement_connections_counter(datanode_name)

class DatanodeService(rpyc.Service):
    ALIASES = ["Datanode"]

    # Sends file to requester
    def exposed_file(self, id):
        print("Getting file",id)
        return file(id)

    # Deletes file
    def exposed_delete(self, id):
        print("Deleting",id)
        monitor.decrement_file_counter(datanode_name)
        return delete(id)

    # Writes file to disk
    def exposed_upload(self, id, chunk_generator):
        print("Uploading",id)
        return upload(id, chunk_generator)

    # Returns FileProxy to write file remotely
    def exposed_getWriteFileProxy(self, id):
        print("Getting Write File Proxy {}".format(id))
        return FileProxy("files/{}".format(id), "wb")

# Generator that returns a chunk for each call
def file(id):
    chunk_size = 2**20

    monitor.increment_connections_counter(datanode_name)

    print("Downloading {}".format(id))
    file = open("files/{}".format(id), "rb")

    while True:
        chunk = file.read(chunk_size)
        if not chunk:
            break
        yield chunk
    file.close()

    monitor.decrement_connections_counter(datanode_name)

# C'mon surely you can guess what this one does
def delete(id):
    print("Removing", id)
    os.remove("files/{}".format(id))

def upload(id, chunk_generator):
    monitor.increment_connections_counter(datanode_name)

    print("Uploading", id)
    file = open("files/{}".format(id), "wb")

    for chunk in chunk_generator:
        file.write(chunk)
    file.close()

    monitor.decrement_connections_counter(datanode_name)

    return id



# Thread that alerts Monitor Service that this node is still alive
def periodicallyPingMonitor():
    period_between_pings = 0.1

    while True:
        monitor.ping(datanode_name)
        time.sleep(period_between_pings)


# Initialize remote object server and register it to name service
if __name__ == "__main__":
    # Start pinging thread
    periodicallyPingMonitorThread = threading.Thread(target=periodicallyPingMonitor)
    periodicallyPingMonitorThread.start()

    # Set alias to datanode_name
    DatanodeService.ALIASES = ["Datanode", datanode_name]

    # Start rpyc service
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(DatanodeService, auto_register=True, protocol_config = {"allow_public_attrs" : True})
    t.start()
