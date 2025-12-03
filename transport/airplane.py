from .vehicle import Vehicle

class Airplane(Vehicle):
    def __init__(self, capacity, max_altitude, clients_list=None, current_load=0):
        super().__init__(capacity, clients_list, current_load)

        if not isinstance(max_altitude, int):
            raise TypeError("max_altitude must be int")

        if max_altitude <= 0:
            raise ValueError("max_altitude must be positive")

        self.max_altitude = max_altitude

    def __str__(self):
        base = super().__str__()
        return base + f"\nMax altitude: {self.max_altitude}"
