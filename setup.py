from setuptools import setup, find_packages

setup(
    name='smartfin-tools',
    author='UCSD Engineers for Exploration',
    author_email='e4e@eng.ucsd.edu',
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
    packages=find_packages()
)