import uuid
from .client import Client

class CapacityOverloadError(Exception):
    def __init__(self, message):
        self.message = message

class Vehicle:
    vehicle_id = ''
    capacity = 0
    current_load = 0
    clients_list = []
    
    def __init__(self, capacity, clients_list, current_load=0):
        
        if (
            type(capacity) != int and type(capacity) != float or
            type(clients_list) != list and type(clients_list) != tuple or
            type(current_load) != int and type(current_load) != float
            ):
            raise TypeError
        
        if capacity < 0 or current_load < 0:
            raise ValueError
        
        self.vehicle_id = uuid.uuid5()
        self.capacity = capacity
        self.clients_list = clients_list
        self.current_load = current_load
        
    def load_cargo(self, client):
        if (
            type(client) != Client or 
            type(client.cargo_weight) != int or 
            type(client.is_vip) != bool or
            type(client.name) != str
        ):
            raise TypeError
        
        if client.cargo_weight < 0:
            raise ValueError
        
        if client.cargo_weight + self.current_load > self.capacity:
            raise CapacityOverloadError(f'Capacity: {self.capacity}\nCurrent load: {self.current_load}\n Client cargo: {client.cargo_weight}, ')

        self.current_load += client.cargo_weight
        self.clients_list.append({
            "name": client.name,
            "is_vip": client.is_vip
        })
    
    def __str__(self):
        return f'ID: {self.vehicle_id}\nCapacity: {self.capacity}\nCurrent load: {self.current_load}'