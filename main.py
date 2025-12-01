import transport

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
        action = int(input("Выберите действие: "))
        return action
    except:
        return 'invalid'

while (True):
    print(menu)
    action = select_action()
    
    if (action == 'invalid'):
        print('Выбрано некорректное действие.')
        continue
    
    match (action):
        # создать клиента
        case 1:
            print("Not Implemented")
        
        # создать самолет
        case 2:
            print("Not Implemented")
            
        # создать поезд
        case 3:
            print("Not Implemented")
            
        # вывести всех клиентов
        case 4:
            print("Not Implemented")
        
        # вывести весь транспорт
        case 5:
            print("Not Implemented")
            
        # оптимизировать клиентов и транспорт
        case 6:
            print("Not Implemented")
            
        # Exit
        case 7:
            print("Заканчиваем работу")
            break