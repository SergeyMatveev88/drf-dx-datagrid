from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='drf_dx_datagrid',
    version='0.4.2',
    packages=find_packages(),
    url='https://github.com/SergeyMatveev88/drf-dx-datagrid',
    license='MIT',
    author='SergeyMatveev88',
    author_email='dazranagon@yandex.ru',
    description='This package provides easy integration between Django REST framework and DevExtreme Data Grid. It handles grouping, paging, filtering, aggregating and ordering on serverside.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['djangorestframework'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Framework :: Django'
    ],
    python_requires='>=3.5',
)
