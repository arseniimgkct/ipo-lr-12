"""
transport_gui.py

Tkinter GUI for the provided transport CLI application.

How to use:
- Place this file in the same folder as your `transport` package (client.py, train.py, airplane.py, vehicle.py, transport_company.py).
- Run: python transport_gui.py

Features implemented (per requirements):
- Main window with menu (Export result, About), control panel, two tables (clients, vehicles), status bar.
- Add / Edit / Delete client and vehicle via dialogs with validation.
- Double-click to edit an item.
- Distribute cargo (calls company.optimize_cargo_distribution()) and shows results in a modal.
- Save/Load company state (JSON).
- Export distribution results to JSON/CSV.
- Tooltips, keyboard shortcuts (Enter=save in dialog, Esc=cancel), column sorting.

Notes / placeholders:
- About dialog shows placeholders for lab number, variant and developer name. Edit as needed.
"""

import json
import csv
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from functools import partial
import re
import os

from transport.transport_company import TransportCompany
from transport.client import Client
from transport.train import Train
from transport.airplane import Airplane
from transport.vehicle import Vehicle, CapacityOverloadError


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, _=None):
        if self.tip:
            return
        x, y, cx, cy = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0,0,0,0)
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 20
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        label = tk.Label(self.tip, text=self.text, justify='left', background="#ffffe0", relief='solid', borderwidth=1)
        label.pack()
        self.tip.wm_geometry(f"+{x}+{y}")

    def hide(self, _=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None


def validate_name(name: str) -> bool:
    if not isinstance(name, str):
        return False
    name = name.strip()
    if len(name) < 2:
        return False
    if not re.match(r'^[A-Za-zА-Яа-яЁё\-\s]+$', name):
        return False
    return True


def validate_weight(w: str) -> tuple[bool, float]:
    try:
        val = float(w)
    except Exception:
        return False, 0.0
    if val <= 0 or val > 10000:
        return False, val
    return True, val


def validate_capacity(c: str) -> tuple[bool, float]:
    try:
        val = float(c)
    except Exception:
        return False, 0.0
    if val < 0:
        return False, val
    return True, val


class ClientDialog(tk.Toplevel):
    def __init__(self, parent, title="Добавить клиента", client: Client=None):
        super().__init__(parent)
        self.parent = parent
        self.client = client
        self.result = None
        self.title(title)
        self.resizable(False, False)
        self.grab_set()

        tk.Label(self, text="Имя клиента:").grid(row=0, column=0, sticky='e', padx=6, pady=6)
        self.name_var = tk.StringVar(value=getattr(client, 'name', ''))
        self.name_entry = tk.Entry(self, textvariable=self.name_var)
        self.name_entry.grid(row=0, column=1, padx=6, pady=6)

        tk.Label(self, text="Вес груза (кг):").grid(row=1, column=0, sticky='e', padx=6, pady=6)
        self.weight_var = tk.StringVar(value=str(getattr(client, 'cargo_weight', '')))
        self.weight_entry = tk.Entry(self, textvariable=self.weight_var)
        self.weight_entry.grid(row=1, column=1, padx=6, pady=6)

        self.vip_var = tk.BooleanVar(value=getattr(client, 'is_vip', False))
        self.vip_check = tk.Checkbutton(self, text="VIP", variable=self.vip_var)
        self.vip_check.grid(row=2, column=1, sticky='w', padx=6, pady=6)

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=(0,6))

        save_btn = tk.Button(btn_frame, text="Сохранить", command=self.on_save)
        save_btn.pack(side='left', padx=6)
        cancel_btn = tk.Button(btn_frame, text="Отмена", command=self.on_cancel)
        cancel_btn.pack(side='left')

        ToolTip(save_btn, 'Сохранить клиента (Enter)')
        ToolTip(cancel_btn, 'Отмена (Esc)')

        self.bind('<Return>', lambda e: self.on_save())
        self.bind('<Escape>', lambda e: self.on_cancel())

        self.name_entry.focus()

    def on_save(self):
        name = self.name_var.get().strip()
        ok_name = validate_name(name)
        if not ok_name:
            messagebox.showwarning("Неверное имя", "Имя обязательно: только буквы и минимум 2 символа.")
            self.name_var.set('')
            return

        ok_weight, weight = validate_weight(self.weight_var.get())
        if not ok_weight:
            messagebox.showwarning("Неверный вес", "Вес должен быть положительным числом не более 10000 кг.")
            self.weight_var.set('')
            return

        vip = self.vip_var.get()
        self.result = Client(name, weight, vip)
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()


class VehicleDialog(tk.Toplevel):
    def __init__(self, parent, title='Добавить транспорт', vehicle: Vehicle=None):
        super().__init__(parent)
        self.parent = parent
        self.vehicle = vehicle
        self.result = None
        self.title(title)
        self.resizable(False, False)
        self.grab_set()

        tk.Label(self, text="Тип транспорта:").grid(row=0, column=0, sticky='e', padx=6, pady=6)
        self.type_var = tk.StringVar(value='Train' if isinstance(vehicle, Train) else 'Airplane')
        self.type_combo = ttk.Combobox(self, values=['Поезд', 'Самолёт'], state='readonly')
        if vehicle is None:
            self.type_combo.set('Поезд')
        else:
            self.type_combo.set('Поезд' if isinstance(vehicle, Train) else 'Самолёт')
        self.type_combo.grid(row=0, column=1, padx=6, pady=6)

        tk.Label(self, text="Вместимость (кг):").grid(row=1, column=0, sticky='e', padx=6, pady=6)
        self.capacity_var = tk.StringVar(value=str(getattr(vehicle, 'capacity', '')))
        self.capacity_entry = tk.Entry(self, textvariable=self.capacity_var)
        self.capacity_entry.grid(row=1, column=1, padx=6, pady=6)

        tk.Label(self, text="Кол-во вагонов (для поезда):").grid(row=2, column=0, sticky='e', padx=6, pady=6)
        self.cars_var = tk.StringVar(value=str(getattr(vehicle, 'number_of_cars', 0)))
        self.cars_entry = tk.Entry(self, textvariable=self.cars_var)
        self.cars_entry.grid(row=2, column=1, padx=6, pady=6)

        tk.Label(self, text="Макс. высота (для самолёта):").grid(row=3, column=0, sticky='e', padx=6, pady=6)
        self.alt_var = tk.StringVar(value=str(getattr(vehicle, 'max_altitude', 0)))
        self.alt_entry = tk.Entry(self, textvariable=self.alt_var)
        self.alt_entry.grid(row=3, column=1, padx=6, pady=6)

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(0,6))

        save_btn = tk.Button(btn_frame, text="Сохранить", command=self.on_save)
        save_btn.pack(side='left', padx=6)
        cancel_btn = tk.Button(btn_frame, text="Отмена", command=self.on_cancel)
        cancel_btn.pack(side='left')

        ToolTip(save_btn, 'Сохранить транспорт (Enter)')
        ToolTip(cancel_btn, 'Отмена (Esc)')

        self.bind('<Return>', lambda e: self.on_save())
        self.bind('<Escape>', lambda e: self.on_cancel())

        self.capacity_entry.focus()

    def on_save(self):
        ok_cap, cap = validate_capacity(self.capacity_var.get())
        if not ok_cap:
            messagebox.showwarning("Неверная вместимость", "Вместимость должна быть числом >= 0.")
            self.capacity_var.set('')
            return

        t = self.type_combo.get()
        if t == 'Поезд':
            try:
                cars = int(self.cars_var.get())
                if cars < 0:
                    raise ValueError()
            except Exception:
                messagebox.showwarning("Неверное число вагонов", "Число вагонов должно быть неотрицательным целым.")
                self.cars_var.set('')
                return
            self.result = Train(cap, cars)
        else:
            try:
                alt = int(self.alt_var.get())
                if alt <= 0:
                    raise ValueError()
            except Exception:
                messagebox.showwarning("Неверная высота", "Максимальная высота должна быть положительным целым.")
                self.alt_var.set('')
                return
            self.result = Airplane(cap, alt)

        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()


class TransportApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Transport Company GUI')
        self.geometry('1000x600')

        self.company = TransportCompany('MyCompany', [], [])
        self.last_distribution = None

        self.create_menu()

        self.create_controls()

        self.create_tables()

        self.status_var = tk.StringVar(value='Готово')
        status = tk.Label(self, textvariable=self.status_var, bd=1, relief='sunken', anchor='w')
        status.pack(side='bottom', fill='x')

    def create_menu(self):
        menubar = tk.Menu(self)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label='Экспорт результата', command=self.export_result)
        file_menu.add_separator()
        file_menu.add_command(label='Сохранить состояние...', command=self.save_state)
        file_menu.add_command(label='Загрузить состояние...', command=self.load_state)
        file_menu.add_separator()
        file_menu.add_command(label='Выход', command=self.quit)
        menubar.add_cascade(label='Файл', menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label='О программе', command=self.show_about)
        menubar.add_cascade(label='Справка', menu=help_menu)

        self.config(menu=menubar)

    def create_controls(self):
        frame = tk.Frame(self)
        frame.pack(side='top', fill='x', padx=6, pady=6)

        add_client_btn = tk.Button(frame, text='Добавить клиента', command=self.add_client)
        add_client_btn.pack(side='left')
        ToolTip(add_client_btn, 'Открыть форму добавления клиента')

        add_vehicle_btn = tk.Button(frame, text='Добавить транспорт', command=self.add_vehicle)
        add_vehicle_btn.pack(side='left', padx=6)
        ToolTip(add_vehicle_btn, 'Открыть форму добавления транспорта')

        del_btn = tk.Button(frame, text='Удалить выделенное', command=self.delete_selected)
        del_btn.pack(side='left', padx=6)
        ToolTip(del_btn, 'Удалить выбранную запись в таблице')

        distribute_btn = tk.Button(frame, text='Распределить грузы', command=self.distribute)
        distribute_btn.pack(side='left', padx=6)
        ToolTip(distribute_btn, 'Оптимизировать распределение грузов')

    def create_tables(self):
        paned = ttk.Panedwindow(self, orient='horizontal')
        paned.pack(fill='both', expand=True, padx=6, pady=6)

        client_frame = ttk.Labelframe(paned, text='Клиенты')
        self.client_tree = ttk.Treeview(client_frame, columns=('name','weight','vip'), show='headings', selectmode='browse')
        for col, text in [('name','Имя'),('weight','Вес (кг)'),('vip','VIP')]:
            self.client_tree.heading(col, text=text, command=partial(self.sort_tree, self.client_tree, col))
            self.client_tree.column(col, anchor='center')
        self.client_tree.pack(fill='both', expand=True)
        self.client_tree.bind('<Double-1>', self.on_client_double)
        paned.add(client_frame, weight=1)

        vehicle_frame = ttk.Labelframe(paned, text='Транспорт')
        self.vehicle_tree = ttk.Treeview(vehicle_frame, columns=('id','type','capacity','load'), show='headings', selectmode='browse')
        for col, text in [('id','ID'),('type','Тип'),('capacity','Вместимость'),('load','Текущая загрузка')]:
            self.vehicle_tree.heading(col, text=text, command=partial(self.sort_tree, self.vehicle_tree, col))
            self.vehicle_tree.column(col, anchor='center')
        self.vehicle_tree.pack(fill='both', expand=True)
        self.vehicle_tree.bind('<Double-1>', self.on_vehicle_double)
        paned.add(vehicle_frame, weight=2)

        search_frame = tk.Frame(client_frame)
        search_frame.pack(side='bottom', fill='x')
        tk.Label(search_frame, text='Поиск по имени:').pack(side='left')
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side='left', padx=6)
        search_entry.bind('<KeyRelease>', lambda e: self.refresh_clients())

    def sort_tree(self, tree, col):
        data = [(tree.set(k, col), k) for k in tree.get_children('')]
        try:
            data.sort(key=lambda t: float(t[0]))
        except Exception:
            data.sort(key=lambda t: t[0])
        for index, (_, k) in enumerate(data):
            tree.move(k, '', index)

    def add_client(self):
        dlg = ClientDialog(self, title='Добавить клиента')
        self.wait_window(dlg)
        if dlg.result:
            self.company.add_client(dlg.result)
            self.status('Клиент добавлен')
            self.refresh_clients()

    def add_vehicle(self):
        dlg = VehicleDialog(self, title='Добавить транспорт')
        self.wait_window(dlg)
        if dlg.result:
            self.company.add_vehicle(dlg.result)
            self.status('Транспорт добавлен')
            self.refresh_vehicles()

    def on_client_double(self, event):
        sel = self.client_tree.selection()
        if not sel:
            return
        item = sel[0]
        idx = int(self.client_tree.item(item, 'text'))
        client = self.company.clients[idx]
        dlg = ClientDialog(self, title='Редактировать клиента', client=client)
        self.wait_window(dlg)
        if dlg.result:
            self.company.clients[idx] = dlg.result
            self.status('Клиент обновлён')
            self.refresh_clients()

    def on_vehicle_double(self, event):
        sel = self.vehicle_tree.selection()
        if not sel:
            return
        item = sel[0]
        idx = int(self.vehicle_tree.item(item, 'text'))
        vehicle = self.company.vehicles[idx]
        dlg = VehicleDialog(self, title='Редактировать транспорт', vehicle=vehicle)
        self.wait_window(dlg)
        if dlg.result:
            self.company.vehicles[idx] = dlg.result
            self.status('Транспорт обновлён')
            self.refresh_vehicles()

    def delete_selected(self):
        focus = self.focus_get()
        if self.client_tree.selection():
            sel = self.client_tree.selection()[0]
            idx = int(self.client_tree.item(sel, 'text'))
            name = self.company.clients[idx].name
            if messagebox.askyesno('Подтвердите удаление', f'Удалить клиента "{name}"?'):
                del self.company.clients[idx]
                self.status(f'Клиент {name} удалён')
                self.refresh_clients()
            return
        if self.vehicle_tree.selection():
            sel = self.vehicle_tree.selection()[0]
            idx = int(self.vehicle_tree.item(sel, 'text'))
            vid = self.company.vehicles[idx].vehicle_id
            if messagebox.askyesno('Подтвердите удаление', f'Удалить транспорт {vid}?'):
                del self.company.vehicles[idx]
                self.status('Транспорт удалён')
                self.refresh_vehicles()
            return
        messagebox.showinfo('Нет выбора', 'Сначала выберите запись в таблице.')

    def refresh_clients(self):
        q = self.search_var.get().strip().lower()
        for i in self.client_tree.get_children(''):
            self.client_tree.delete(i)
        for idx, c in enumerate(self.company.clients):
            if q and q not in c.name.lower():
                continue
            self.client_tree.insert('', 'end', text=str(idx), values=(c.name, c.cargo_weight, str(c.is_vip)))

    def refresh_vehicles(self):
        for i in self.vehicle_tree.get_children(''):
            self.vehicle_tree.delete(i)
        for idx, v in enumerate(self.company.vehicles):
            typ = 'Поезд' if isinstance(v, Train) else 'Самолёт' if isinstance(v, Airplane) else 'Транспорт'
            self.vehicle_tree.insert('', 'end', text=str(idx), values=(str(v.vehicle_id), typ, v.capacity, v.current_load))

    def distribute(self):
        if not self.company.clients or not self.company.vehicles:
            messagebox.showwarning('Ошибка', 'Нужно как минимум один клиент и один транспорт для распределения.')
            return
        for v in self.company.vehicles:
            v.clients_list = []
            v.current_load = 0
        try:
            self.company.optimize_cargo_distribution()
            self.status('Распределение выполнено')
        except Exception as e:
            messagebox.showerror('Ошибка при распределении', str(e))
            self.status('Ошибка')
            return
        result = []
        for v in self.company.vehicles:
            result.append({
                'vehicle_id': str(v.vehicle_id),
                'type': 'Поезд' if isinstance(v, Train) else 'Самолёт' if isinstance(v, Airplane) else 'Транспорт',
                'capacity': v.capacity,
                'current_load': v.current_load,
                'clients': [{'name': c.name, 'cargo_weight': c.cargo_weight, 'vip': c.is_vip} for c in v.clients_list]
            })
        self.last_distribution = result
        self.show_distribution_modal(result)
        self.refresh_vehicles()

    def show_distribution_modal(self, result):
        dlg = tk.Toplevel(self)
        dlg.title('Результат распределения')
        dlg.geometry('700x400')
        dlg.grab_set()

        tree = ttk.Treeview(dlg, columns=('id','type','capacity','load','clients'), show='headings')
        for col, text in [('id','ID'),('type','Тип'),('capacity','Вместимость'),('load','Загружено'),('clients','Клиенты')]:
            tree.heading(col, text=text)
            tree.column(col, anchor='w')
        tree.pack(fill='both', expand=True)

        for r in result:
            clients_str = '; '.join([f"{c['name']}({c['cargo_weight']})" for c in r['clients']])
            tree.insert('', 'end', values=(r['vehicle_id'], r['type'], r['capacity'], r['current_load'], clients_str))

        btn_frame = tk.Frame(dlg)
        btn_frame.pack(fill='x', pady=6)
        save_btn = tk.Button(btn_frame, text='Сохранить результат...', command=self.export_result)
        save_btn.pack(side='right', padx=6)

    def export_result(self):
        if not self.last_distribution:
            messagebox.showwarning('Нет данных', 'Сначала выполните распределение грузов.')
            return
        ftypes = [('JSON file', '*.json'), ('CSV file', '*.csv')]
        path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=ftypes)
        if not path:
            return
        try:
            if path.lower().endswith('.json'):
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(self.last_distribution, f, ensure_ascii=False, indent=2)
            else:
                with open(path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['vehicle_id','type','capacity','current_load','clients'])
                    for r in self.last_distribution:
                        writer.writerow([r['vehicle_id'], r['type'], r['capacity'], r['current_load'], json.dumps(r['clients'], ensure_ascii=False)])
            self.status(f'Результат экспортирован в {os.path.basename(path)}')
            messagebox.showinfo('Экспорт', 'Результат успешно сохранён.')
        except Exception as e:
            messagebox.showerror('Ошибка сохранения', str(e))
            self.status('Ошибка при экспорте')

    def save_state(self):
        path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON','*.json')])
        if not path:
            return
        try:
            state = {
                'clients': [{'name': c.name, 'cargo_weight': c.cargo_weight, 'is_vip': c.is_vip} for c in self.company.clients],
                'vehicles': []
            }
            for v in self.company.vehicles:
                if isinstance(v, Train):
                    state['vehicles'].append({'type':'Train','capacity':v.capacity,'number_of_cars':v.number_of_cars})
                elif isinstance(v, Airplane):
                    state['vehicles'].append({'type':'Airplane','capacity':v.capacity,'max_altitude':v.max_altitude})
                else:
                    state['vehicles'].append({'type':'Vehicle','capacity':v.capacity})
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            self.status('Состояние сохранено')
            messagebox.showinfo('Сохранено', 'Состояние успешно сохранено.')
        except Exception as e:
            messagebox.showerror('Ошибка', str(e))
            self.status('Ошибка при сохранении')

    def load_state(self):
        path = filedialog.askopenfilename(filetypes=[('JSON','*.json')])
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            clients = [Client(c['name'], c['cargo_weight'], c.get('is_vip', False)) for c in state.get('clients', [])]
            vehicles = []
            for v in state.get('vehicles', []):
                if v.get('type') == 'Train':
                    vehicles.append(Train(v.get('capacity',0), v.get('number_of_cars',0)))
                elif v.get('type') == 'Airplane':
                    vehicles.append(Airplane(v.get('capacity',0), v.get('max_altitude',1)))
                else:
                    from transport.vehicle import Vehicle as V
                    vehicles.append(V(v.get('capacity',0)))
            self.company.clients = clients
            self.company.vehicles = vehicles
            self.refresh_clients()
            self.refresh_vehicles()
            self.status('Состояние загружено')
            messagebox.showinfo('Готово', 'Состояние загружено.')
        except Exception as e:
            messagebox.showerror('Ошибка', str(e))
            self.status('Ошибка при загрузке')

    def show_about(self):
        about_text = (
            'Описание: GUI для управления транспортной компанией и распределения грузов.'
        )
        messagebox.showinfo('О программе', about_text)

    def status(self, text: str):
        self.status_var.set(text)


if __name__ == '__main__':
    app = TransportApp()
    app.refresh_clients()
    app.refresh_vehicles()
    app.mainloop()
    
    
