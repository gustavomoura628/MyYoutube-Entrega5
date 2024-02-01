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
    ALIASES = ["monitor"]

    def on_connect(self, conn):
        addr, port = conn._channel.stream.sock.getpeername()
        self.addr = addr
        self.port = port
        self.client_service_port = None
        print("Address = ",addr," Port = ", port)

    def on_disconnect(self, conn):
        pass

    # Registers Node for monitoring
    def exposed_register(self, clientServicePort):
        register(self.addr, clientServicePort)
        print("Address = ",self.addr," Port = ", clientServicePort)

    # Alerts monitoring service that the Node is still alive
    def exposed_ping(self, clientServicePort):
        ping(self.addr, clientServicePort)
        print("Address = ",self.addr," Port = ", clientServicePort)
    
    # List of all Nodes currently alive
    def exposed_list_alive(self):
        return list_alive()

    def exposed_get_host_data_alive(self):
        return get_host_data_alive()

    # Checks if Node is alive
    def exposed_isAlive(self, address):
        return isAlive(address)

    # Receives a list of Nodes and returns its subset of all Nodes alive
    def exposed_aliveFromList(self, list):
        return aliveFromList(list)

    def exposed_increment_file_counter(self, clientServicePort):
        increment_file_counter(self.addr, clientServicePort)

    def exposed_decrement_file_counter(self, clientServicePort):
        decrement_file_counter(self.addr, clientServicePort)

    def exposed_increment_connections_counter(self, clientServicePort):
        increment_connections_counter(self.addr, clientServicePort)

    def exposed_decrement_connections_counter(self, clientServicePort):
        decrement_connections_counter(self.addr, clientServicePort)


import datetime


def increment_file_counter(ip, port):
    address = str(ip)+":"+str(port)
    hosts_data[address]["number_of_files"] += 1
    print("increment_file_counter",address,"number_of_files =",hosts_data[address]["number_of_files"])

def decrement_file_counter(ip, port):
    address = str(ip)+":"+str(port)
    hosts_data[address]["number_of_files"] -= 1
    print("decrement_file_counter",address,"number_of_files =",hosts_data[address]["number_of_files"])


def increment_connections_counter(ip, port):
    address = str(ip)+":"+str(port)
    hosts_data[address]["number_of_connections"] += 1
    print("increment_connections_counter",address,"number_of_connections =",hosts_data[address]["number_of_connections"])

def decrement_connections_counter(ip, port):
    address = str(ip)+":"+str(port)
    hosts_data[address]["number_of_connections"] -= 1
    print("decrement_connections_counter",address,"number_of_connections =",hosts_data[address]["number_of_connections"])

def register(ip, port):
    address = str(ip)+":"+str(port)
    print("Registering {}".format(address))
    hosts_data[address] = {}
    hosts_data[address]["number_of_files"] = 0
    hosts_data[address]["number_of_connections"] = 0
    hosts_data[address]["ping"] = datetime.datetime.now()

def ping(ip, port):
    address = str(ip)+":"+str(port)
    if address not in hosts_data:
        print("ERROR: ADDRESS {} NOT REGISTERED".format(address))
        return -1

    print("Address Ping = {}".format(address))

    lasttime = hosts_data[address]["ping"]
    print("Last Ping Time= {}".format(lasttime))

    hosts_data[address]["ping"] = datetime.datetime.now()
    print("Current Time = {}".format(hosts_data[address]["ping"]))

    diff = hosts_data[address]["ping"] - lasttime
    print("Diff = {}".format(diff))

def isAlive(address):
    if datetime.datetime.now() - hosts_data[address]["ping"] < datetime.timedelta(seconds=10):
        return True
    return False

def list_alive():
    list = []
    for address in hosts_data:
        if isAlive(address):
            list += [address]
    return list

def get_host_data_alive():
    alive_hosts = {}
    for address in hosts_data:
        if isAlive(address):
            alive_hosts[address] = hosts_data[address]
    return alive_hosts

def aliveFromList(list):
    print(f'list = {list}')
    result_list = []
    for address in list:
        if isAlive(address):
            result_list += [address]
    print(f'alive = {result_list}')
    return result_list

# Initialize remote object server and register it to name service
if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    MonitorService.ALIASES = ["monitor", "potato"]
    print("aliases = ",MonitorService.ALIASES)
    t = ThreadedServer(MonitorService, auto_register=True, protocol_config = {"allow_public_attrs" : True})
    ThreadedServer(MonitorService, auto_register=True, protocol_config = {"allow_public_attrs" : True})
    t.start()
