"""The main PyNETGEN module.

This file contains the main driver functions for the PyNETGEN procedures,
which are handled using the classes defined in the submodules.
"""

from ._version import __author__, __version__, _author_email, _copyright_year

import argparse

def main():
    """The main driver for use when PyNETGEN is called from the console.
    
    This function is called when the main pynetgen.py file is executed as a
    script, or when it is called from the console using:
        $ pynetgen [args]
    
    This function attempts to parse any included command line arguments and
    then calls the main network generation function.
    """
    
    # Define documentation strings
    desc = "A script for generating random flow networks in DIMACS format."
    vers = ("PyNETGEN v" + __version__ + "\nCopyright (c) " + _copyright_year
            + " " + __author__ + "\n" + _author_email)
    epil = """
    PyNETGEN is a Python implementation of NETGEN, a random network flows
    problem instance generator defined in Klingman, Napier, and Stutz 1974
    (doi:10.1287/mnsc.20.5.814). The original NETGEN script, along with its
    pseudorandom number generator, are included along with some other types
    of random network scripts. PyNETGEN is based primarily on a 1989
    implementation of NETGEN by Norbert Schlenker in C.
    
    NETGEN is a script for generating random flow networks for use as test
    instances, exported in DIMACS graph format
    <http://dimacs.rutgers.edu/archive/Challenges/>.
    """
    
    # Define argument parser
    parser = argparse.ArgumentParser(description=desc, epilog=epil,
                         formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-v", "--version", action="version", version=vers)
    parser.add_argument("-f", "--file", nargs="?", dest="file",
                        help="output file path (prints to screen if blank)")
    
    ###
    args = parser.parse_args()
    ###

def netgen_generate(seed=1, problem=0, nodes=10, sources=3, sinks=3,
                    density=30, mincost=10, maxcost=99, supply=1000,
                    tsources=0, tsinks=0, hicost=0, capacitated=100,
                    mincap=100, maxcap=1000, rng=0):
    """The main NETGEN random network generation function.

    Keyword arguments:
    seed -- random number generator seed (default 1)
    problem -- problem type index (default 0), including:
        0: minimum-cost flow
        1: maximum flow
        2: assignment
    nodes -- number of nodes (default 10)
    sources -- number of source nodes (default 3)
    sinks -- number of sink nodes (default 3)
    density -- number of arcs (default 30)
    mincost -- minimum arc cost (default 10)
    maxcost -- maximum arc cost (default 99)
    supply -- total supply (default 1000)
    tsources -- number of transshipment sources (default 0)
    tsinks -- number of transshipment sinks (default 0)
    hicost -- percent of skeleton arcs (0-100) given maximum cost (default 0)
    capacitated -- percent of arcs (0-100) that are capacitated (default 100)
    mincap -- minimum arc capacity (default 100)
    maxcap -- maximum arc capacity (default 1000)
    rng -- index of random network generator to use (default 0), including:
        0: the original NETGEN pseudorandom number generator
        1: the Python standard library random number generator
    
    All keyword arguments besides the RNG selection are identical to those of
    the original C implementation of NETGEN.
    """

    pass

def grid_generate(seed=1, problem=0, rows=3, columns=4, diagonal=1,
                  reverse=1, wrap=0, mincost=10, maxcost=99, supply=1000,
                  hicost=0, capacitated=100, mincap=100, maxcap=1000, rng=0):
    """A grid-based random network generation function.
    
    Keyword arguments:
    seed -- random number generator seed (default 1)
    problem -- problem type index (default 0), including:
        0: minimum-cost flow
        1: maximum flow
        2: assignment
    nodes -- number of nodes (default 10)
    rows -- number of grid rows (default 3)
    columns -- number of grid columns (default 4)
    diagonal -- whether to include diagonal arcs (default 1)
    reverse -- whether to include arcs in the reverse direction (default 1)
    wrap -- whether to wrap the row adjacencies like a cylinder (default 0)
    mincost -- minimum arc cost (default 10)
    maxcost -- maximum arc cost (default 99)
    supply -- total supply at the master supply node (default 1000)
    hicost -- percent of skeleton arcs (0-100) given maximum cost (default 0)
    capacitated -- percent of arcs (0-100) that are capacitated (default 100)
    mincap -- minimum arc capacity (default 100)
    maxcap -- maximum arc capacity (default 1000)
    rng -- index of random network generator to use (default 0), including:
        0: the original NETGEN pseudorandom number generator
        1: the Python standard library random number generator
    
    The grid-based network consists of an m-by-n array of transshipment nodes
    with one master source that acts as a predecessor to every node in the
    first column and one master sink that acts as a successor to every node in
    the last column.
    
    In all cases an arc is generated from each transshipment node to the nodes
    North, East, and South of it (within the boundaries of the grid. If the
    "diagonal" argument is True then arcs are also generated to the Northeast
    and Southeast. If the "reverse" argument is True then arcs are also
    generated in the Western directions. If the "wrap" argument is True then
    the first row is considered to be adjacent to the last row.
    
    The "skeleton arcs" in the grid-based network are simply the arcs in the
    first row. They are always uncapacitated to ensure that the network can
    carry all necessary flow.
    """
    
    pass

if __name__ == "__main__":
    # Run main script to parse command line arguments and generate a network
    main()
