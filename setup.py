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
    name = 'forecast',
    version='1.1.13',
    description = 'forecasts',
    #long_description = README,
    #long_description_content_type = "text/markdown",  
    license = "MIT",
    #url = 'https://github.com/piccolomo/plotext',
    packages = find_packages(),
    #python_requires = "==3.11.4",
    #include_package_data = True,
    install_requires = ["pandas", "numpy", "scipy", "matplotlib", "prophet", "pmdarima", "scikit-learn"],
    classifiers = []
    )
