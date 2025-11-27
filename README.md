# ModelFormGenerator - Генератор моделей и форм

Скрипт для автоматической генерации моделей Flask-SQLAlchemy/SQLAlchemy и форм WTForms на основе таблиц базы данных.

## Возможности

- Генерация моделей SQLAlchemy для таблиц БД
- Генерация форм WTForms с валидаторами
- Поддержка Flask-SQLAlchemy и классического SQLAlchemy
- Настраиваемая конфигурация через JSON файлы
- Автоматическое определение типов полей и валидаторов
- Гибкие опции вывода (файл или консоль)

## Установка зависимостей

```bash
pip install sqlalchemy flask-sqlalchemy flask-wtf wtforms
```

## Использование
### Базовое использование
```bash
python generator.py <database_url> <table_name> [output_file] [config_file]
```

```bash
# Генерация модели и формы для таблицы users
python generator.py sqlite:///example.db users users.py

# Генерация только модели
python generator.py sqlite:///example.db users -m

# Генерация только формы
python generator.py sqlite:///example.db users -f

# Использование классического SQLAlchemy
python generator.py sqlite:///example.db users -s

# Переименование классов в Model и Form
python generator.py sqlite:///example.db users -r
```
### Аргументы командной строки

#### Обязательные аргументы:
- `database` - URL базы данных (например: sqlite:///example.db)

- `table_name` - Имя таблицы для генерации

#### Опциональные аргументы:
- `output` - Имя выходного файла (генерируется автоматически если не указан)

- `config` - Путь к JSON файлу конфигурации

#### Флаги:
- `-c, --config` - Путь к JSON файлу конфигурации

- `-r, --default-rename` - Переименовать классы в Model и Form

- `-m, --only-model` - Создать только модель

- `-f, --only-form` - Создать только форму

- `-s, --classic-sqlalchemy` - Создать модель sqlalchemy вместо flask_sqlalchemy

- `-t, --tab` - Заменить 4 пробела символом \t

## Программное использование

```python
from db_model_generator import generate

# Генерация файла
generate(
    database='sqlite:///example.db',
    table_name='users', 
    output='output.py',
    config='config.json', 
    default_rename=True,
    only_model=False,
    only_form=False,
    classic_sqlalchemy=False,
    tab=False
)
```

## Конфигурационный файл
#### Скрипт поддерживает настройку через JSON файл. Пример конфигурации:
```json
{
  "model": {
    "base_class": "db.Model",
    "imports": [
      "from flask_sqlalchemy import SQLAlchemy",
      "from datetime import datetime"
    ],
    "exclude_columns": ["created_at", "updated_at"],
    "type_mapping": {
      "string": "db.String",
      "text": "db.Text",
      "integer": "db.Integer",
      "float": "db.Float",
      "boolean": "db.Boolean",
      "datetime": "db.DateTime",
      "date": "db.Date"
    }
  },
  "form": {
    "base_class": "FlaskForm",
    "imports": [
      "from flask_wtf import FlaskForm",
      "from wtforms import StringField, TextAreaField, IntegerField, FloatField, BooleanField, DateField, DateTimeField, SelectField, SubmitField",
      "from wtforms.validators import DataRequired, Email, Length, NumberRange"
    ],
    "field_mapping": {
      "string": "StringField",
      "text": "TextAreaField",
      "integer": "IntegerField",
      "float": "FloatField",
      "boolean": "BooleanField",
      "datetime": "DateTimeField",
      "date": "DateField"
    },
    "default_validators": {
      "required": "DataRequired()",
      "email": "Email()"
    },
    "meta": {}
  }
}
```

## Настройки для классического SQLAlchemy
#### При использовании флага `--classic-sqlalchemy` автоматически применяется конфигурация:

```json
{
  "model": {
    "base_class": "Base",
    "imports": [
      "from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, Float",
      "from sqlalchemy.ext.declarative import declarative_base",
      "",
      "Base = declarative_base()"
    ],
    "exclude_columns": ["id", "created_at", "updated_at"],
    "type_mapping": {
      "string": "String",
      "text": "Text",
      "integer": "Integer",
      "float": "Float",
      "boolean": "Boolean",
      "datetime": "DateTime",
      "date": "Date"
    }
  }
}
```

## Пример выходного файла
### Модель SQLAlchemy

```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

__all__ += ['User']

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return f'<User {self.id}>'
```

### Форма WTForms

```python
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, FloatField, BooleanField, DateField, DateTimeField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange

__all__ += ['User']

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=255)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    submit = SubmitField('Отправить')
```

## Поддерживаемые типы данных:
- String - строковые поля (VARCHAR)

- Text - текстовые поля (TEXT)

- Integer - целочисленные поля

- Float - числа с плавающей точкой

- Boolean - логические значения

- DateTime - дата и время

- Date - дата

## Особенности:
- Автоматическое определение первичных ключей

- Генерация соответствующих валидаторов (DataRequired, Email, Length)

- Преобразование имен полей из snake_case в CamelCase

- Исключение служебных полей (created_at, updated_at)

- Поддержка пользовательских мета-настроек для форм

## Обработка ошибок
Скрипт обрабатывает следующие ошибки:

- Отсутствие базы данных или таблицы

- Некорректный формат конфигурационного файла

- Проблемы с подключением к БД

В случае ошибки выводится сообщение в stderr и завершение с кодом 1.

## Зависимости
- SQLAlchemy

- Flask-SQLAlchemy (опционально)

- Flask-WTF (опционально)

- tab4 (для форматирования отступов)

