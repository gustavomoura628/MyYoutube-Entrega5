import rpyc
def connect(service_name):
    service = rpyc.connect_by_service(service_name)
    service._config['sync_request_timeout'] = None
    return service.root
