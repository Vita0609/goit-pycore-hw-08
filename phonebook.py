import pickle
import sys
from pathlib import Path
from collections import UserDict
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Телефон не містить 10 чисел")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            birthday_date = datetime.strptime(value, "%d.%m.%Y")
            super().__init__(birthday_date)
        except ValueError:
            raise ValueError("Невірний формат дати. Використовуйте формат DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
                break

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p.value
        return None

    def add_birthday(self, date):
        self.birthday = Birthday(date)

    def __str__(self):
        phones = '; '.join(p.value for p in self.phones)
        return f"Ім'я: {self.name.value}, телефони: {phones}, день народження: {self.birthday if self.birthday else 'не зазначено'}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

def save_data(book, filename="book.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="book.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

class InvalidCommand(Exception):
    pass

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Будь ласка, надайте ім'я та номер телефону."
        except KeyError:
            return "Контакт не знайдений."
        except IndexError:
            return "Неправильне використання команди. Будь ласка, спробуйте знову."
        except Exception as e:
            return f"Помилка: {e}"
    return inner

@input_error
def add_contact(args, contacts):
    name, phone, *_ = args
    record = contacts.find(name)
    message = "Контакт оновлений."
    if record is None:
        record = Record(name)
        contacts.add_record(record)
        message = "Контакт доданий."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, contacts):
    name, old_phone, new_phone = args
    record = contacts.find(name)
    if record is None:
        return f"Контакт з іменем {name} не знайдено."
    record.edit_phone(old_phone, new_phone)
    return "Контакт оновлено."

@input_error
def show_phone(args, contacts):
    name, = args
    record = contacts.find(name)
    if record is None:
        return f"Контакт з іменем {name} не знайдено."
    return f"{record}"

@input_error
def show_all(contacts):
    res = [f"{key} {value}" for key, value in contacts.items()]
    return "\n".join(res)

@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

@input_error
def add_birthday(args, contacts):
    name, birthday, *_ = args
    record = contacts.find(name)
    if record is None:
        return f"Контакт {name} не знайдено."
    record.add_birthday(birthday)
    return "День народження додано."

@input_error
def show_birthday(args, contacts):
    name, = args
    record = contacts.find(name)
    if record is None or record.birthday is None:
        return f"Немає дня народження для {name}."
    return f"День народження {name}: {record.birthday}"

@input_error
def birthdays(args, contacts):
    today = datetime.today()
    next_week = today + timedelta(days=7)
    upcoming_birthdays = []
    for record in contacts.values():
        if record.birthday:
            birthday_this_year = record.birthday.value.replace(year=today.year)
            if today <= birthday_this_year <= next_week:
                days_left = (birthday_this_year - today).days
                upcoming_birthdays.append(f"{record.name.value}: {record.birthday} (через {days_left} днів)")
    return "\n".join(upcoming_birthdays) if upcoming_birthdays else "Немає найближчих днів народження."

def main():
    contacts = load_data()

    print("Вітаємо в асистенті! \n\
    - add [ім'я] [новий номер телефону] \n\
    - change [ім'я] [старий номер телефону] [новий номер телефону] \n\
    - phone [ім'я] \n\
    - all \n\
    - add-birthday [ім'я] [дата] \n\
    - show-birthday [ім'я] \n\
    - birthdays [кількість днів] \n\
    - close або exit")

    while True:
        user_input = input("Введіть команду: ")
        command, args = parse_input(user_input)
        if command in ["close", "exit"]:
            save_data(contacts)
            print("До побачення!")
            break      
        elif command == "hello":
            print("Як я можу допомогти?")      
        elif command == "add":
            print(add_contact(args, contacts))           
        elif command == "change":
            print(change_contact(args, contacts))       
        elif command == "phone":
            print(show_phone(args, contacts))         
        elif command == "all":
            print(show_all(contacts))
        elif command == "add-birthday":
            print(add_birthday(args, contacts))
        elif command == "show-birthday":
            print(show_birthday(args, contacts))
        elif command == "birthdays":
            print(birthdays(args, contacts))           
        else:
            print("Невірна команда.")

if __name__ == "__main__":
    main()
