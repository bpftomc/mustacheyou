from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mustacheyou",
    version="0.0.1",
    author="B. P. Flannery",
    author_email="bpflannery@tomchesnutt.com",
    description="Copies a template folder structure and interpolates values based on YAML configuration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/mustacheyou",
    packages=find_packages(exclude=('tests', 'docs')),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        'chevron',
    ],
    scripts=['bin/mustacheyou'],
)
