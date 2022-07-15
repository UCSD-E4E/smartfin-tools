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
    ],
    entry_points={
        'console_scripts': [
            'smartfinDownloader = smartfin.smartfinDownloader:main',
            'sfDownloader = smartfin.sfDownloader:main',
            'sfPlotter = smartfin.sfPlotter:main',
        ]
    },
    packages=find_packages()
)