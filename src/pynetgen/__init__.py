"""A Python module for generating random network flows problem instances.

Importing the pynetgen module allows the netgen_generate and grid_generate
methods to be called from within Python. Random networks can also be generated
from the command line using the "pynetgen" shell script. For help, use:
$ pynetgen --help
"""

from ._version import __author__, __version__, _author_email, _copyright_year
from .pynetgen import *
