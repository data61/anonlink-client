from setuptools import setup, find_packages


requirements = [
        "anonlink >= 0.12.5",
        "clkhash >= 0.14.0",
        "jsonschema >= 3.0.2",
        "numpy >= 1.17.0",
        "pandas >= 0.25.2",
        "pytest >= 5.2.1",
        "requests >= 2.22.0",
    ]

with open('README.md', 'r', encoding='utf-8') as f:
        readme = f.read()

setup(
    name="anonlink-client",
    version='0.1.1',
    description='Client side tool for clkhash and blocklib',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/data61/anonlink-client',
    license='Apache',
    install_requires=requirements,
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
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
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