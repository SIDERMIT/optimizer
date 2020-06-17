from setuptools import setup, find_packages

setup(
    install_requires=[
        'pandas==1.0.4',
        'matplotlib==3.2.1'
    ],
    packages=find_packages(exclude=[]),
)
