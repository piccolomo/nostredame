# /usr/bin/env python3
import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
#README = (HERE / "README.md").read_text()

setup(
    author = "Savino Piccolomo",
    author_email = "piccolomo@gmail.com",
    name = 'cassandra',
    version='1.3.1',
    description = 'forecasts',
    #long_description = README,
    #long_description_content_type = "text/markdown",  
    license = "MIT",
    #url = 'https://github.com/piccolomo/plotext',
    packages = find_packages(),
    python_requires = ">=3.10.0, <=3.11.4",
    #include_package_data = True,
    #install_requires = ["pandas >= 2.0.0", "numpy >= 1.24.0", "scipy >= 1.10.0", "matplotlib >= 3.7.0", "prophet >= 1.1.0", "pmdarima >= 2.0.0"],
    classifiers = []
    )
