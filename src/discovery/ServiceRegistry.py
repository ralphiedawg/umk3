import socket
import json
from zeroconf import ServiceBrowser, ServiceInfo, Zeroconf, ServiceListener

class ServiceRegistry():
    def __init__(self, 
                 identifier: str = '_umk._tcp.local.', 
                 port: int = 2022,
                 name: str = 'UMK-server'
                 ):
        self.zc = Zeroconf()
        self.identifier = identifier
        self.port = port
        self.name = f'{name}.{identifier}'

        host = socket.gethostname()
        local_ip = socket.gethostbyname(host)

        self.info = ServiceInfo(
            type_= self.identifier,
            name = self.name,
            addresses = [socket.inet_aton(local_ip)],
            port = self.port,
            server = f'{host}.local.'
        )
        
    def register(self):
        print(f'Registering service {self.name} on {self.port}')
        self.zc.register_service(self.info)

    def unregister(self):
        print('Unregistering')
        self.zc.unregister_service(self.info)
        self.zc.close()

class Listener(ServiceListener):
    def add_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        info = zc.get_service_info(type_, name) 
        if not info:
            return

        data = {
            'serviceName': name,
            'addresses': info.parsed_addresses(),
            'port': info.port
        }
        
        print(json.dumps(data))

        with open('known_services.json', 'w') as file:
            json.dump(data, file, indent = 4)


    def update_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        return super().update_service(zc, type_, name)

    def remove_service(self, zc: Zeroconf, type_: str, name: str) -> None:
        return super().remove_service(zc, type_, name)

if __name__ == "__main__":
    mode = input("Mode: ")
    if mode == 'server':
       registry = ServiceRegistry()
       registry.register()
       try:
            input("Service is live. Press Enter to stop...\n")
       finally:
            registry.unregister()
    elif mode == 'client':
        zc = Zeroconf()
        listener = Listener()
        browser = ServiceBrowser(zc, '_umk._tcp.local.', listener)
        try:
            input("Browsing for services... Press Enter to stop.\n")
        finally:
            zc.close()

