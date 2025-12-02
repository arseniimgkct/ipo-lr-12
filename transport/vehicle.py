import uuid
from .client import Client


class CapacityOverloadError(Exception):
    pass


class Vehicle:
    def __init__(self, capacity, clients_list=None, current_load=0):

        if not isinstance(capacity, (int, float)):
            raise TypeError("capacity must be number")

        if clients_list is not None and not isinstance(clients_list, (list, tuple)):
            raise TypeError("clients_list must be list or tuple")

        if not isinstance(current_load, (int, float)):
            raise TypeError("current_load must be number")

        if capacity < 0 or current_load < 0:
            raise ValueError("capacity and current_load must be >= 0")

        self.vehicle_id = uuid.uuid4()
        self.capacity = capacity
        self.clients_list = list(clients_list) if clients_list else []
        self.current_load = current_load

    def load_cargo(self, client):
        if not isinstance(client, Client):
            raise TypeError("client must be instance of Client")

        if client.cargo_weight < 0:
            raise ValueError("cargo_weight must be >= 0")

        if client.cargo_weight + self.current_load > self.capacity:
            raise CapacityOverloadError(
                f"capacity={self.capacity}, load={self.current_load}, cargo={client.cargo_weight}"
            )

        self.current_load += client.cargo_weight
        self.clients_list.append(client)

    def __str__(self):
        return (
            f"ID: {self.vehicle_id}\n"
            f"Capacity: {self.capacity}\n"
            f"Current load: {self.current_load}\n"
            f"Clients: {[c.name for c in self.clients_list]}"
        )
