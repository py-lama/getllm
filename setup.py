from setuptools import setup, find_packages

setup(
    name="pyllm",
    version="0.1.0",
    description="A package for managing LLM models with Ollama integration",
    author="Tom Sapletta",
    license="Apache-2.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "bs4",
        "python-dotenv",
        "questionary",
    ],
    entry_points={
        'console_scripts': [
            'pyllm=pyllm.cli:main',
        ],
    },
    extras_require={
        'dev': [
            'pytest',
            'pytest-cov',
            'tox',
            'flake8',
            'black',
        ],
    },
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
