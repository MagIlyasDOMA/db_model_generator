# db-model-generator
Пакет для автоматической генерации моделей SQLAlchemy и форм WTForms на основе таблиц базы данных.

## Установка
```bash
pip install db-model-generator
```

## Использование
### Командная строка
Основная команда для использования из командной строки:

```bash
db-model-generator [ОПЦИИ] DATABASE TABLE_NAME [OUTPUT] [CONFIG]
```

#### Основные аргументы:
- `database` - URL базы данных (например: sqlite:///example.db)

- `table_name` - имя таблицы для генерации

- `output` - имя выходного файла (опционально)

- `config` - путь к JSON файлу конфигурации (опционально)

#### Опции:
- `--database`, `--table-name`, `--output`, `--config` - альтернативный способ указания основных аргументов

- `--default-rename`, `-r` - переименовать классы в Model и Form

- `--only-model`, `-m` - создать только модель

- `--only-form`, `-f` - создать только форму

- `--classic-sqlalchemy`, `-s` - создать модель sqlalchemy вместо flask_sqlalchemy

- `--tab`, `-t` - заменить 4 пробела символом табуляции \t

- `--translate-labels`, `-l` - перевести labels в форме (указать код языка)

- `--label-original-language` - оригинальный язык labels (по умолчанию: 'en')

- `--log-mode`, `--log`, `-V`, `-L` - включить логирование

- `--version`, `-v` - показать версию пакета

- `--env`, `-e` - путь к файлу окружения (.env)

- `--submit-button`, `--submit`, `-s` - текст для кнопки submit (если не указан, то кнопка не добавляется)

- `--all-langs` - показать все доступные языки для перевода форм. В случае использования программа покажет все доступные языки и завершит работу

- `--non-rewritable`, `--file-protect`, `-p` - отметить файл как неперезаписываемый

- `--ignore-and-rewrite`, `-i` - перезаписать файл в любом случае

- `--debug`, `-d` - включить режим отладки

- `--add-db-to-all`, `--add-db`, `--db-add`, `-a` - Добавить объект базы данных (db) в `__all__`

#### Примеры использования:
```bash
# Базовая генерация модели и формы
db-model-generator sqlite:///example.db users

# Генерация только модели
db-model-generator sqlite:///example.db users --only-model

# Генерация с сохранением в файл
db-model-generator sqlite:///example.db users models.py

# Использование конфигурационного файла
db-model-generator sqlite:///example.db users --config config.json

# Перевод labels на русский язык
db-model-generator sqlite:///example.db users --translate-labels ru

# Классический SQLAlchemy вместо Flask-SQLAlchemy
db-model-generator sqlite:///example.db users --classic-sqlalchemy

# Добавить кнопку подтверждения в форму
db-model-generator sqlite:///example.db users --submit-button "Send"

# Показать все доступные языки
db-model-generator --all-langs

# Защита файла от перезаписи
db-model-generator sqlite:///example.db users --non-rewritable

# Принудительная перезапись файла
db-model-generator sqlite:///example.db users --ignore-and-rewrite

# Режим отладки с подробными ошибками
db-model-generator sqlite:///example.db users --debug

# Добавить переменную db в __all__
db-model-generator sqlite:///example.db users --add-db-to-all
```

### Использование env-файлов
Пакет поддерживает загрузку аргументов из файлов окружения (.env). Для этого используйте опцию --env или укажите путь к файлу в параметре env при вызове функции.

#### Поддерживаемые переменные окружения:

`DATABASE_URL` или `DATABASE` - URL базы данных

`TABLE_NAME` - имя таблицы для генерации

`OUTPUT_PATH` или `OUTPUT` - путь к выходному файлу

`DEFAULT_RENAME` - переименовать классы в Model и Form (true/false)

`ONLY_MODEL` - генерировать только модель (true/false)

`ONLY_FORM` - генерировать только форму (true/false)

`CLASSIC_SQLALCHEMY` - использовать классический SQLAlchemy (true/false)

`TAB` - использовать табуляцию вместо пробелов (true/false)

`TRANSLATE_LABELS` - код языка для перевода labels

`LABEL_ORIGINAL_LANGUAGE` - исходный язык labels

`LOG_MODE` - включить логирование (true/false)

`SUBMIT` - текст для кнопки submit

`NON_REWRITABLE` - защита файла от перезаписи (true/false)

`IGNORE_AND_REWRITE` - принудительная перезапись файла (true/false)

`ADD_DB_TO_ALL` - Добавить объект базы данных (db) в `__all__`

#### Пример .env-файла
```dotenv
DATABASE_URL=sqlite:///example.db
TABLE_NAME=users
OUTPUT_PATH=models.py
DEFAULT_RENAME=false
ONLY_MODEL=false
ONLY_FORM=false
CLASSIC_SQLALCHEMY=false
TAB=false
TRANSLATE_LABELS=ru
LABEL_ORIGINAL_LANGUAGE=en
LOG_MODE=true
SUBMIT=Отправить
NON_REWRITABLE=false
IGNORE_AND_REWRITE=false
ADD_DB_TO_ALL=false
```


### Использование в Python
```python
from db_model_generator import generate

# Базовая генерация
generate(
    database="sqlite:///example.db",
    table_name="users"
)

# Расширенная генерация с опциями
generate(
    database="sqlite:///example.db",
    table_name="users",
    output="models.py",
    config="config.json",
    only_model=True,
    classic_sqlalchemy=False,
    translate_labels="ru",
    log_mode=True,
    submit='Send',
    non_rewritable=False,
    ignore_and_rewrite=True,
    debug=False
)
```

#### Параметры функции `generate()`:
- `database` (str) - URL базы данных

- `table_name` (str) - имя таблицы

- `output` (str, опционально) - путь к выходному файлу

- `config` (str, опционально) - путь к JSON файлу конфигурации

- `default_rename` (bool) - переименовать классы в Model и Form

- `only_model` (bool) - генерировать только модель

- `only_form` (bool) - генерировать только форму

- `classic_sqlalchemy` (bool) - использовать классический SQLAlchemy

- `tab` (bool) - использовать табуляцию вместо пробелов

- `translate_labels` (str, опционально) - код языка для перевода labels

- `label_original_language` (str) - исходный язык labels (по умолчанию 'en')

- `log_mode` (bool) - включить логирование

- `env` (str, опционально) - путь к файлу окружения

- `submit` (str, опционально) - текст для кнопки submit (если None, то кнопка не добавляется)

- `non_rewritable` (bool) - защита файла от перезаписи

- `ignore_and_rewrite` (bool) - принудительная перезапись файла

- `debug` (bool) - включить режим отладки

- `add_db_to_all` (bool) - Добавить объект базы данных (db) в `__all__ `

## Конфигурационный файл
Вы можете создать JSON файл конфигурации для настройки генерации:

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
    },
    "arguments": {
        "database": "sqlite:///example.db",
        "table_name": "users",
        "output": "models.py",
        "default_rename": false,
        "only_model": false,
        "only_form": false,
        "classic_sqlalchemy": false,
        "tab": false,
        "translate_labels": null,
        "label_original_language": "en",
        "log_mode": false,
        "submit": "Send",
        "non_rewritable": false,
        "ignore_and_rewrite": false
    }
}
```

## Поддерживаемые языки для перевода
Пакет поддерживает перевод labels форм на множество языков через Google Translate. Полный список поддерживаемых языков доступен в модуле constants.py.

#### Примеры кодов языков:

- `en` - английский

- `ru` - русский

- `es` - испанский

- `fr` - французский

- `de` - немецкий

- `zh-cn` - китайский (упрощенный)

- `ja` - японский

### Пример выходного файла
Для таблицы users с колонками id, username, email, created_at:

```python
# Файл сгенерирован db-model-generator 30.11.2025 13:46:39
# Путь к базе данных: example.db
# Название таблицы: programs

__all__ = ['Users', 'UsersForm']

# Модель SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f'<Users {self.id}>'


# Форма WTForms
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, FloatField, BooleanField, DateField, DateTimeField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange


class UsersForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField("Send")
```
    
## Зависимости
- `sqlalchemy` - для работы с базами данных

- `deep-translator` - для перевода labels

- `tab4` - для форматирования кода

- `python-dotenv` - для загрузки переменных окружения

- `undefined-python` - для реализации некоторых функций

## Поддерживаемые СУБД
Пакет работает с любыми СУБД, поддерживаемыми SQLAlchemy:

- SQLite

- PostgreSQL

- MySQL

- Oracle

- Microsoft SQL Server

- и другие

## Обработка ошибок
### Режим отладки
При использовании опции --debug или -d пакет выводит полную трассировку стека ошибок, что полезно для диагностики проблем.

### Защита файлов
--non-rewritable - предотвращает случайную перезапись существующих файлов

--ignore-and-rewrite - принудительно перезаписывает файлы, игнорируя защиту

### Логирование
Опция --log-mode включает подробное логирование процесса генерации, что помогает отслеживать каждый этап работы пакета.

### Версия
Текущая версия пакета: 1.4.1

