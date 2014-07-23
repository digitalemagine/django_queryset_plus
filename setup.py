from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup


setup(
    name='django_queryset_plus',
    version='0.1',
    author='Stefano Crosta',
    author_email='stefano@digitalemagine.com',
    packages=['queryset_plus'],
    url='',
    license='See LICENSE.txt',
    description='',
    long_description=open('README.rst').read(),
)
