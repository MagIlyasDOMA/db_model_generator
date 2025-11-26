from setuptools import setup, find_packages

base_requirements = ['sqlalchemy==2.0.44']
flask_requirements = ['flask~=3.1.1', 'flask-sqlalchemy==3.1.1', 'flask-wtf==1.2.2', 'wtforms==3.2.1']

extras_require = dict(
    base=base_requirements,
    flask=base_requirements + flask_requirements,
    all=base_requirements + flask_requirements
)

setup(
    name='db-model-generator',
    version='1.0.1',
    packages=find_packages(),
    author="Маг Ильяс DOMA (MagIlyasDOMA)",
    author_email='magilyas.doma.09@list.ru',
    description="Генератор моделей sqlalchemy из таблиц базы данных",
    install_requires=extras_require['all'],
    python_requires='>=3.10',
    extras_require=extras_require,
    entry_points=dict(
        console_scripts=[
            "db-model-generator=db_model_generator.generator:main",
        ]
    ),
    url="https://github.com/MagIlyasDOMA/db_model_generator",
    project_urls=dict(
        Source="https://github.com/MagIlyasDOMA/db_model_generator",
        Documentation="https://magilyasdoma.github.io/db_model_generator",
    ),

)
