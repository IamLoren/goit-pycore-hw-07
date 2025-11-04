# Віртуальний асистент з адресною книгою

Консольний бот-помічник для управління адресною книгою з підтримкою телефонів та днів народження.

## Функціональність

Бот підтримує наступні команди:

### Основні команди

- `hello` - Привітання від бота
- `close` або `exit` - Вийти з програми

### Управління контактами

- `add [ім'я] [телефон]` - Додати новий контакт або телефон до існуючого
- `change [ім'я] [старий_телефон] [новий_телефон]` - Змінити номер телефону
- `phone [ім'я]` - Показати телефони контакту
- `all` - Показати всі контакти

### Управління днями народження

- `add-birthday [ім'я] [дата]` - Додати день народження (формат: DD.MM.YYYY)
- `show-birthday [ім'я]` - Показати день народження контакту
- `birthdays` - Показати дні народження на наступному тижні

## Валідація даних

- **Телефон**: має містити рівно 10 цифр
- **День народження**: формат DD.MM.YYYY (наприклад, 15.05.1990)

## Приклад використання

```bash
python main.py
```

### Діалог з ботом:

```
Welcome to the assistant bot!

Enter a command: add John 1234567890
Contact added.

Enter a command: add John 5555555555
Contact updated.

Enter a command: phone John
John: 1234567890; 5555555555

Enter a command: add-birthday John 15.05.1990
Birthday added for John.

Enter a command: show-birthday John
John: 15.05.1990

Enter a command: all
Contact name: John, phones: 1234567890; 5555555555, birthday: 15.05.1990

Enter a command: change John 1234567890 9999999999
Contact updated.

Enter a command: phone John
John: 9999999999; 5555555555

Enter a command: birthdays
Upcoming birthdays:
John: 15.05.2025

Enter a command: close
Good bye!
```

## Обробка помилок

Всі помилки введення обробляються декоратором `@input_error`:

```
Enter a command: add
Give me name and phone please.

Enter a command: phone Unknown
Contact not found.

Enter a command: add-birthday John 15-05-1990
Invalid date format. Use DD.MM.YYYY

Enter a command: add Alice 12345
Phone number must contain exactly 10 digits
```

## Класи

### Field
Базовий клас для всіх полів запису.

### Name
Клас для зберігання імені контакту (обов'язкове поле).

### Phone
Клас для зберігання телефону з валідацією (10 цифр).

### Birthday
Клас для зберігання дня народження з валідацією формату DD.MM.YYYY.

### Record
Клас для зберігання інформації про контакт:
- Ім'я (Name)
- Список телефонів (Phone)
- День народження (Birthday) - необов'язкове

### AddressBook
Клас для управління записами контактів з методами:
- `add_record()` - додавання запису
- `find()` - пошук запису за ім'ям
- `delete()` - видалення запису
- `get_upcoming_birthdays()` - отримання списку майбутніх днів народження

## Особливості

- Якщо день народження випадає на вихідні (субота/неділя), привітання переноситься на наступний понеділок
- Можна додати декілька телефонів до одного контакту
- Всі дані зберігаються в пам'яті під час роботи програми

