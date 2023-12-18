#distributed database
import os

import rpyc
class MonitorService(rpyc.Service):
    def on_connect(self, conn):
        addr, port = conn._channel.stream.sock.getpeername()
        self.addr = addr
        self.port = port
        print("Address = ",addr," Port = ", port)

    def on_disconnect(self, conn):
        pass

    def exposed_register(self, clientServicePort):
        register(self.addr, clientServicePort)
        print("Address = ",self.addr," Port = ", clientServicePort)

    def exposed_ping(self, clientServicePort):
        ping(self.addr, clientServicePort)
        print("Address = ",self.addr," Port = ", clientServicePort)
    
    def exposed_list(self):
        return list()

    def exposed_isAlive(self, address):
        return isAlive(address)
    def exposed_aliveFromList(self, list):
        return aliveFromList(list)

hosts_data = {}

import datetime


def register(ip, port):
    address = str(ip)+":"+str(port)
    print("Registering {}".format(address))
    hosts_data[address] = datetime.datetime.now()

def ping(ip, port):
    address = str(ip)+":"+str(port)
    if address not in hosts_data:
        print("ERROR: ADDRESS {} NOT REGISTERED".format(address))
        return -1

    print("Address Ping = {}".format(address))

    lasttime = hosts_data[address]
    print("Last Ping Time= {}".format(lasttime))

    hosts_data[address] = datetime.datetime.now()
    print("Current Time = {}".format(hosts_data[address]))

    diff = hosts_data[address] - lasttime
    print("Diff = {}".format(diff))

def isAlive(address):
    if datetime.datetime.now() - hosts_data[address] < datetime.timedelta(seconds=10):
        return True
    return False

def list():
    list = []
    for address in hosts_data:
        if isAlive(address):
            list += [address]
    return list

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
    t = ThreadedServer(MonitorService, port=8082, auto_register=True, protocol_config = {"allow_public_attrs" : True})
    t.start()
