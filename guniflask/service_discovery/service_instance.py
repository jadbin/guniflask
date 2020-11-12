class ServiceInstance:
    def __init__(self, service_id: str = None, host: str = None, port: int = None):
        self.service_id = service_id
        self.host = host
        self.port = port
