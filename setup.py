from setuptools import setup, find_packages

setup(
    name='cell-flow-tracking',
    version='0.1.0',
    packages=find_packages(include=['src', 'src.*', 'client', 'client.*']),
    install_requires=[
        'click',
        # other dependencies
    ],
    entry_points={
        'console_scripts': [
            'cf = client.cli:cf',
        ],
    },
)