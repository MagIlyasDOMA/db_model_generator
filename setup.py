import sys, os, shutil, time
from setuptools import setup, find_packages


def clean():
    if '--clean' in sys.argv:
        sys.argv.remove('--clean')
        # Удаляем build, dist и .egg-info директории
        dirs_to_remove = ['build', 'dist']
        # Добавляем .egg-info директории
        dirs_to_remove.extend([d for d in os.listdir('.')
                               if d.endswith('.egg-info')])

        for dir_name in dirs_to_remove:
            if os.path.exists(dir_name):
                shutil.rmtree(dir_name)
                print(f"Удалена директория {dir_name}")
        time.sleep(0.5)


with open('README.md', encoding='utf-8') as file:
    readme = file.read()

clean()
setup(
    name='db-model-generator',
    version='1.4.1',
    packages=find_packages(),
    author="Маг Ильяс DOMA (MagIlyasDOMA)",
    author_email='magilyas.doma.09@list.ru',
    description="Генератор моделей sqlalchemy из таблиц базы данных",
    long_description=readme,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords=["sqlalchemy", "wtforms", "code-generation", "database", "models", "forms"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Framework :: Flask",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
        "Topic :: Database",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        "sqlalchemy==2.0.44",
        "deep-translator>=1.11.4",
        "tab4>=0.1.0",
        "python-dotenv>=1.0.0",
        "undefined-python>=1.0.0",
        "typing-extensions>=4.0.0; python_version<'3.8'",
    ],
    python_requires='>=3.10',
    extras_require={
        'base': [
            "sqlalchemy==2.0.44",
            "deep-translator>=1.11.4",
            "tab4>=0.1.0",
            "python-dotenv>=1.0.0",
            "undefined-python>=1.1.0",
            "typing-extensions>=4.0.0; python_version<'3.8'",
        ],
        'flask': [
            "flask>=3.1.1,<4.0.0",
            "flask-sqlalchemy==3.1.1",
            "flask-wtf==1.2.2",
            "wtforms==3.2.1",
        ],
        'all': [
            "sqlalchemy==2.0.44",
            "deep-translator>=1.11.4",
            "tab4>=0.1.0",
            "python-dotenv>=1.0.0",
            "undefined-python>=1.0.0",
            "typing-extensions>=4.0.0; python_version<'3.8'",
            "flask>=3.1.1,<4.0.0",
            "flask-sqlalchemy==3.1.1",
            "flask-wtf==1.2.2",
            "wtforms==3.2.1",
        ],
    },
    entry_points={
        'console_scripts': [
            "db-model-generator=db_model_generator.generator:main",
        ]
    },
    url="https://github.com/MagIlyasDOMA/db_model_generator",
    project_urls={
        "Homepage": "https://github.com/MagIlyasDOMA/db_model_generator",
        "Documentation": "https://magilyasdoma.github.io/db_model_generator",
        "Repository": "https://github.com/MagIlyasDOMA/db_model_generator",
        "Issues": "https://github.com/MagIlyasDOMA/db_model_generator/issues",
    },
)