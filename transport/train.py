from .vehicle import Vehicle

class Train(Vehicle):
    number_of_cars = 0
    
    def __init__(self, capacity, clients_list, number_of_cars, current_load=0):
        super().__init__(capacity, clients_list, current_load)
        if type(number_of_cars) != int:
            raise TypeError
        
        if number_of_cars < 0:
            raise ValueError
        
        self.number_of_cars = number_of_cars