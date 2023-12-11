#distributed database
import os

# Assert that the folder files exists
if os.path.isdir("files"):
    pass
elif os.path.exists("files"):
    print("ERROR: 'files' FOLDER COULD NOT BE CREATED BECAUSE A FILE EXISTS WITH THE SAME NAME")
    exit(1)
else:
    os.makedirs("files")

import rpyc
class DatanodeService(rpyc.Service):
    def on_connect(self, conn):
        pass
    def on_disconnect(self, conn):
        pass

    def exposed_file(self, id):
        return file(id)

    def exposed_delete(self, id):
        return delete(id)

    def exposed_upload(self, id, chunk_generator):
        return upload(id, chunk_generator)

def file(id):
    print("Downloading {}".format(id))
    file = open("files/{}".format(id), "rb")
    while True:
        chunk = file.read(2**20)
        if not chunk:
            break
        yield chunk
    file.close()

def delete(id):
    print("Removing {}".format(id))
    os.remove("files/{}".format(id))

def upload(id, chunk_generator):
    print("Uploading {}".format(id))

    file = open("files/{}".format(id), "wb")
    for chunk in chunk_generator:
        file.write(chunk)
    file.close()

    return id

# Initialize remote object server and register it to name service
if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(DatanodeService, port=8090, auto_register=True)
    t.start()
