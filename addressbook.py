"""AddressBook module with Contact management classes."""

from collections import UserDict
from datetime import datetime, timedelta
import re
import config


class Field:
    """Base class for record fields."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.value}')"


class Name(Field):
    """Class for storing contact name."""

    @staticmethod
    def validator(name):
        """Validate name."""
        return isinstance(name, str) and len(name) > 0


class Phone(Field):
    """Class for storing and validating phone number."""

    def __init__(self, value):
        if not self.validator(value):
            raise ValueError(
                "Phone number must contain exactly 10 digits"
            )
        super().__init__(value)

    @staticmethod
    def validator(value):
        """
        Validate phone number.

        Args:
            value: Phone number string

        Returns:
            bool: True if valid
        """
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
    """Class for storing and validating birthday date."""

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
        """
        Validate birthday date.

        Args:
            value: Date string in DD.MM.YYYY format

        Returns:
            bool: True if valid
        """
        try:
            datetime.strptime(value, config.BIRTHDAY_FORMAT)
            return True
        except (ValueError, AttributeError):
            return False


class Record:
    """Class for storing contact information."""

    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        """Add phone number to contact."""
        phone_obj = Phone(phone)
        self.phones.append(phone_obj)

    def remove_phone(self, phone):
        """Remove phone number from contact."""
        for i, p in enumerate(self.phones):
            if p == phone:
                self.phones.pop(i)
                return True
        return False

    def edit_phone(self, old_phone, new_phone):
        """Edit existing phone number."""
        for i, p in enumerate(self.phones):
            if p == old_phone:
                self.phones[i] = Phone(new_phone)
                return True
        return False

    def find_phone(self, phone):
        """Find phone number in contact."""
        for p in self.phones:
            if p == phone:
                return p
        return None

    def add_birthday(self, birthday):
        """Add birthday to contact."""
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = '; '.join(p.value for p in self.phones)
        birthday_str = (f", birthday: {self.birthday.value}"
                        if self.birthday else "")
        return (f"Contact name: {self.name.value}, "
                f"phones: {phones_str}{birthday_str}")


class AddressBook(UserDict):
    """Class for managing address book of contacts."""

    def add_record(self, record):
        """Add contact record to address book."""
        self.data[record.name.value] = record

    def find(self, name):
        """Find contact by name."""
        return self.data.get(name)

    def delete(self, name):
        """Delete contact from address book."""
        if name in self.data:
            del self.data[name]
            return True
        return False

    def get_upcoming_birthdays(self):
        """
        Get list of contacts with birthdays in next week.

        Returns:
            list: List of dicts with 'name' and 'congratulation_date'
        """
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

                # Move to Monday if falls on weekend
                if birthday_this_year.weekday() == 5:  # Saturday
                    congratulation_date = (birthday_this_year +
                                           timedelta(days=2))
                elif birthday_this_year.weekday() == 6:  # Sunday
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
        """Get all contacts as formatted string."""
        if not self.data:
            return "No contacts saved."

        result = []
        for record in self.data.values():
            result.append(str(record))

        return "\n".join(result)
