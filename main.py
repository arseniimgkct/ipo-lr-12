import transport

company = transport.TransportCompany("MyCompany", [], [])

menu = """
1. Создать клиента
2. Создать самолет
3. Создать поезд
4. Вывести всех клиентов
5. Вывести весь транспорт
6. Оптимизировать клиентов и транспорт
7. Выход
"""

def select_action():
    try:
        return int(input("Выберите действие: "))
    except:
        return None


while True:
    print(menu)
    action = select_action()

    if action is None:
        print("Некорректный ввод.")
        continue

    match action:
        case 1:
            name = input("Имя: ")
            weight = float(input("Вес груза: "))
            vip = input("VIP? (y/n): ").lower() == "y"

            client = transport.Client(name, weight, vip)
            company.add_client(client)

            print("Клиент добавлен.")

        case 2:
            capacity = float(input("Вместимость: "))
            altitude = int(input("Макс. высота: "))

            airplane = transport.Airplane(capacity, altitude)
            company.add_vehicle(airplane)

            print("Самолёт добавлен.")

        case 3:
            capacity = float(input("Вместимость: "))
            cars = int(input("Кол-во вагонов: "))

            train = transport.Train(capacity, cars)
            company.add_vehicle(train)

            print("Поезд добавлен.")

        case 4:
            print("\n--- Клиенты ---")
            for c in company.clients:
                print(c)

        case 5:
            print("\n--- Транспорт ---")
            for v in company.vehicles:
                print(v)
                print()

        case 6:
            print("Оптимизация...")
            company.optimize_cargo_distribution()
            print("Грузы распределены.")

        case 7:
            print("Выход.")
            break

        case _:
            print("Некорректное действие.")
