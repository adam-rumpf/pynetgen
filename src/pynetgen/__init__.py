"""A Python module for generating random network flows problem instances.

Importing the pynetgen module grants access to the two main public methods:
    netgen_generate()
    grid_generate()
for generating random networks using the NETGEN algorithm or a grid-based
network generation algorithm. Access their docstrings via help() for
detailed usage instructions.

PyNETGEN can also be accessed via the command line using the pynetgen shell
script. Access its documentation via
$ pynetgen --help
for detailed usage instructions.
"""

from ._version import __author__, __version__, _author_email, _copyright_year
from .pynetgen import *
