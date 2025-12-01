from .vehicle import Vehicle
from .client import Client


class TransportCompany:
    name = ''
    vehicles = []
    clients = []
    
    def __init__(self, name, vehicles, clients):
        if (
            type(name) != str or 
            type(vehicles) != list and type(vehicles) != tuple or
            type(clients) != list and type(clients) != tuple 
        ):
            raise TypeError
        
        self.name = name
        self.vehicles = vehicles
        self.clients = clients
        
    def add_vehicles(self, vehicle):
        if type(vehicle) != Vehicle:
            raise TypeError
        
        self.vehicles.append(vehicle)
        
    def list_vehicles(self):
        return self.vehicles
    
    def add_client(self, client):
        if type(client) != Client:
            raise TypeError
        
        self.clients.append(client)
        
    def optimize_cargo_distibution(self):
        self.clients.sort(key=lambda u: u.is_vip)
        self.vehicles.sort(key=lambda v: v.capacity)
    
    