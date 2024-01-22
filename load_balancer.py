#distributed database
import os

import rpyc
class LoadBalancerService(rpyc.Service):
    def on_connect(self, conn):
        pass

    def on_disconnect(self, conn):
        pass

    def exposed_(self):
        pass

# Initialize remote object server and register it to name service
if __name__ == "__main__":
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(LoadBalancerService, port=8083, auto_register=True, protocol_config = {"allow_public_attrs" : True})
    t.start()
