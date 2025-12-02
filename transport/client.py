class Client:
    def __init__(self, name, cargo_weight, is_vip=False):
        if not isinstance(name, str):
            raise TypeError("name must be string")

        if not isinstance(is_vip, bool):
            raise TypeError("is_vip must be bool")

        if not isinstance(cargo_weight, (int, float)):
            raise TypeError("cargo_weight must be number")

        if cargo_weight < 0:
            raise ValueError("cargo_weight must be >= 0")

        self.name = name
        self.cargo_weight = cargo_weight
        self.is_vip = is_vip

    def __str__(self):
        return f"{self.name} | cargo: {self.cargo_weight} | VIP: {self.is_vip}"
