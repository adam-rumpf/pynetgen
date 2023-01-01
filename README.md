# PyNETGEN

<a href="https://pypi.org/project/pynetgen"><img src="https://img.shields.io/pypi/v/pynetgen?logo=pypi&logoColor=white"/></a> <a href="https://github.com/adam-rumpf/pynetgen"><img src="https://img.shields.io/github/v/tag/adam-rumpf/pynetgen?logo=github"></a> <a href="https://pypi.org/project/pynetgen/#history"><img src="https://img.shields.io/pypi/status/pynetgen"/></a> <a href="https://www.python.org/"><img src="https://img.shields.io/pypi/pyversions/pynetgen?logo=python&logoColor=white"></a> <a href="https://github.com/adam-rumpf/pynetgen/blob/main/LICENSE"><img src="https://img.shields.io/github/license/adam-rumpf/pynetgen"/></a> <a href="https://github.com/adam-rumpf/pynetgen/commits/main"><img src="https://img.shields.io/maintenance/yes/2023"/></a>

A Python module for generating random network flows problem instances in [DIMACS graph format](#dimacs-file-format), including an implementation of the NETGEN algorithm ([Klingman et al. 1974](https://doi.org/10.1287/mnsc.20.5.814)).

## Introduction

This package defines a variety of scripts for generating random instances of network flows problems subject to tuneable parameters. This can be accomplished within Python by importing `pynetgen` as a [module](#module-usage), or from the command line by calling `pynetgen` as a [shell script](#command-line-usage).

PyNETGEN began as a Python implementation of NETGEN, a random network flows problem instance generator defined in:

> D. Klingman, A. Napier, and J. Stutz. NETGEN: A Program for generating large scale capacitated assignment, transportation, and minimum cost flow network problems. _Management Science_, 20(5):814-821, 1974. [doi:10.1287/mnsc.20.5.814](https://doi.org/10.1287/mnsc.20.5.814).

This package's implementation of NETGEN is based on a [C implementation](https://lemon.cs.elte.hu/trac/lemon/browser/lemon-benchmark/generators/netgen) of NETGEN by Norbert Schlenker (1989). The original implementation was used to generate random minimum-cost flow, maximum flow, and assignment problems, exported in DIMACS graph format.

An alternate network generation algorithm is also included for generating grid-based graphs similar to those described for the test problems of:

> S. Sadeghi, A. Seifi, and E. Azizi. Trilevel shortest path network interdiction with partial fortification. _Computers & Industrial Engineering_, 106:400-411, 2017. [doi:10.1016/j.cie.2017.02.006](https://doi.org/10.1016/j.cie.2017.02.006).

## Network Generation Algorithms

Two different random network generation algorithms are defined. Both are capable of generating minimum-cost network flows problems according to a set of tuneable parameters that control things like the size of the network and the acceptable ranges of arc costs and capacities. Both also have measures in place to guarantee that the resulting problem is feasible. To briefly describe each algorithm:

* The NETGEN algorithm (`netgen_generate`) begins by defining source and sink nodes and randomly distributing supply among them. It then generates a set of "skeleton arcs" to create paths from the sources to the sinks. Skeleton arcs are guaranteed to have enough capacity to carry all required flow, ensuring that the problem instance is feasible, but they can also be specified to have maximum cost in order to discourage uninteresting solutions that utilize only skeleton arcs. After the skeleton is defined, arcs are randomly generated between pairs of randomly-selected nodes until the desired density is reached.
* The grid-based algorithm (`grid_generate`) defines a rectangular array of nodes with a specified number of columns and rows. A single master source is placed on one side, and a master sink is placed on the other. Arcs are generated in a square (or square with diagonal) grid pattern, and can be specified to be directed either strictly from the source side to the sink side or in both directions. The "skeleton arcs" consist of paths that move along the rows of the network.

By default both algorithms produce a minimum-cost flow problem instance. If the minimum and maximum arc costs are both set to exactly 1, and if the number of sources does not equal the total supply (easily achieved by setting the supply to 0), then a maximum flow problem is generated instead.

## Usage

PyNETGEN can be installed from [PyPI](https://pypi.org/project/pynetgen) via the console command
```
$ pip install pynetgen
```

After installation, PyNETGEN can be used either by importing it as a module or through its shell script.

### Module Usage

PyNETGEN can be imported from within Python using
```python
import pynetgen
```
which grants access to the two main public functions `netgen_generate()` and `grid_generate()`. For detailed descriptions of the algorithms see their docstrings via `help(netgen_generate)` and `help(grid_generate)`. This includes brief descriptions of the network structures and a detailed lists of network parameters.

### Command Line Usage

PyNETGEN can be run through the command line using the `pynetgen` shell script
```
$ pynetgen [-h] [-v] [-q] [-f [FILE]] arg_list [arg_list ...]
```
For basic usage instructions, access the documentation via
```
$ pynetgen --help
```
For detailed instructions for the NETGEN and grid-based algorithms, including a brief description of the network's structure and a detailed list of network parameters, use
```
$ pynetgen netgen help
```
or
```
$ pynetgen grid help
```

## DIMACS File Format

The resulting network is output as a file in [DIMACS graph format](http://dimacs.rutgers.edu/archive/Challenges/) (or printed to the screen, in case no file path is given). To give a brief description of the format, a DIMACS graph file is a pure text file in which every line begins with either the letter `c`, `p`, `n`, or `a` to specify what type of information it defines.

In the case of a minimum-cost flows problem, the lines are formatted as follows:

* `c` indicates a comment line. The output file begins with a header made up of comment lines describing the parameters used to generate the problem.
* `p` indicates the problem definition. This follows the header and has the format `p min NODES DENSITY`, where:
  * `NODES` is the total number of nodes.
  * `DENSITY` is the total number of arcs.
* `n` indicates a node definition. The node definitions follow the problem definition, and have the format `n ID SUPPLY`, where:
  * `ID` is a unique numerical index given to all nodes (starting at 1).
  * `SUPPLY` is the supply value of the node (positive for sources, negative for sinks). In order to save space, only nodes with nonzero supply values are included.
* `a` indicates an arc definition. The arc definitions follow the node definitions, and have the format `a FROM TO MINCAP MAXCAP COST`, where:
  * `FROM` and `TO` are the node indices of the arc's origin and destination, respectively.
  * `MINCAP` and `MAXCAP` are the arc's lower and upper capacity bounds, respectively.
  * `COST` is the arc's unit flow cost.

The output file for a maximum-flow problem follows the same format with the following exceptions:

* The objective is `max` instead of `min`.
* Source and sink nodes are given a `SUPPLY` value of `s` or `t`, respectively, rather than a specific number.
* Arc definitions omit the cost and lower capacity bound, now having the format `a FROM TO MAXCAP`.
