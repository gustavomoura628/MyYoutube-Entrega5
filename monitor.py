#distributed database
import os


import pickle
hosts_data = {}
if os.path.exists("monitordata_pickle.pyc"):
    monitordata_pickle = open("monitordata_pickle.pyc", "rb")
    hosts_data = pickle.load(monitordata_pickle)
    monitordata_pickle.close()



def updateMonitordataFile():
    monitordata_pickle = open("monitordata_pickle.pyc", "wb")
    pickle.dump(hosts_data, monitordata_pickle)
    monitordata_pickle.close()

import rpyc
class MonitorService(rpyc.Service):
    def on_connect(self, conn):
        pass

    def on_disconnect(self, conn):
        pass

    # Registers Node for monitoring
    def exposed_register(self, client_name):
        register(client_name)
        print("Registered client",client_name)

    # Alerts monitoring service that the Node is still alive
    def exposed_ping(self, client_name):
        ping(client_name)
        print(client_name,"has pinged")
    
    # List of all Nodes currently alive
    def exposed_list_alive(self):
        print("List alive")
        return list_alive()

    def exposed_get_host_data_alive(self):
        print("Host data alive")
        return get_host_data_alive()

    # Checks if Node is alive
    def exposed_isAlive(self, client_name):
        print("isAlive",client_name)
        return isAlive(client_name)

    # Receives a list of Nodes and returns its subset of all Nodes alive
    def exposed_aliveFromList(self, list):
        print("AliveFromList",list)
        return aliveFromList(list)

    def exposed_increment_file_counter(self, client_name):
        print("increment file",client_name)
        increment_file_counter(client_name)

    def exposed_decrement_file_counter(self, client_name):
        print("decrement file",client_name)
        decrement_file_counter(client_name)

    def exposed_increment_connections_counter(self, client_name):
        print("increment connections",client_name)
        increment_connections_counter(client_name)

    def exposed_decrement_connections_counter(self, client_name):
        print("decrement connections",client_name)
        decrement_connections_counter(client_name)


import datetime


def increment_file_counter(client_name):
    hosts_data[client_name]["number_of_files"] += 1
    print("increment_file_counter",client_name,"number_of_files =",hosts_data[client_name]["number_of_files"])

def decrement_file_counter(client_name):
    hosts_data[client_name]["number_of_files"] -= 1
    print("decrement_file_counter",client_name,"number_of_files =",hosts_data[client_name]["number_of_files"])


def increment_connections_counter(client_name):
    hosts_data[client_name]["number_of_connections"] += 1
    print("increment_connections_counter",client_name,"number_of_connections =",hosts_data[client_name]["number_of_connections"])

def decrement_connections_counter(client_name):
    hosts_data[client_name]["number_of_connections"] -= 1
    print("decrement_connections_counter",client_name,"number_of_connections =",hosts_data[client_name]["number_of_connections"])

def register(client_name):
    print("Registering {}".format(client_name))
    hosts_data[client_name] = {}
    hosts_data[client_name]["number_of_files"] = 0
    hosts_data[client_name]["number_of_connections"] = 0
    hosts_data[client_name]["ping"] = datetime.datetime.now()

def ping(client_name):
    if client_name not in hosts_data:
        print("ERROR: ADDRESS {} NOT REGISTERED".format(client_name))
        return -1

    print("Address Ping = {}".format(client_name))

    lasttime = hosts_data[client_name]["ping"]
    print("Last Ping Time= {}".format(lasttime))

    hosts_data[client_name]["ping"] = datetime.datetime.now()
    print("Current Time = {}".format(hosts_data[client_name]["ping"]))

    diff = hosts_data[client_name]["ping"] - lasttime
    print("Diff = {}".format(diff))

def isAlive(client_name):
    if datetime.datetime.now() - hosts_data[client_name]["ping"] < datetime.timedelta(seconds=0.2):
        return True
    return False

def list_alive():
    list = []
    for client_name in hosts_data:
        if isAlive(client_name):
            list += [client_name]
    return list

def get_host_data_alive():
    alive_hosts = {}
    for client_name in hosts_data:
        if isAlive(client_name):
            alive_hosts[client_name] = hosts_data[client_name]
    return alive_hosts

def aliveFromList(list):
    print(f'list = {list}')
    result_list = []
    for client_name in list:
        if isAlive(client_name):
            result_list += [client_name]
    print(f'alive = {result_list}')
    return result_list

# Initialize remote object server and register it to name service
if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(MonitorService, auto_register=True, protocol_config = {"allow_public_attrs" : True})
    ThreadedServer(MonitorService, auto_register=True, protocol_config = {"allow_public_attrs" : True})
    t.start()
