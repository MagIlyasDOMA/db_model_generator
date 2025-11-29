import json
from dataclasses import dataclass
from pathlib import Path
from warnings import warn
from dotenv import dotenv_values
from deep_translator import GoogleTranslator
from tab4 import tab4
from sqlalchemy import create_engine, MetaData, Table, inspect
from sqlalchemy.types import String, Integer, Float, Text, Boolean, DateTime, Date
from pyundefined import undefined
from .typings import *
from .warnings import MeaninglessArgumentWarning


@dataclass
class Environment:
    config_path: PathLikeOrNone = None
    database_url: NullStr = None
    table_name: NullStr = None
    output_path: NullStr = None
    default_rename: bool = False
    only_model: bool = False
    only_form: bool = False
    classic_sqlalchemy: bool = False
    tab: bool = False
    translate_labels: Optional[LanguageCodeType] = None
    label_original_language: LanguageCodeType = 'en'
    log_mode: bool = False
    submit: NullStr = None

    def __post_init__(self):
        self.__errors()
        self.__warnings()

    def __errors(self):
        if self.only_model and self.only_form:
            raise ValueError('only_model and only_form are mutually exclusive')

    @property
    def __label_original_language(self):
        return self.label_original_language != 'en'

    def __warnings(self):
        if ((self.__label_original_language and not self.translate_labels) or
                (self.only_model and self.__label_original_language)):
            warn('label_original_language is meaningless', MeaninglessArgumentWarning)
        if self.only_model and self.translate_labels:
            warn('translate_labels is meaningless', MeaninglessArgumentWarning)
        if self.only_model and self.submit:
            warn('submit is meaningless', MeaninglessArgumentWarning)



class ModelFormGenerator:
    """Генератор моделей и форм на основе таблиц БД"""

    _translator: Optional[GoogleTranslator] = None
    environment: Environment

    def __init__(self,
                 config_path: PathLikeOrNone = None,
                 database_url: NullStr = None,
                 table_name: NullStr = None,
                 output_path: NullStr = None,
                 default_rename: NullBool = None,
                 only_model: NullBool = None,
                 only_form: NullBool = None,
                 classic_sqlalchemy: NullBool = None,
                 tab: NullBool = None,
                 translate_labels: Optional[LanguageCodeType] = None,
                 label_original_language: Optional[LanguageCodeType] = None,
                 log_mode: NullBool = None,
                 env: PathLikeOrNone = None,
                 submit: NullStr = None):
        self._init_environment(env)
        if not config_path:
            config_path = self.environment.config_path
        self.config = self._load_config(config_path)
        self._init_main_args(self.__format_kwargs(
            database_url=database_url,
            table_name=table_name,
            default_rename=default_rename,
            only_model=only_model,
            only_form=only_form,
            classic_sqlalchemy=classic_sqlalchemy,
            tab=tab,
            translate_labels=translate_labels,
            label_original_language=label_original_language,
            output_path=output_path,
            log_mode=log_mode,
            submit=submit
        ))
        self.engine = create_engine(self.database_url)
        self.metadata = MetaData()

    def _init_environment(self, env_path: PathLikeOrNone = None):
        if env_path is not undefined:
            env = dict(dotenv_values(env_path))
            lower_dict = dict()
            for key, value in env.items():
                if isinstance(value, str):
                    if value.lower() == 'true' or value == '1':
                        value = True
                    elif value.lower() == 'false' or value == '0':
                        value = False
                lower_dict[key.lower()] = value
            lower_dict = self.__fix_args_keys(lower_dict)
            self.environment = Environment(**lower_dict)
        else:
            self.environment = Environment()

    def log(self, *values: str, sep: str = ' ', end: str = '\n', file=None, flush: bool = False):
        if self.log_mode:
            print(*values, sep=sep, end=end, file=file, flush=flush)

    @staticmethod
    def __format_kwargs(**kwargs) -> dict:
        return {key: value for key, value in kwargs.items() if value is not None}

    def __output_path(self, path: PathLikeOrNone = None) -> Path:
        if path:
            return Path(path)
        if self.only_model:
            suffix = '_model'
        elif self.only_form:
            suffix = '_form'
        else:
            suffix = ''
        return Path(self.table_name + suffix + '.py')

    @staticmethod
    def __database_url(url: str) -> str:
        if not url:
            raise ValueError('database_url is required')
        if url.startswith('sqlite:///'):
            path = url.replace('sqlite:///', '')
            if not Path(path).exists():
                raise FileNotFoundError('SQLite database does not exist')
        return url

    @staticmethod
    def __table_name(table_name: str) -> str:
        if not table_name:
            raise ValueError('table_name is required')
        return table_name

    def _init_main_args(self, kwargs):
        """Инициализирует основные аргументы до загрузки конфигурации"""
        args = self.config['arguments']
        for key, value in kwargs.items():
            if value:
                args[key] = value
        self.database_url = self.__database_url(args['database_url'])
        self.table_name = self.__table_name(args['table_name'])
        self.default_rename = args['default_rename']
        self.only_model = args['only_model']
        self.only_form = args['only_form']
        self.classic_sqlalchemy = args['classic_sqlalchemy']
        self.tab = args['tab']
        self.translate_labels = args['translate_labels']
        self.label_original_language = args['label_original_language']
        self.output_path: Path = self.__output_path(args['output_path'])
        self.log_mode = args['log_mode']
        self.submit = args['submit']

    @staticmethod
    def __get_classic_sqlalchemy(default, config_path: PathLikeOrNone = None) -> bool:
        if config_path and Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                try:
                    return json.load(f)['arguments']['classic_sqlalchemy']
                except KeyError:
                    pass
        return default['arguments']['classic_sqlalchemy']

    def _load_config(self, config_path):
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
                "database_url": self.environment.database_url,
                "table_name": self.environment.table_name,
                "default_rename": self.environment.default_rename,
                "only_model": self.environment.only_model,
                "only_form": self.environment.only_form,
                "classic_sqlalchemy": self.environment.classic_sqlalchemy,
                "tab": self.environment.tab,
                "translate_labels": self.environment.translate_labels,
                "label_original_language": self.environment.label_original_language,
                "output_path": self.environment.output_path,
                "log_mode": self.environment.log_mode,
                "submit": self.environment.submit
            }
        }

        # Если используется классический SQLAlchemy, меняем настройки
        if getattr(self, 'classic_sqlalchemy',
                                     self.__get_classic_sqlalchemy(default_config, config_path)):
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
        if config_path:
            if Path(config_path).exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    user_config['arguments'] = self.__fix_args_keys(user_config.get('arguments', {}))
                    self._update_config(default_config, user_config)
            else:
                warn("Конфигурационного файла не существует", UserWarning, 3)

        return default_config

    @staticmethod
    def __fix_args_keys(args: dict):
        arguments = args.copy()
        if 'database' in arguments:
            arguments['database_url'] = arguments['database']
            del arguments['database']
        if 'output' in arguments:
            arguments['output_path'] = arguments['output']
            del arguments['output']
        return arguments

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

    @staticmethod
    def _generate_validators(column_info):
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

    @staticmethod
    def _to_camel_case(name):
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

        model_code.append(f"__all__ = ['{class_name}']\n\n\n")
        model_code.append(f"class {class_name}({self.config['model']['base_class']}):\n")
        model_code.append(f"\t__tablename__ = '{self.table_name}'\n")

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
                    model_code.append(f"\t{column['name']} = Column({sqlalchemy_type}, {params_str})\n")
                else:
                    model_code.append(f"\t{column['name']} = Column({sqlalchemy_type})\n")
            else:
                if params_str:
                    model_code.append(f"\t{column['name']} = db.Column({sqlalchemy_type}, {params_str})\n")
                else:
                    model_code.append(f"\t{column['name']} = db.Column({sqlalchemy_type})\n")

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
        form_code = [f"{imports}\n\n", f"__all__ = ['{form_class_name}']\n\n\n", f"class {form_class_name}({self.config['form']['base_class']}):\n"]

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
                form_code.append(f"\t{column['name']} = {field_type}('{label}', validators=[{validators_str}])\n")
            else:
                form_code.append(f"\t{column['name']} = {field_type}('{label}')\n")

        if self.submit is not None:
            form_code.append(f"    submit = SubmitField(\"{self.submit}\")\n")
        meta = self.config["form"]["meta"]
        if meta:
            form_code.append('\n    class Meta:\n')
            for key, value in meta.items():
                form_code.append(f'\t\t{key} = {value}\n')

        return "".join(form_code)

    def generate_file(self):
        """Генерирует файл с моделью и/или формой"""
        if self.default_rename:
            model_class_name = "Model"
            form_class_name = "Form"
        else:
            model_class_name = None
            form_class_name = None

        model_code = ""
        form_code = ""

        # Генерируем только то, что нужно
        if not self.only_form:
            model_code = self.generate_model(model_class_name)

        if not self.only_model:
            form_code = self.generate_form(form_class_name)

        if self.output_path:
            # Записываем в файл
            with open(self.output_path, 'w', encoding='utf-8') as file:
                file.write('__all__ = []\n\n')

                if model_code:
                    file.write("# Модель SQLAlchemy\n")
                    if not self.tab:
                        file.write(tab4(model_code))
                    else:
                        file.write(model_code)
                    if form_code:
                        file.write("\n\n")

                if form_code:
                    file.write("# Форма WTForms\n")
                    if not self.tab:
                        file.write(tab4(form_code))
                    else:
                        file.write(form_code)

            self.log(f"Файл создан: {self.output_path}")

            # Информация о том, что было сгенерировано
            generated = []
            if model_code:
                generated.append("модель")
            if form_code:
                generated.append("форма")
            self.log(f"Сгенерировано: {', '.join(generated)}")

        else:
            # Выводим в консоль
            if model_code:
                self.log("# Модель SQLAlchemy")
                self.log(model_code)
                if form_code:
                    self.log("\n")

            if form_code:
                self.log("# Форма WTForms")
                self.log(form_code)

        return model_code, form_code
