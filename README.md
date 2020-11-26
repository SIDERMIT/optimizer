[![Build Status](https://travis-ci.com/SIDERMIT/optimizer.svg?branch=master)](https://travis-ci.com/SIDERMIT/optimizer)

[![Coverage Status](https://coveralls.io/repos/github/SIDERMIT/optimizer/badge.svg?branch=master)](https://coveralls.io/github/SIDERMIT/optimizer?branch=master)

# Optimizer
Package to design optimal public transport networks in parameterizable cities

# Package documentation

Link: https://sidermit.github.io/optimizer/

# Usage example 

Link examples: https://github.com/SIDERMIT/optimizer/tree/master/examples

# Python requirements

Project works with python 3.7 or higher

# Build and install package

To build the package, make sure to delete the folder sidermit.egg-info and then run `python setup.py sdist` in the root folder of sidermit package.

To install the package run `python -m pip install <path_to_package_file>`

Example: `python -m pip install .\dist\sidermit-v1.0.0.tar.gz`

# Upload package to PyPi

Reference: https://medium.com/@joel.barmettler/how-to-upload-your-python-package-to-pypi-65edc5fe9c56

## Steps to upload package
1. Create an account at https://pypi.org/account/register/
2. Create a source distribution: `python setup.py sdist`
3. Install package twine: `pip install twine`
4. Upload package: `twine upload dist/*`
5. You will be asked to provide username and password
6. Visit your website package: https://pypi.org/project/sidermit 

## Install package

```
pip install sidermit
```
to upgrade package add option `--upgrade`

## Upgrade package in pip repository

Process:
1. Update code 
2. Push changes to github repository
3. Create new release on github
4. Adapt setup.py (new download_url and version) and commit changes
5. Remove `dist` folder
1. Install `twine` library
6. run twine command:

```
python setup.py sdist
twine upload dist/*
```
