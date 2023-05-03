import os
import uuid

from setuptools import find_packages
from distutils.core import setup

try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_requirements = parse_requirements(os.path.join(PROJECT_ROOT, 'requirements.txt'), session=uuid.uuid1())

# e.g. ['django', 'google-api-python-client']
requirements = [getattr(ir, 'requirement', str(getattr(ir, 'req', None))) for ir in install_requirements]

setup(
    name='cap-editor',
    version='0.1.5',
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
    license='MIT License',
    description='Wagtail CAP Editor can be run as standalone or integrated into website',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/wmo-raf/cap-editor',
    author='Grace Amondi',
    author_email='miswa.grace@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
