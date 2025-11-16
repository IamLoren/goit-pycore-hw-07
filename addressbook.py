

from collections import UserDict
from datetime import datetime, timedelta
import re
import config


class Field:

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.value}')"


class Name(Field):

    @staticmethod
    def validator(name):
        """Validate name."""
        return isinstance(name, str) and len(name) > 0


class Phone(Field):

    def __init__(self, value):
        if not self.validator(value):
            raise ValueError(
                "Phone number must contain exactly 10 digits"
            )
        super().__init__(value)

    @staticmethod
    def validator(value):

        if not isinstance(value, str):
            return False
        return bool(re.match(config.PHONE_FORMAT, value))

    def __eq__(self, other):
        if isinstance(other, Phone):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other
        return False


class Birthday(Field):

    def __init__(self, value):
        if not self.validator(value):
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        try:
            birthday_date = datetime.strptime(
                value, config.BIRTHDAY_FORMAT
            )
            super().__init__(value)
            self.date = birthday_date
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    @staticmethod
    def validator(value):

        try:
            datetime.strptime(value, config.BIRTHDAY_FORMAT)
            return True
        except (ValueError, AttributeError):
            return False


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
        birthday_str = (f", birthday: {self.birthday.value}"
                        if self.birthday else "")
        return (f"Contact name: {self.name.value}, "
                f"phones: {phones_str}{birthday_str}")


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
                birthday_this_year = birthday_date.replace(
                    year=today.year + 1
                )

            delta_days = (birthday_this_year - today).days

            if 0 <= delta_days <= 7:
                congratulation_date = birthday_this_year

                if birthday_this_year.weekday() == 5:
                    congratulation_date = (birthday_this_year +
                                           timedelta(days=2))
                elif birthday_this_year.weekday() == 6:
                    congratulation_date = (birthday_this_year +
                                           timedelta(days=1))

                upcoming_birthdays.append({
                    "name": record.name.value,
                    "congratulation_date":
                        congratulation_date.strftime(
                            config.BIRTHDAY_FORMAT
                        )
                })

        return upcoming_birthdays

    def all_contacts(self):
        if not self.data:
            return "No contacts saved."

        result = []
        for record in self.data.values():
            result.append(str(record))

        return "\n".join(result)
