"""The main PyNETGEN module.

This file contains the main driver functions for the PyNETGEN procedures,
which are handled using the classes defined in the submodules.

Importing the pynetgen module allows the netgen_generate and grid_generate
methods to be called from within Python. Random networks can also be generated
from the command line using the "pynetgen" shell script. For help, use:

    $ pynetgen --help
"""

###
if __name__ == "__main__":
    from _version import __author__, __version__, _author_email, _copyright_year
else:
    from ._version import __author__, __version__, _author_email, _copyright_year

import argparse

# Define help strings
desc = "Scripts for generating random flow networks in DIMACS format."
vers = ("PyNETGEN v" + __version__ + "\nCopyright (c) " + _copyright_year
            + " " + __author__ + "\n" + _author_email)
epil = """
PyNETGEN is a Python implementation of NETGEN, a random network flows problem
instance generator defined in Klingman, Napier, and Stutz 1974
(doi:10.1287/mnsc.20.5.814). The original NETGEN script, along with its
pseudorandom number generator, is included along with some other types of
random network scripts. PyNETGEN is based primarily on a C implementation of
NETGEN (copyright (c) 1989 Norbert Schlenker).

This shell script generates random network flows problem instances, exported in
DIMACS graph format <http://dimacs.rutgers.edu/archive/Challenges/>.

The "method" argument specifies the network generation method. Choices include:
    netgen (run '$ pynetgen netgen help' for details)
    grid (run '$ pynetgen grid help' for details)
"""
netgen_instructions = """
usage: pynetgen.py [-f [FILE]] netgen [ARGS ...]

NETGEN is a standard network flows problem instance generator defined in:

    D. Klingman, A. Napier, and J. Stutz. NETGEN: A Program for generating
    large scale capacitated assignment, transportation, and minimum cost flow
    network problems. Management Science, 20(5):814-821, 1974.
    doi:10.1287/mnsc.20.5.814.

By default the resulting problem instance is a minimum-cost flow problem.
Transportation and maximum flow problems can also be generated, and are
implicitly chosen according to the network parameters.

The resulting problem instance is a transportation problem if the total number
of sources and sinks equals the total number of nodes, and if there are no
transshipment sources or sinks. It is a maximum flow problem if it is not an
assignment problem and the min/max costs are both set to 1.

The command line arguments for the NETGEN script are as follows (in order):
    seed -- random number generator seed (default 1; -1 for random)
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

With the exception of the final "rng" argument, these are identical to the
original C implementation's command line arguments.

Skeleton arcs are part of NETGEN's process for generated minimum-cost flow
problems, and are included to ensure feasibility. They are a subset of arcs
that include paths from sources to sinks, and they are uncapacitated in order
to ensure that the network can carry sufficient flow, but a fraction of them
are chosen to receive the maximum possible cost in order to discourage
uninteresting solutions that use only the skeleton arcs.
"""
grid_instructions = """
usage: pynetgen.py [-f [FILE]] grid [args]

This is a simple network flows problem instance generator that uses a
grid-based network. The network consists of a square grid of nodes, with a
master source on one side feeding into all rows, and a master sink on the other
side extracting from all rows.

By default the resulting problem instance is a minimum-cost flow problem. A
maximum flow problem is generated if the minimum and maximum arc costs are both
set equal to 1. Transshipment sources and sinks are not included, and
transportation problems cannot be generated.

The command line arguments for the grid-based method are as follows (in order):
    seed -- random number generator seed (default 1; -1 for random)
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

The master source is located on the West side while the master sink is located
on the East side. All transshipment arcs feed into their immediate neighbors to
the North, East, and South (within the boundaries of the grid). If the
"diagonal" argument is True then they also feed into their neighbors to the
Northeast and Southeast. If the "reverse" argument is True then they also feed
into the Western directions. If the "wrap" argument is True then the first row
is considered to be adjacent to the last row.

Skeleton arcs are included in minimum-cost flow problems in order to ensure
feasibility. All arcs in the first row are treated as skeleton arcs, which are
uncapacitated to ensure that the network can carry enough flow, but a fraction
of them are chosen to receive the maximum possible cost in order to discourage
uninteresting solutions that use only the skeleton arcs.
"""

def main():
    """The main driver for use when PyNETGEN is called from the console.
    
    This function is called when the main pynetgen.py file is executed as a
    script, or when it is called from the console using:
        $ pynetgen [args]
    
    This function attempts to parse any included command line arguments and
    then calls the main network generation function.
    """
    
    # Define argument parser
    parser = argparse.ArgumentParser(description=desc, epilog=epil,
                         formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-v", "--version", action="version", version=vers)
    parser.add_argument("-f", "--file", nargs="?", dest="file",
                        help="output file path (prints to screen if blank)")
    parser.add_argument("arg_list", nargs="+",
                        help="select a method and its command line arguments")
    
    args = parser.parse_args()
    arg_list = args.arg_list

    # Display method-specific help messages if requested
    if len(arg_list) > 1:
        if arg_list[0] == "netgen" and arg_list[1] == "help":
            print(netgen_instructions)
            return None
        if arg_list[0] == "grid" and arg_list[1] == "help":
            print(grid_instructions)
            return None

    ###

def netgen_generate(seed=1, nodes=10, sources=3, sinks=3, density=30,
                    mincost=10, maxcost=99, supply=1000, tsources=0, tsinks=0,
                    hicost=0, capacitated=100, mincap=100, maxcap=1000, rng=0):
    """The main NETGEN random network generation function.

    Keyword arguments:
    seed -- random number generator seed (default 1; -1 for random)
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

    The problem type is implicitly determined according to the network's
    attributes. By default NETGEN generates a minimum-cost network flows
    problem, in which case skeleton arcs are generated to ensure that the
    network can carry all necessary flow from the sources to the sinks.
    Skeleton arcs are uncapacitated but always have the maximum possible cost.

    A transportation problem instance is generated if the total number of
    sources and sinks equals the total number of nodes, and if no transshipment
    sources or sinks are specified.

    A maximum flow problem instance is generated if the problem is not a
    transportation problem and if the maximum and minimum arc costs are both
    set equal to 1.

    Arc costs and capacities are drawn uniformly at random from the specified
    ranges.
    """

    pass

def grid_generate(seed=1, rows=3, columns=4, diagonal=1, reverse=1, wrap=0,
                  mincost=10, maxcost=99, supply=1000, hicost=0,
                  capacitated=100, mincap=100, maxcap=1000, rng=0):
    """A grid-based random network generation function.
    
    Keyword arguments:
    seed -- random number generator seed (default 1; -1 for random)
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

    By default this method generates a minimum-cost flow problem. Skeleton arcs
    are generated by default in order to ensure that the network can carry the
    required amount of flow from the master source to the master sink. To
    generate skeleton arcs, all arcs in the first row are uncapacitated, and a
    fraction of them specified by "hicost" are set to the maximum allowed cost.

    Setting "mincost" and "maxcost" both equal to 1 instead results in a
    maximum flow problem, in which case skeleton arcs are not generated.

    Unlike NETGEN, transportation problems are not supported.

    Arc costs and capacities are drawn uniformly at random from the specified
    ranges.
    """
    
    pass

if __name__ == "__main__":
    # Run main script to parse command line arguments and generate a network
    main()
