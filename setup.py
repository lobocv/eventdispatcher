import os
from setuptools import setup

with open(os.path.join('.', 'eventdispatcher', 'version.py')) as version_file:
    __version__ = ''
    exec(version_file.read())
    assert len(__version__) > 0


setup(
    name='eventdispatcher',
    packages=['eventdispatcher'],
    version=__version__,
    description="An event dispatcher framework inspired by the Kivy project.",
    author="Calvin Lobo",
    author_email='calvinvlobo@gmail.com',
    url='https://github.com/lobocv/eventdispatcher',
    download_url='https://github.com/lobocv/eventdispatcher/tarball/%s' % __version__,
    keywords=['event', 'dispatcher', 'dispatching', 'kivy', 'observer', 'framework', 'property', 'properties'],
    install_requires=['future',
                      'numpy'
                      ],
)