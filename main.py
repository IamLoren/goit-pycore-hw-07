
from commands import BotCommands
import config


def parse_input(user_input):
    parts = user_input.strip().split()
    if not parts:
        return "", []
    command = parts[0].lower()
    args = parts[1:]
    return command, args


def main():
    print(config.WELCOME_MESSAGE)
    command_processor = BotCommands()

    while not command_processor.done:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        if not command:
            continue

        handler_name = command.replace("-", "_") + "_handler"

        if handler_name in dir(command_processor):
            handler = getattr(command_processor, handler_name)
            result = handler(args)
            print(result)
        else:
            print(
                "Invalid command. Type 'help' to see "
                "available commands."
            )


if __name__ == "__main__":
    main()
