#distributed database
import os

import rpyc
monitor = rpyc.connect_by_service("monitor")
monitor._config['sync_request_timeout'] = None
monitor = monitor.root

class LoadBalancerService(rpyc.Service):
    def on_connect(self, conn):
        pass

    def on_disconnect(self, conn):
        pass

    def exposed_get_nodes_to_store(self, number_of_nodes):
        print("Getting nodes to store")
        hosts_data = monitor.get_host_data_alive()
        print("Alive hosts = ",hosts_data)
        sorted_addresses = sorted(hosts_data.keys(), key=lambda x: hosts_data[x]['number_of_files'])
        return sorted_addresses[:number_of_nodes]

    def exposed_get_node_to_retrieve(self, nodes_with_file):
        hosts_data = monitor.get_host_data_alive()
        sorted_addresses = sorted(hosts_data.keys(), key=lambda x: hosts_data[x]['number_of_connections'])
        for address in sorted_addresses:
            if address in nodes_with_file:
                return address

# Initialize remote object server and register it to name service
if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(LoadBalancerService, auto_register=True, protocol_config = {"allow_public_attrs" : True})
    t.start()
