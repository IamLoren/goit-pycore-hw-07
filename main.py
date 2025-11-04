
from collections import UserDict
from datetime import datetime, timedelta


class Field:
    
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        return f"{self.__class__.__name__}('{self.value}')"


class Name(Field):
    
    pass


class Phone(Field):
    
    def __init__(self, value):
        if not self._validate(value):
            raise ValueError("Phone number must contain exactly 10 digits")
        super().__init__(value)
    
    def _validate(self, value):
        if not isinstance(value, str):
            return False
        digits = ''.join(filter(str.isdigit, value))
        return len(digits) == 10
    
    def __eq__(self, other):
        if isinstance(other, Phone):
            return self._normalize(self.value) == self._normalize(other.value)
        if isinstance(other, str):
            return self._normalize(self.value) == self._normalize(other)
        return False
    
    def _normalize(self, value):
        return ''.join(filter(str.isdigit, value))


class Birthday(Field):
    
    def __init__(self, value):
        try:
            birthday_date = datetime.strptime(value, "%d.%m.%Y")
            super().__init__(value)
            self.date = birthday_date
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Record:
    
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
    
    def add_phone(self, phone):
        phone_obj = Phone(phone)
        self.phones.append(phone_obj)
    
    def remove_phone(self, phone):
        for i, p in enumerate(self.phones):
            if p == phone:
                self.phones.pop(i)
                return True
        return False
    
    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p == old_phone:
                self.phones[i] = Phone(new_phone)
                return True
        return False
    
    def find_phone(self, phone):
        for p in self.phones:
            if p == phone:
                return p
        return None
    
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
    
    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones)
        birthday_str = f", birthday: {self.birthday.value}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {phones_str}{birthday_str}"


class AddressBook(UserDict):
    
    def add_record(self, record):
        self.data[record.name.value] = record
    
    def find(self, name):
        return self.data.get(name)
    
    def delete(self, name):
        if name in self.data:
            del self.data[name]
            return True
        return False
    
    def get_upcoming_birthdays(self):
 
        today = datetime.today().date()
        upcoming_birthdays = []
        
        for record in self.data.values():
            if record.birthday is None:
                continue
            
            birthday_date = record.birthday.date.date()
            
            birthday_this_year = birthday_date.replace(year=today.year)
            
            if birthday_this_year < today:
                birthday_this_year = birthday_date.replace(year=today.year + 1)
            
            delta_days = (birthday_this_year - today).days
            
            if 0 <= delta_days <= 7:
                congratulation_date = birthday_this_year
                
                if birthday_this_year.weekday() == 5:  
                    congratulation_date = birthday_this_year + timedelta(days=2)
                elif birthday_this_year.weekday() == 6: 
                    congratulation_date = birthday_this_year + timedelta(days=1)
                
                upcoming_birthdays.append({
                    "name": record.name.value,
                    "congratulation_date": congratulation_date.strftime("%d.%m.%Y")
                })
        
        return upcoming_birthdays


def input_error(func):
    
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact not found."
        except ValueError as e:
            return str(e) if str(e) else "Enter the argument for the command"
        except IndexError:
            return "Enter the argument for the command"
    
    return inner


@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        raise ValueError("Give me name and phone please.")
    
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    
    if phone:
        record.add_phone(phone)
    
    return message


@input_error
def change_contact(args, book: AddressBook):
    if len(args) < 3:
        raise ValueError("Give me name, old phone and new phone please.")
    
    name, old_phone, new_phone = args[0], args[1], args[2]
    record = book.find(name)
    
    if record is None:
        raise KeyError
    
    if record.edit_phone(old_phone, new_phone):
        return "Contact updated."
    else:
        return f"Phone {old_phone} not found for contact {name}."


@input_error
def show_phone(args, book: AddressBook):
    if len(args) == 0:
        raise IndexError
    
    name = args[0]
    record = book.find(name)
    
    if record is None:
        raise KeyError
    
    if not record.phones:
        return f"No phones for contact {name}."
    
    phones = '; '.join(p.value for p in record.phones)
    return f"{name}: {phones}"


@input_error
def show_all(args, book: AddressBook):
    if not book.data:
        return "No contacts saved."
    
    result = []
    for record in book.data.values():
        result.append(str(record))
    
    return "\n".join(result)


@input_error
def add_birthday(args, book: AddressBook):
    if len(args) < 2:
        raise ValueError("Give me name and birthday please.")
    
    name, birthday = args[0], args[1]
    record = book.find(name)
    
    if record is None:
        raise KeyError
    
    record.add_birthday(birthday)
    return f"Birthday added for {name}."


@input_error
def show_birthday(args, book: AddressBook):
    if len(args) == 0:
        raise IndexError
    
    name = args[0]
    record = book.find(name)
    
    if record is None:
        raise KeyError
    
    if record.birthday is None:
        return f"No birthday set for {name}."
    
    return f"{name}: {record.birthday.value}"


@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    
    if not upcoming:
        return "No upcoming birthdays in the next week."
    
    result = ["Upcoming birthdays:"]
    for item in upcoming:
        result.append(f"{item['name']}: {item['congratulation_date']}")
    
    return "\n".join(result)


def parse_input(user_input):
    parts = user_input.strip().split()
    if not parts:
        return "", []
    command = parts[0].lower()
    args = parts[1:]
    return command, args


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)
        
        if command in ["close", "exit"]:
            print("Good bye!")
            break
        
        elif command == "hello":
            print("How can I help you?")
        
        elif command == "add":
            print(add_contact(args, book))
        
        elif command == "change":
            print(change_contact(args, book))
        
        elif command == "phone":
            print(show_phone(args, book))
        
        elif command == "all":
            print(show_all(args, book))
        
        elif command == "add-birthday":
            print(add_birthday(args, book))
        
        elif command == "show-birthday":
            print(show_birthday(args, book))
        
        elif command == "birthdays":
            print(birthdays(args, book))
        
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()

