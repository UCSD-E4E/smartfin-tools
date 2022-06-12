from setuptools import setup, find_packages

setup(
    name='smartfin-tools',
    author='UCSD Engineers for Exploration',
    author_email='e4e@eng.ucsd.edu',
    install_requires=[
        'pandas',
        'numpy',
    ],
    packages=find_packages()
)