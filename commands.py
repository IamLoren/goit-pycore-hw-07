
from addressbook import AddressBook, Record, Phone, Birthday
import config


class BotCommands:

    done = False

    def __init__(self):
        self.book = AddressBook()

    def input_validator(func):
        def inner(self, params):
            command = func.__name__.removesuffix('_handler')
            command_helper = self.get_helper(command)

            if command_helper is not None:
                command_params = command_helper()
                params_validation = {}
                help_string = ""
                i = 0

                for param_name, value in command_params.items():
                    if param_name != 'help':
                        if callable(value):
                            params_validation[param_name] = (
                                value(params[i]) if len(params) > i
                                else False
                            )
                        else:
                            params_validation[param_name] = (
                                True if len(params) > i else False
                            )
                        i += 1
                    else:
                        help_string = f"{command}: {value}"

                validation_errors = [
                    field for field, val in params_validation.items()
                    if not val
                ]

                if validation_errors:
                    error_in_fields = (
                        "Invalid fields: " + " ".join(validation_errors)
                    )
                    usage = (
                        f"{help_string}\n"
                        f"Usage: {command} <" +
                        "> <".join(params_validation.keys()) +
                        f">\n{error_in_fields}"
                    )
                    return usage
            else:
                if len(params) > 0:
                    return f"Usage: {command}"

            return func(self, params)
        return inner

    @input_validator
    def add_handler(self, params):
        name, phone = params[0], params[1]
        record = self.book.find(name)
        message = "Contact updated."

        if record is None:
            record = Record(name)
            self.book.add_record(record)
            message = "Contact added."

        if phone:
            try:
                record.add_phone(phone)
            except ValueError as e:
                return str(e)

        return message

    def add_helper(self):
        return {
            'help': "Add new contact or phone to existing contact",
            'name': None,
            'phone': Phone.validator,
        }

    @input_validator
    def change_handler(self, params):
        name, old_phone, new_phone = params[0], params[1], params[2]
        record = self.book.find(name)

        if record is None:
            return "Contact not found."

        if record.edit_phone(old_phone, new_phone):
            return "Contact updated."
        else:
            return f"Phone {old_phone} not found for contact {name}."

    def change_helper(self):
        return {
            'help': "Change phone number for existing contact",
            'name': None,
            'old_phone': Phone.validator,
            'new_phone': Phone.validator,
        }

    @input_validator
    def phone_handler(self, params):
        name = params[0]
        record = self.book.find(name)

        if record is None:
            return "Contact not found."

        if not record.phones:
            return f"No phones for contact {name}."

        phones = '; '.join(p.value for p in record.phones)
        return f"{name}: {phones}"

    def phone_helper(self):
        return {
            'help': "Show phone numbers for contact",
            'name': None,
        }

    @input_validator
    def all_handler(self, params):
        return self.book.all_contacts()

    def all_helper(self):
        return {
            'help': "Show all contacts in address book",
        }

    @input_validator
    def add_birthday_handler(self, params):
        name, birthday = params[0], params[1]
        record = self.book.find(name)

        if record is None:
            return "Contact not found."

        try:
            record.add_birthday(birthday)
            return f"Birthday added for {name}."
        except ValueError as e:
            return str(e)

    def add_birthday_helper(self):
        return {
            'help': "Add birthday to contact (format: DD.MM.YYYY)",
            'name': None,
            'birthday': Birthday.validator,
        }

    @input_validator
    def show_birthday_handler(self, params):
        name = params[0]
        record = self.book.find(name)

        if record is None:
            return "Contact not found."

        if record.birthday is None:
            return f"No birthday set for {name}."

        return f"{name}: {record.birthday.value}"

    def show_birthday_helper(self):
        return {
            'help': "Show birthday for contact",
            'name': None,
        }

    @input_validator
    def birthdays_handler(self, params):
        upcoming = self.book.get_upcoming_birthdays()

        if not upcoming:
            return "No upcoming birthdays in the next week."

        result = ["Upcoming birthdays:"]
        for item in upcoming:
            result.append(
                f"{item['name']}: {item['congratulation_date']}"
            )

        return "\n".join(result)

    def birthdays_helper(self):
        """Help for birthdays command."""
        return {
            'help': "Show birthdays in next week",
        }

    @input_validator
    def hello_handler(self, params):
        return "How can I help you?"

    def hello_helper(self):
        return {
            'help': "Greet the bot",
        }

    @input_validator
    def exit_handler(self, params):
        self.done = True
        return config.GOODBYE_MESSAGE

    def exit_helper(self):
        return {
            'help': "Exit the application",
        }

    def close_handler(self, params):
        return self.exit_handler(params)

    def close_helper(self):
        return self.exit_helper()

    @input_validator
    def help_handler(self, params):
        all_commands = sorted(self.get_avail_commands())
        help_dict = {}

        for command in all_commands:
            helper = self.get_helper(command)
            if helper is not None:
                params_dict = helper()
                help_dict[command] = (
                    params_dict['help'] if 'help' in params_dict else ""
                )
            else:
                help_dict[command] = ""

        txt = "Available commands:\n"
        for command, help_txt in help_dict.items():
            txt += f"  {command.ljust(20)} {help_txt}\n"

        return txt

    def help_helper(self):
        return {
            'help': "Show all available commands",
        }

    def get_avail_commands(self):
        return [
            func.replace("_handler", "").replace("_", "-")
            for func in dir(self)
            if func.endswith("_handler")
        ]

    def get_helper(self, command):
        helper_name = command.replace("-", "_") + "_helper"
        if helper_name in dir(self):
            return getattr(self, helper_name)
        return None
