#distributed database
import os
import uuid
import pickle

name_service_data = {}
name_service_file = "name_service_data.pyc"
if os.path.exists(name_service_file):
    name_service_data_pickle = open(name_service_file, "rb")
    name_service_data = pickle.load(name_service_data_pickle)
    name_service_data_pickle.close()

def idAlreadyExists(id):
    return id in name_service_data

def genId():
    id = "NAMESERVICE_"+str(uuid.uuid4())
    while idAlreadyExists(id):
        id = str(uuid.uuid4())
    return id


def updateDataFile():
    name_service_data_pickle = open(name_service_file, "wb")
    pickle.dump(name_service_data, name_service_data_pickle)
    name_service_data_pickle.close()

import rpyc
class NameServiceService(rpyc.Service):
    def on_connect(self, conn):
        pass

    def on_disconnect(self, conn):
        pass

    # Registers Node for monitoring
    def exposed_get_name(self):
        name = genId()
        name_service_data[name] = True
        updateDataFile()
        return name

if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(NameServiceService, auto_register=True, protocol_config = {"allow_public_attrs" : True})
    ThreadedServer(NameServiceService, auto_register=True, protocol_config = {"allow_public_attrs" : True})
    t.start()
