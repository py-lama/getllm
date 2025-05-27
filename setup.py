from setuptools import setup, find_packages

setup(
    name="pyllm",
    version="0.1.3",
    description="Python LLM operations service for the DevLama ecosystem",
    author="Tom Sapletta",
    author_email="info@softreck.dev",
    license="Apache-2.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0,<3.0.0",
        "bs4>=0.0.1,<0.0.2",
        "beautifulsoup4>=4.12.2,<5.0.0",
        "python-dotenv>=1.0.0,<2.0.0",
    ],
    entry_points={
        'console_scripts': [
            'pyllm=pyllm.cli:main',
        ],
    },
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov',
            'tox',
            'flake8',
            'black',
        ],
    },
    python_requires='>=3.8,<4.0',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/tom-sapletta-com/py-lama",
    project_urls={
        "Bug Tracker": "https://github.com/tom-sapletta-com/py-lama/issues",
    },
)
