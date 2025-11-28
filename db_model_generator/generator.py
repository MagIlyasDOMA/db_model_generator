#!/usr/bin/env python3
"""
Скрипт для автоматической генерации моделей Flask-SQLAlchemy и форм WTForms
на основе таблиц базы данных.
"""

import argparse, sys
from pathlib import Path
from typing import Union
from pyundefined import UndefinedType, undefined
from db_model_generator.constants import LANGUAGES
from db_model_generator.core import ModelFormGenerator
from db_model_generator.typings import PathLikeOrNone, Optional, LanguageCodeType, NullStr

__all__ = ['generate']


def translate_validator(language_code: str) -> str:
    if not isinstance(language_code, str):
        raise argparse.ArgumentTypeError("Language code must be a string")
    elif language_code not in LANGUAGES.keys():
        raise argparse.ArgumentTypeError(f"Language code {language_code} is not supported")
    return language_code


def generate(database: PathLikeOrNone, table_name: str, output: PathLikeOrNone = None,
             config: PathLikeOrNone = None, default_rename: bool = False,
             only_model: bool = False, only_form: bool = False,
             classic_sqlalchemy: bool = False, tab: bool = False,
             translate_labels: Optional[LanguageCodeType] = None,
             label_original_language: Optional[LanguageCodeType] = None,
             log_mode: bool = False, env: Union[PathLikeOrNone, UndefinedType] = None,
             submit: NullStr = None):
    """
   Генерирует модели SQLAlchemy и формы WTForms на основе таблицы базы данных.

   :param database: URL базы данных для подключения
   :type database: str
   :param table_name: Имя таблицы для генерации моделей и форм
   :type table_name: str
   :param output: Путь к выходному файлу для сохранения результата
   :type output: str или None
   :param config: Путь к JSON файлу конфигурации с настройками генерации
   :type config: str или None
   :param default_rename: Переименовать классы в Model и Form
   :type default_rename: bool
   :param only_model: Генерировать только модель SQLAlchemy
   :type only_model: bool
   :param only_form: Генерировать только форму WTForms
   :type only_form: bool
   :param classic_sqlalchemy: Использовать классический SQLAlchemy вместо Flask-SQLAlchemy
   :type classic_sqlalchemy: bool
   :param tab: Использовать символ табуляции \\t вместо пробелов для форматирования
   :type tab: bool
   :param translate_labels: Код языка для перевода labels в форме (например: 'ru', 'es', 'fr')
   :type translate_labels: str или None
   :param label_original_language: Исходный язык labels для перевода (по умолчанию 'en')
   :type label_original_language: str
   :param log_mode: Включить режим логирования для отладки
   :type log_mode: bool
   :param env: Путь к файлу окружения (.env) для загрузки переменных
   :type env: str или None
   :param submit: Текст для кнопки submit в форме (если None, кнопка не добавляется)
   :type submit: str или None

   :raises ValueError: Если не указаны обязательные параметры database или table_name
   :raises ConnectionError: Если не удается подключиться к указанной базе данных
   :raises TableNotFoundError: Если указанная таблица не существует в базе данных
    """

    try:
        generator = ModelFormGenerator(
            config_path=config,
            database_url=database,
            table_name=table_name,
            default_rename=default_rename,
            only_model=only_model,
            only_form=only_form,
            classic_sqlalchemy=classic_sqlalchemy,
            translate_labels=translate_labels,
            output_path=output,
            tab=tab,
            label_original_language=label_original_language,
            log_mode=log_mode,
            env=env,
            submit=submit
        )
        generator.generate_file()
    except Exception as e:
        print(f"Ошибка {e.__class__.__name__}: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    from db_model_generator import __version__

    parser = argparse.ArgumentParser(description='Генератор моделей Flask-SQLAlchemy и форм WTForms из таблиц базы данных')

    only_group = parser.add_mutually_exclusive_group()

    # Основные аргументы
    parser.add_argument('database', nargs='?', help='URL базы данных (например: sqlite:///example.db)')
    parser.add_argument('table_name', nargs='?', help='Имя таблицы для генерации')
    parser.add_argument('output', nargs='?', help='Имя выходного файла')
    parser.add_argument('config', nargs='?', help='Путь к JSON файлу конфигурации')

    # Опции
    parser.add_argument('--database', dest='database', help='URL базы данных (например: sqlite:///example.db)')
    parser.add_argument('--table-name', dest='table_name', help='Имя таблицы для генерации')
    parser.add_argument('--output', dest='output', help='Имя выходного файла')
    parser.add_argument('--config', '-c', dest='config', help='Путь к JSON файлу конфигурации')
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
    parser.add_argument('--label-original-language', help="Оригинальный язык labels",
                        type=translate_validator, default='en')
    parser.add_argument('--log-mode', '--log', '--verbosity', '-V', '-L',
                        dest='log_mode', action='store_true', help="Включает логирование")
    parser.add_argument('--version', '-v', action='version', version=__version__)
    parser.add_argument('--env', '-e', nargs='?', const=None, default=undefined,
                        help="Путь к файлу")
    parser.add_argument('--submit-button', '--submit', '-b', const="Отправить",
                        help="Добавить кнопку submit в форму", dest='submit', nargs='?')

    args = parser.parse_args()

    generate(**vars(args))


if __name__ == "__main__":
    main()
