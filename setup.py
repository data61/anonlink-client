from setuptools import setup, find_packages


requirements = [
        "anonlink >= 0.12.5",
        "blocklib >= 0.1.3",
        "click >= 7.1.1",
        "clkhash >= 0.16.0a1",
        "jsonschema >= 3.2.0",
        "numpy >= 1.18.1",
        "pandas >= 1.0.1",
        "pytest >= 5.3.5",
        "requests >= 2.22.0",
    ]

with open('README.md', 'r', encoding='utf-8') as f:
        readme = f.read()

setup(
    name="anonlink-client",
    version='0.1.3',
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
