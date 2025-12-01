from .vehicle import Vehicle

class Airplane(Vehicle):
    max_altitude = 0
    
    def __init__(self, capacity, clients_list, max_altitude, current_load=0):
        super().__init__(capacity, clients_list, current_load)
        
        if type(max_altitude) != int:
            raise TypeError
        
        if max_altitude < 0:
            raise ValueError
        
        self.max_altitude = max_altitude