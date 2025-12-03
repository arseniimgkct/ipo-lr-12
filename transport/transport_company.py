from .vehicle import Vehicle, CapacityOverloadError
from .client import Client


class TransportCompany:
    def __init__(self, name, vehicles=None, clients=None):
        if not isinstance(name, str):
            raise TypeError("name must be a string")

        if vehicles is not None and not isinstance(vehicles, (list, tuple)):
            raise TypeError("vehicles must be a list or tuple")

        if clients is not None and not isinstance(clients, (list, tuple)):
            raise TypeError("clients must be a list or tuple")

        self.name = name
        self.vehicles = list(vehicles) if vehicles else []
        self.clients = list(clients) if clients else []

    def add_vehicle(self, vehicle):
        if not isinstance(vehicle, Vehicle):
            raise TypeError("vehicle must be instance of Vehicle")

        self.vehicles.append(vehicle)

    def list_vehicles(self):
        return self.vehicles

    def add_client(self, client):
        if not isinstance(client, Client):
            raise TypeError("client must be instance of Client")

        self.clients.append(client)

    def optimize_cargo_distribution(self):
        sorted_clients = sorted(
            self.clients,
            key=lambda c: not c.is_vip
        )

        sorted_vehicles = sorted(
            self.vehicles,
            key=lambda v: v.capacity
        )

        for client in sorted_clients:
            loaded = False

            for vehicle in sorted_vehicles:
                try:
                    vehicle.load_cargo(client)
                    loaded = True
                    break
                except CapacityOverloadError:
                    continue

            if not loaded:
                print(f"Не удалось загрузить клиента {client.name}: груз слишком большой")
