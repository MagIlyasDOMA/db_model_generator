#!/usr/bin/env python3
"""
Скрипт для автоматической генерации моделей Flask-SQLAlchemy и форм WTForms
на основе таблиц базы данных.
"""

import argparse, json, re, sys
from pathlib import Path
from tab4 import tab4
from typing import Optional, Union
from sqlalchemy import create_engine, MetaData, Table, inspect
from sqlalchemy.types import String, Integer, Float, Text, Boolean, DateTime, Date
from deep_translator import GoogleTranslator
from .constants import LANGUAGES

PathLike = Union[str, Path]

__all__ = ['generate']


def translate_validator(language_code: str) -> str:
    if not isinstance(language_code, str):
        raise argparse.ArgumentTypeError("Language code must be a string")
    elif language_code not in LANGUAGES.keys():
        raise argparse.ArgumentTypeError(f"Language code {language_code} is not supported")
    return language_code


class ModelFormGenerator:
    """Генератор моделей и форм на основе таблиц БД"""

    REQUIRED_ARGS = ['database_url', 'table_name']
    ALLOWED_ARGS = ['database_url', 'table_name', 'default_rename', 'only_model', 'only_form',
                    'classic_sqlalchemy', 'tab', 'translate_labels', 'label_original_language']
    database_url: Optional[str]
    table_name: Optional[str]
    classic_sqlalchemy: bool = False
    translate_labels: Optional[str] = None
    label_original_language: str = 'en'
    _translator: Optional[GoogleTranslator] = None

    def __init__(self, config_path=None, **kwargs):
        self.config = self._load_config(config_path, kwargs)
        self._init_main_args(kwargs)
        self.engine = create_engine(self.database_url)
        self.metadata = MetaData()

    def _init_main_args(self, kwargs):
        """Инициализирует основные аргументы до загрузки конфигурации"""
        # Сначала устанавливаем значения по умолчанию
        self.database_url = None
        self.table_name = None
        self.classic_sqlalchemy = False
        self.translate_labels = None
        self.label_original_language = 'en'

        # Затем обновляем из kwargs
        for key, value in kwargs.items():
            if key in self.ALLOWED_ARGS and value is not None:
                setattr(self, key, value)

        # Проверяем обязательные аргументы
        for key in self.REQUIRED_ARGS:
            if getattr(self, key) is None:
                raise ValueError(f"Required argument {key} is missing")

    def _load_config(self, config_path, kwargs):
        """Загружает конфигурацию из JSON файла"""
        # Базовые настройки для Flask-SQLAlchemy
        default_config = {
            "model": {
                "base_class": "db.Model",
                "imports": [
                    "from flask_sqlalchemy import SQLAlchemy",
                    "from datetime import datetime",
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
                "database_url": None,
                "table_name": None,
                "default_rename": False,
                "only_model": False,
                "only_form": False,
                "classic_sqlalchemy": False,
                "tab": False,
                "translate_labels": None,
                "label_original_language": "en"
            }
        }

        # Если используется классический SQLAlchemy, меняем настройки
        if self.classic_sqlalchemy:
            default_config["model"] = {
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

        # Загружаем пользовательскую конфигурацию если указан путь
        if config_path and Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                # Рекурсивно обновляем конфигурацию по умолчанию
                self._update_config(default_config, user_config)

        return default_config

    def _update_config(self, default, user):
        """Рекурсивно обновляет конфигурацию по умолчанию пользовательской"""
        for key, value in user.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._update_config(default[key], value)
            else:
                default[key] = value

    def _get_table_info(self):
        """Получает информацию о таблице и ее колонках"""
        inspector = inspect(self.engine)

        # Получаем информацию о колонках
        columns_info = []
        for column in inspector.get_columns(self.table_name):
            col_info = {
                'name': column['name'],
                'type': type(column['type']).__name__.lower(),
                'nullable': column['nullable'],
                'default': column['default'],
                'primary_key': column.get('primary_key', False),
                'length': getattr(column['type'], 'length', None)
            }
            columns_info.append(col_info)

        return columns_info

    def _python_type_to_sqlalchemy(self, sql_type, length=None):
        """Преобразует SQL тип в SQLAlchemy тип"""
        type_mapping = self.config["model"]["type_mapping"]

        if sql_type.startswith('varchar') or sql_type == 'string' or sql_type == 'text':
            if self.classic_sqlalchemy:
                return f"String({length})" if length else "String"
            else:
                return f"db.String({length})" if length else "db.String"
        elif sql_type == 'integer':
            return "Integer" if self.classic_sqlalchemy else "db.Integer"
        elif sql_type == 'float' or sql_type == 'numeric':
            return "Float" if self.classic_sqlalchemy else "db.Float"
        elif sql_type == 'boolean':
            return "Boolean" if self.classic_sqlalchemy else "db.Boolean"
        elif sql_type == 'datetime':
            return "DateTime" if self.classic_sqlalchemy else "db.DateTime"
        elif sql_type == 'date':
            return "Date" if self.classic_sqlalchemy else "db.Date"
        elif sql_type == 'text':
            return "Text" if self.classic_sqlalchemy else "db.Text"
        else:
            return "String" if self.classic_sqlalchemy else "db.String"

    def _python_type_to_wtforms(self, sql_type):
        """Преобразует SQL тип в WTForms поле"""
        field_mapping = self.config["form"]["field_mapping"]

        if sql_type.startswith('varchar') or sql_type == 'string':
            return field_mapping["string"]
        elif sql_type == 'text':
            return field_mapping["text"]
        elif sql_type == 'integer':
            return field_mapping["integer"]
        elif sql_type == 'float' or sql_type == 'numeric':
            return field_mapping["float"]
        elif sql_type == 'boolean':
            return field_mapping["boolean"]
        elif sql_type == 'datetime':
            return field_mapping["datetime"]
        elif sql_type == 'date':
            return field_mapping["date"]
        else:
            return field_mapping["string"]

    def _generate_validators(self, column_info):
        """Генерирует валидаторы для поля формы"""
        validators = []

        # Проверка на обязательность
        if not column_info['nullable'] and not column_info['primary_key']:
            validators.append("DataRequired()")

        # Проверка длины для строковых полей
        if column_info['type'] in ['string', 'varchar'] and column_info.get('length'):
            validators.append(f"Length(max={column_info['length']})")

        # Проверка email по имени поля
        if 'email' in column_info['name'].lower():
            validators.append("Email()")

        return validators

    def _to_camel_case(self, name):
        """Преобразует snake_case в CamelCase"""
        return ''.join(word.capitalize() for word in name.split('_'))

    def generate_model(self, class_name=None):
        """Генерирует код модели SQLAlchemy"""
        if not class_name:
            class_name = self._to_camel_case(self.table_name)

        columns_info = self._get_table_info()

        # Импорты
        imports = "\n".join(self.config["model"]["imports"])

        # Код модели
        model_code = [f"{imports}\n\n"]

        if not self.classic_sqlalchemy:
            model_code.append(f"db = SQLAlchemy()\n\n")

        model_code.append(f"class {class_name}({self.config['model']['base_class']}):\n")
        model_code.append(f"    __tablename__ = '{self.table_name}'\n")

        for column in columns_info:
            if column['name'] in self.config["model"]["exclude_columns"]:
                continue

            sqlalchemy_type = self._python_type_to_sqlalchemy(
                column['type'],
                column.get('length')
            )

            # Параметры колонки
            params = []
            if column['primary_key']:
                params.append("primary_key=True")
            if not column['nullable']:
                params.append("nullable=False")
            if column.get('default') is not None:
                params.append(f"default={column['default']}")

            params_str = ", ".join(params)

            # Для классического SQLAlchemy используем Column вместо db.Column
            if self.classic_sqlalchemy:
                if params_str:
                    model_code.append(f"    {column['name']} = Column({sqlalchemy_type}, {params_str})\n")
                else:
                    model_code.append(f"    {column['name']} = Column({sqlalchemy_type})\n")
            else:
                if params_str:
                    model_code.append(f"    {column['name']} = db.Column({sqlalchemy_type}, {params_str})\n")
                else:
                    model_code.append(f"    {column['name']} = db.Column({sqlalchemy_type})\n")

        model_code.append("\n    def __repr__(self):\n")
        model_code.append(f"        return f'<{class_name} {{self.id}}>'\n")

        return "".join(model_code)

    def _translate(self, text: str):
        if self.translate_labels:
            if not self._translator:
                self._translator = GoogleTranslator(source=self.label_original_language,
                                                    target=self.translate_labels)
            try:
                return self._translator.translate(text)
            except Exception:
                return text
        return text

    def generate_form(self, class_name=None):
        """Генерирует код формы WTForms"""
        if not class_name:
            form_class_name = self._to_camel_case(self.table_name) + "Form"
        else:
            form_class_name = class_name

        columns_info = self._get_table_info()

        # Импорты
        imports = "\n".join(self.config["form"]["imports"])

        # Код формы
        form_code = [f"{imports}\n\n"]
        form_code.append(f"class {form_class_name}({self.config['form']['base_class']}):\n")

        for column in columns_info:
            if column['name'] in self.config["model"]["exclude_columns"] or column['primary_key']:
                continue

            field_type = self._python_type_to_wtforms(column['type'])
            validators = self._generate_validators(column)

            # Лейбл поля (преобразуем snake_case в Normal Case)
            label_text = column['name'].replace('_', ' ').title()
            label = self._translate(label_text)

            # Параметры поля
            if validators:
                validators_str = ", ".join(validators)
                form_code.append(f"    {column['name']} = {field_type}('{label}', validators=[{validators_str}])\n")
            else:
                form_code.append(f"    {column['name']} = {field_type}('{label}')\n")

        form_code.append("    submit = SubmitField('Отправить')\n")
        meta = self.config["form"]["meta"]
        if meta:
            form_code.append('\n    class Meta:\n')
            for key, value in meta.items():
                form_code.append(f'        {key} = {value}\n')

        return "".join(form_code)

    def generate_file(self, output_file: Optional[str] = None, default_rename: bool = False,
                      only_model: bool = False, only_form: bool = False, tab: bool = False):
        """Генерирует файл с моделью и/или формой"""
        if default_rename:
            model_class_name = "Model"
            form_class_name = "Form"
        else:
            model_class_name = None
            form_class_name = None

        model_code = ""
        form_code = ""

        # Генерируем только то, что нужно
        if not only_form:
            model_code = self.generate_model(model_class_name)

        if not only_model:
            form_code = self.generate_form(form_class_name)

        if output_file:
            # Записываем в файл
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write('__all__ = []\n\n')

                if model_code:
                    file.write("# Модель SQLAlchemy\n")
                    if tab:
                        file.write(tab4(model_code))
                    else:
                        file.write(model_code)
                    if form_code:
                        file.write("\n\n")

                if form_code:
                    file.write("# Форма WTForms\n")
                    if tab:
                        file.write(tab4(form_code))
                    else:
                        file.write(form_code)

            print(f"Файл создан: {output_file}")

            # Информация о том, что было сгенерировано
            generated = []
            if model_code:
                generated.append("модель")
            if form_code:
                generated.append("форма")
            print(f"Сгенерировано: {', '.join(generated)}")

        else:
            # Выводим в консоль
            if model_code:
                print("# Модель SQLAlchemy")
                print(model_code)
                if form_code:
                    print("\n")

            if form_code:
                print("# Форма WTForms")
                print(form_code)

        return model_code, form_code


def generate(database: PathLike, table_name: str, output: Optional[PathLike] = None,
             config: Optional[PathLike] = None, default_rename: bool = False,
             only_model: bool = False, only_form: bool = False,
             classic_sqlalchemy: bool = False, tab: bool = False,
             translate_labels: Optional[str] = None, **kwargs):
    if isinstance(database, Path):
        database = f'sqlite:///{database}'
    elif not database.startswith(('sqlite:///', 'postgresql://', 'mysql://')):
        database = f'sqlite:///{database}'

    if not output:
        base_name = table_name
        if only_model:
            output = f"{base_name}_model.py"
        elif only_form:
            output = f"{base_name}_form.py"
        else:
            output = f"{base_name}.py"

    try:
        generator = ModelFormGenerator(
            config_path=config,
            database_url=database,
            table_name=table_name,
            default_rename=default_rename,
            only_model=only_model,
            only_form=only_form,
            classic_sqlalchemy=classic_sqlalchemy,
            translate_labels=translate_labels
        )
        generator.generate_file(
            output,
            default_rename,
            only_model,
            only_form,
            tab
        )

    except Exception as e:
        print(f"Ошибка {e.__class__.__name__}: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Генератор моделей Flask-SQLAlchemy и форм WTForms из таблиц БД'
    )

    only_group = parser.add_mutually_exclusive_group()

    # Основные аргументы
    parser.add_argument('database', help='URL базы данных (например: sqlite:///example.db)')
    parser.add_argument('table_name', help='Имя таблицы для генерации')
    parser.add_argument('output', nargs='?', help='Имя выходного файла')
    parser.add_argument('--config', '-c', help='Путь к JSON файлу конфигурации')

    # Опции
    parser.add_argument('--default-rename', '-r', action='store_true',
                        help='Переименовать классы в Model и Form')

    # Новые опции
    only_group.add_argument('--only-model', '-m', action='store_true',
                            help="Создать только модель")
    only_group.add_argument('--only-form', '-f', action='store_true',
                            help="Создать только форму")
    parser.add_argument('--classic-sqlalchemy', '-s', action='store_true',
                        help="Создать модель sqlalchemy вместо flask_sqlalchemy")
    parser.add_argument('--tab', '-t', action='store_true',
                        help="Заменить 4 пробела символом \\t")
    parser.add_argument('--translate-labels', '-l', help="Перевести labels в форме",
                        type=translate_validator)

    args = parser.parse_args()

    # Определяем имя выходного файла
    if not args.output:
        base_name = args.table_name
        if args.only_model:
            args.output = f"{base_name}_model.py"
        elif args.only_form:
            args.output = f"{base_name}_form.py"
        else:
            args.output = f"{base_name}.py"

    generate(**vars(args))


if __name__ == "__main__":
    main()
