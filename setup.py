import re
from setuptools import setup, find_packages


def find_version():
    for line in open("django-api/__init__.py"):
        if line.startswith("__version__"):
            return re.match(r"""__version__\s*=\s*(['"])([^'"]+)\1""", line).group(2)

modules = ['tornado', 'torndsession', 'passlib', 'ujson', 'six']
setup(
    name='tornkts',
    version=find_version(),
    description='Library for creating easy django api',
    long_description='Library for creating easy django api',

    author='Alexander Opryshko',
    author_email='alexopryshko@yandex.ru',
    url='https://github.com/alexopryshko/django-api',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='django-api setuptools development',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=[
        'Django>=1.10',
        'psycopg2>=2.6.2'
    ]
)
