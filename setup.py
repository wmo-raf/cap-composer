from setuptools import setup, find_packages

setup(
    name='capeditor',
    version='0.1.3',
    description='Wagtail CAP Editor can be used as standalone or integrated into website',
    author='Grace Amondi',
    author_email='miswa.grace@gmail.com',
    install_requires=[
        'Django>=4.0.0',
        'djangorestframework-xml>=2.0.0',
        'six>=1.16.0',
        'wagtail>=4.0.0',
        'wagtail-cache>=2.2.0',
        'psycopg2-binary>=2.9.5',
        'wagtail-lazyimages>=0.1.5'
    ],
    include_package_data=True,
    packages=find_packages(),
)
