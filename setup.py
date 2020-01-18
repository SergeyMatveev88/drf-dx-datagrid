from setuptools import setup, find_packages

setup(
    name='drf_dx_datagrid',
    version='0.1',
    packages=find_packages(),
    url='https://github.com/SergeyMatveev88/drf-dx-datagrid',
    license='MIT',
    author='Sergey Matveev',
    author_email='dazranagon@yandex.ru',
    description='Serverside realisation of grouping, filtering and sorting for DevExtreme datagrid on django rest framework',
    install_requires=['djangorestframework']
)
