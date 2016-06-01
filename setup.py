import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.md')) as f:
    CHANGES = f.read()

requires = [
    'pybluez',
    'redis',
    'requests'
]

setup(name='smartgympi',
      version='0.1',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python"
      ],
      author='Nerds Wit Attitudes',
      author_email='',
      keywords='pybluez',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='smartgympi',
      install_requires=requires
      )
