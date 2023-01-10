'''Smartfin Tools setup
'''
from setuptools import find_packages, setup

from smartfin import __version__

setup(
    name='smartfin-tools',
    author='UCSD Engineers for Exploration',
    author_email='e4e@eng.ucsd.edu',
    version=__version__,
    install_requires=[
        'pandas',
        'numpy',
        "pyserial",
        'matplotlib',
        'pytest',
    ],
    entry_points={
        'console_scripts': [
            'smartfinDownloader = smartfin.smartfinDownloader:main',
            'sfDownloader = smartfin.sfDownloader:sfDownloader',
            'sfFlogDownloader = smartfin.sfDownloader:flogDownloader',
            'sfPlotter = smartfin.sfPlotter:main',
            'sfConvert = smartfin.sfConvert:main',
        ]
    },
    packages=find_packages(),
    extras_require={
        'dev': [
            'pytest',
            'coverage',
            'pylint',
            'wheel',
        ]
    },
)
