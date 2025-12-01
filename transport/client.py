class Client:
    name = ''
    cargo_weight = 0
    is_vip = False
    
    def __init__(self, name, cargo_weight, is_vip=False):
        if (
            type(name) != str or 
            type(is_vip) != bool or 
            (type(cargo_weight) != float and type(cargo_weight) != int)
        ):
            raise TypeError
        
        if cargo_weight < 0:
            raise ValueError
        

        self.name = name
        self.cargo_weight = cargo_weight
        self.is_vip = is_vip