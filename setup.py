import re
from os import path
from setuptools import setup, find_packages

BASE_DIR = path.abspath(path.dirname(__file__))


def find_version():
    for line in open(path.join(BASE_DIR, 'django_serializer/__init__.py')):
        if line.startswith('__version__'):
            return re.match(r"""__version__\s*=\s*(['"])([^'"]+)\1""",
                            line).group(2)


setup(
    name='django-serializer',
    version=find_version(),
    description='Library for creating simple django api',
    long_description='Library for creating simple django api',

    author='Alexander Opryshko',
    author_email='alexopryshko@yandex.ru',
    url='https://github.com/alexopryshko/django-serializer',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='django-serializer setuptools development',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=[
        'Django>=2.1',
        'marshmallow>=3.5.0',
        'apispec>=3.3.0',
    ]
)
