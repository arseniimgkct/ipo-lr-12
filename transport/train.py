from .vehicle import Vehicle

class Train(Vehicle):
    def __init__(self, capacity, number_of_cars, clients_list=None, current_load=0):
        super().__init__(capacity, clients_list, current_load)

        if not isinstance(number_of_cars, int):
            raise TypeError("number_of_cars must be int")

        if number_of_cars < 0:
            raise ValueError("number_of_cars must be >= 0")

        self.number_of_cars = number_of_cars

    def __str__(self):
        base = super().__str__()
        return base + f"\nCars: {self.number_of_cars}"
