from setuptools import setup, find_packages


requirements = [
        "blocklib >= 0.1.8",
        "click >= 7.1.1",
        "clkhash >= 0.16.0b1",
        "jsonschema >= 3.2.0",
        "requests >= 2.22.0",
        "minio >= 7.0.0",
        "bashplotlib >= 0.6.5",
        "retrying>=1.3.3",
        "ijson>=3.1.1",
    ]

with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name="anonlink-client",
    version='0.1.5',
    description='Client side tool for clkhash and blocklib',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/data61/anonlink-client',
    license='Apache',
    install_requires=requirements,
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov', 'mock'],
    extras_require={
        "tutorials": ['numpy', 'pandas', 'anonlink']
    },
    packages=find_packages(exclude=['tests']),
    package_data={'anonlinkclient': ['data/*.csv', 'data/*.json', 'schemas/*.json']},
    project_urls={
        'Documentation': 'https://github.com/data61/anonlink-client',
        'Source': 'https://github.com/data61/anonlink-client',
        'Tracker': 'https://github.com/data61/anonlink-client/issues',
    },
    entry_points={
        'console_scripts': [
            'anonlink = anonlinkclient.cli:cli'
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Security :: Cryptography",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
)
