__author__ = 'lobocv'
import os
import shutil
import glob

from distutils.core import setup
from eventdispatcher import __version__
try:
    from Cython.Build import cythonize
    COMPILE = True
except ImportError:
    def cythonize(*args, **kwargs):
        return []
    COMPILE = False


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
    ext_modules=cythonize(glob.glob('eventdispatcher/*.py')),
    classifiers=[],
)


if os.path.exists('./build') and COMPILE:
    shutil.rmtree('./build')
    for f in glob.glob('eventdispatcher/*.c'):
        os.remove(f)
