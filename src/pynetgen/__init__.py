"""A Python implementation of the NETGEN network flows problem generator.

The pynetgen package is a Python implementation of NETGEN, a random network
flows problem instance generator defined in:

    D. Klingman, A. Napier, and J. Stutz. NETGEN: A Program for generating
    large scale capacitated assignment, transportation, and minimum cost flow
    network problems. Management Science, 20(5):814-821, 1974.
    doi:10.1287/mnsc.20.5.814.

This package is based on a C implementation of NETGEN by Norbert Schlenker
(1989). The original implementation was used to generate random minimum-cost
flow, maximum flow, and assignment problems, exported in a DIMACS graph
format.
"""

from ._version import __author__, __version__
from . import pynetgen
