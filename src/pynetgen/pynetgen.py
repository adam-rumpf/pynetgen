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
from pynetgen.gen.grid import GridNetworkGenerator
from pynetgen.gen.netgen import NetgenNetworkGenerator

import argparse

# Define help strings
_desc = "Scripts for generating random flow networks in DIMACS format."
_vers = ("PyNETGEN v" + __version__ + "\nCopyright (c) " + _copyright_year
            + " " + __author__ + "\n" + _author_email)
_epil = """
This shell script generates random network flows problem instances exported in
DIMACS graph format <http://dimacs.rutgers.edu/archive/Challenges/>. The
"arg_list" argument specifies the network generation method and its options.
Choices for method include:
    netgen
    grid

For detailed instructions for these methods, use one of the following commands:
$ pynetgen netgen help
$ pynetgen grid help

The "netgen" option is a Python implementation of NETGEN, a random network
flows problem instance generator defined in Klingman, Napier, and Stutz 1974
(doi:10.1287/mnsc.20.5.814). The algorithm is based primarily on a C
implementation of NETGEN (copyright (c) 1989 Norbert Schlenker).

The "grid" option is a grid-based network generation method based on an
algorithm described in Sadeghi, Seifi, and Azizi 2017
(doi:10.1016/j.cie.2017.02.006).
"""
_netgen_instructions = """
usage: pynetgen.py [-q] [-f [FILE]] netgen [ARGS ...]

An implementation of the NETGEN network flows problem instance generator.

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

The -q tag silences the result message.

The -f argument specifies an output file path. Results are printed to the
screen if left blank.

NETGEN is a standard network flows problem instance generator defined in:

    D. Klingman, A. Napier, and J. Stutz. NETGEN: A Program for generating
    large scale capacitated assignment, transportation, and minimum cost flow
    network problems. Management Science, 20(5):814-821, 1974.
    doi:10.1287/mnsc.20.5.814.

With the exception of the final "rng" argument and the optional file tag, the
command line arguments of this script are identical to those of the original C
implementation. All network parameters are integer.

By default the resulting problem instance is a minimum-cost flow problem.
Transportation and maximum flow problems can also be generated, and are
implicitly chosen according to the network parameters.

The resulting problem instance is a transportation problem if the total number
of sources and sinks equals the total number of nodes, there are no
transshipment sources or sinks, and the total supply, sources, and sinks are
all equal. It is a maximum flow problem if it is not an assignment problem and
the min/max costs are both set to 1.

Skeleton arcs are part of NETGEN's process for generated minimum-cost flow
problems, and are included to ensure feasibility. They are a subset of arcs
that include paths from sources to sinks, and they are uncapacitated in order
to ensure that the network can carry sufficient flow, but a fraction of them
are chosen to receive the maximum possible cost in order to discourage
uninteresting solutions that use only the skeleton arcs.
"""
_grid_instructions = """
usage: pynetgen.py [-f [FILE]] grid [ARGS ...]

A grid-based network flows problem instance generator.

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

All network parameters are integer.

The -q tag silences the result message.

The -f argument specifies an output file path. Results are printed to the
screen if left blank.

This is a simple network flows problem instance generator that uses a
grid-based network. The network consists of a square grid of nodes, with a
master source on one side feeding into all rows, and a master sink on the other
side extracting from all rows.

By default the resulting problem instance is a minimum-cost flow problem. A
maximum flow problem is generated if the minimum and maximum arc costs are both
set equal to 1 and the number of sources does not equal the total supply.
Transshipment sources and sinks are not included. Transportation problems
cannot be generated.

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

In the output file, the different types of arcs in the arc list are divided
using comments. In order, they consist of: the master supply arcs, the master
sink arcs, the Eastern row arcs (with the first row constituting the skeleton
arcs), the Western row arcs (if present), the Southern column arcs, the
Northern column arcs, the Southeast diagonal arcs (if present), the Northeast
diagonal arcs (if present), the Northwest diagonal arcs (if present), and
finally the Southwest diagonal arcs (if present).
"""

#=============================================================================

def main():
    """The main driver for use when PyNETGEN is called from the console.
    
    This function is called when the main pynetgen.py file is executed as a
    script, or when it is called from the console using:
        $ pynetgen [args]
    
    This function attempts to parse any included command line arguments and
    then calls the main network generation function.
    """
    
    # Define argument parser
    parser = argparse.ArgumentParser(prog="pynetgen", description=_desc,
                         epilog=_epil,
                         formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-v", "--version", action="version", version=_vers)
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="silence result message")
    parser.add_argument("-f", "--file", nargs="?", dest="file",
                        help="output file path (prints to screen if blank)")
    parser.add_argument("arg_list", nargs="+",
                        help="select a method and its command line arguments")
    
    args = parser.parse_args()
    arg_list = args.arg_list
    
    # Display method-specific help messages if requested
    if len(arg_list) > 1:
        if arg_list[0] == "netgen" and arg_list[1] == "help":
            print(_netgen_instructions)
            return None
        if arg_list[0] == "grid" and arg_list[1] == "help":
            print(_grid_instructions)
            return None

    # If a method is selected, call its function with the other arguments
    if len(arg_list) > 0:
        if arg_list[0] == "netgen":
            # NETGEN requires 0-15 arguments
            if len(arg_list) > 15:
                raise TypeError("NETGEN requires 0-15 arguments")
            netgen_generate(*arg_list[1:], fname=args.file)
            if args.quiet == False and args.file != None:
                print("Network successfully written to " + args.file)
            return None
        if arg_list[0] == "grid":
            # The grid algorithm requires 0-14 argumets
            if len(arg_list) > 14:
                raise TypeError("grid algorithm requires 0-14 arguments")
            grid_generate(*arg_list[1:], fname=args.file)
            if args.quiet == False and args.file != None:
                print("Network successfully written to " + args.file)
            return None

#-----------------------------------------------------------------------------

def netgen_generate(seed=1, nodes=10, sources=3, sinks=3, density=30,
                    mincost=10, maxcost=99, supply=1000, tsources=0, tsinks=0,
                    hicost=0, capacitated=100, mincap=100, maxcap=1000,
                    rng=0, fname=None):
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
    fname -- path of output file (default None, which prints to screen)
    
    All keyword arguments besides the RNG selection and the file name are
    identical to those of the original C implementation of NETGEN.  All
    network parameters are integer.

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
    
    Returns 0 on successful exit.
    """
    
    # Initialize the network generation object
    Network = NetgenNetworkGenerator(seed=seed, nodes=nodes, sources=sources,
        sinks=sinks, density=density, mincost=mincost, maxcost=maxcost,
        supply=supply, tsources=tsources, tsinks=tsinks, hicost=hicost,
        capacitated=capacitated, mincap=mincap, maxcap=maxcap, rng=rng)

    # Print the network to the specified destination
    Network.write(fname=fname)
    
    del Network
    
    return 0

#-----------------------------------------------------------------------------

def grid_generate(seed=1, rows=3, columns=4, diagonal=1, reverse=1,
                 wrap=0, mincost=10, maxcost=99, supply=1000, hicost=0,
                 capacitated=100, mincap=100, maxcap=1000, rng=0, fname=None):
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
    fname -- path of output file (default None, which prints to screen)
    
    All network parameters are integer.
    
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
    
    Returns 0 on successful exit.
    """
    
    # Initialize network generation object
    Network = GridNetworkGenerator(seed=seed, rows=rows, columns=columns,
        diagonal=diagonal, reverse=reverse, wrap=wrap, mincost=mincost,
        maxcost=maxcost, supply=supply, hicost=hicost, capacitated=capacitated,
        mincap=mincap, maxcap=maxcap, rng=rng)
    
    # Print the network to the specified destination
    Network.write(fname=fname)
    
    del Network
    
    return 0

#-----------------------------------------------------------------------------

if __name__ == "__main__":
    # Run main script to parse command line arguments and generate a network
    main()
