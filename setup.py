from setuptools import setup, find_packages

setup(
    name='cf',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': [
            'cf = client.cli:cf',
        ],
    },
)