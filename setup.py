__author__ = 'lobocv'

from distutils.core import setup
from eventdispatcher import __version__


setup(
    name='eventdispatcher',
    packages=['eventdispatcher'],
    version=__version__,
    description="An event dispatcher framework inspired by the Kivy project.",
    author='Calvin Lobo',
    author_email='calvinvlobo@gmail.com',
    url='https://github.com/lobocv/eventdispatcher',
    download_url='https://github.com/lobocv/eventdispatcher/tarball/%s' % __version__,
    keywords=['event', 'dispatcher', 'dispatching', 'kivy', 'observer', 'framework', 'property', 'properties'],
    classifiers=[],
)