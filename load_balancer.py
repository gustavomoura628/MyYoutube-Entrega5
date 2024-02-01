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
        sorted_nodes = sorted(hosts_data.keys(), key=lambda x: hosts_data[x]['number_of_files'])
        selected_nodes = sorted_nodes[:number_of_nodes]
        print("Selected nodes:",selected_nodes)
        return selected_nodes

    def exposed_get_node_to_retrieve(self, nodes_with_file):
        print("Getting node to retrieve file from nodes:",nodes_with_file)
        hosts_data = monitor.get_host_data_alive()
        sorted_nodes = sorted(hosts_data.keys(), key=lambda x: hosts_data[x]['number_of_connections'])
        for node in sorted_nodes:
            if node in nodes_with_file:
                print("Returning node",node)
                return node

# Initialize remote object server and register it to name service
if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(LoadBalancerService, auto_register=True, protocol_config = {"allow_public_attrs" : True})
    t.start()
