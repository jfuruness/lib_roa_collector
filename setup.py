from setuptools import setup, find_packages
import sys

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# https://stackoverflow.com/a/58534041/8903959
setup(
    name='lib_roa_collector',
    author="Justin Furuness",
    author_email="jfuruness@gmail.com",
    version="0.0.1",
    url='https://github.com/jfuruness/lib_roa_collector.git',
    license="BSD",
    description="Downloads historical ROAs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["Furuness", "roas", "ROA", "ROAs", "RPKI"],
    include_package_data=True,
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=[
        "pytest",
    ],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3'],
    entry_points={},
)
