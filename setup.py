"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
Modified by Madoshakalaka@Github (dependency links added)
"""

# io.open is needed for projects that support Python 2.7
# It ensures open() defaults to text mode with universal newlines,
# and accepts an argument to specify the text encoding
# Python 3 only projects can skip this import
from io import open
from os import path

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="teachable-school-manager",  # Required
    version="1.0.0",  # Required
    description="Manage your Teachable school using the unofficial Teachable API",  # Optional
    long_description=long_description,  # Optional
    long_description_content_type="text/markdown",  # Optional (see note above)
    url="https://github.com/stezz/teachable-scripts",  # Optional
    author="Stefano Mosconi",  # Optional
    author_email="stefano.mosconi@gmail.com",  # Optional
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        # Indicate who your project is intended for
        "Intended Audience :: Users",
        "Topic :: Scripts :: Teachable",
        # Pick your license as you wish
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    keywords="scripts teachable",  # Optional
    packages=find_packages(exclude=["contrib", "docs", "tests"]),  # Required
    python_requires=">3.7, <4",
    install_requires=[
        "jinja2==2.11.2",
        "pyexcel==0.6.6",
        "pyexcel-xlsx==0.6.0",
        "pytablewriter[excel,html]==0.58.0",
        "requests==2.25.0",
    ],  # Optional
    extras_require={"dev": []},  # Optional
    dependency_links=[],
    data_files=[("etc", ["etc/config_example.ini", "etc/logconf.ini"])],  # Optional
    entry_points={"console_scripts": ["remind=scripts.remind:main"]},  # Optional
    #scripts=["scripts/remind.py"],  # Optional
    project_urls={  # Optional
        "Bug Reports": "https://github.com/stezz/teachable-scripts/issues",
#        "Funding": "https://donate.pypi.org",
#        "Say Thanks!": "http://saythanks.io/to/example",
        "Source": "https://github.com/stezz/teachable-scripts/",
    },
)
