from setuptools import setup, find_packages

setup(
    name='sidermit',
    packages=find_packages(exclude=['tests', 'examples']),
    version='0.0.1',
    license='gpl-3.0',
    description='optimize public transport system on a city graph based on one CBD and zones',
    author='Felipe Vera',
    author_email='fvera@transapp.cl',
    url='https://github.com/SIDERMIT/optimizer',
    download_url='https://github.com/SIDERMIT/optimizer/archive/v0.0.1.tar.gz',
    keywords=['public transport', 'optimize'],
    install_requires=[
        'pandas>=1.0.5',
        'matplotlib>=3.3.0',
        'networkx>=2.4',
        'scipy>=1.5.2',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7'
    ]
)
