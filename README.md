# PyNETGEN

<a href="https://pypi.org/project/pynetgen"><img src="https://img.shields.io/pypi/v/pynetgen?logo=pypi&logoColor=white"/></a> <a href="https://github.com/adam-rumpf/pynetgen"><img src="https://img.shields.io/github/v/tag/adam-rumpf/pynetgen?logo=github"></a> <a href="https://pypi.org/project/pynetgen/#history"><img src="https://img.shields.io/pypi/status/pynetgen"/></a> <a href="https://www.python.org/"><img src="https://img.shields.io/pypi/pyversions/pynetgen?logo=python&logoColor=white"></a> <a href="https://github.com/adam-rumpf/pynetgen/blob/main/LICENSE"><img src="https://img.shields.io/github/license/adam-rumpf/pynetgen"/></a> <a href="https://github.com/adam-rumpf/pynetgen/commits/main"><img src="https://img.shields.io/maintenance/yes/2022"/></a>

A Python module for generating random network flows problem instances in [DIMACS graph format](http://dimacs.rutgers.edu/archive/Challenges/), including an implementation of the NETGEN algorithm ([Klingman et al. 1974](https://doi.org/10.1287/mnsc.20.5.814)).

## Introduction

This package defines a variety of scripts for generating random instances of network flows problems subject to tuneable parameters. This can be accomplished within Python by importing `pynetgen` as a module, or from the command line by calling `pynetgen` as a shell script.

PyNETGEN began as a Python implementation of NETGEN, a random network flows problem instance generator defined in:

> D. Klingman, A. Napier, and J. Stutz. NETGEN: A Program for generating large scale capacitated assignment, transportation, and minimum cost flow network problems. _Management Science_, 20(5):814-821, 1974. [doi:10.1287/mnsc.20.5.814](https://doi.org/10.1287/mnsc.20.5.814).

This package's implementation of NETGEN is based on a [C implementation](https://lemon.cs.elte.hu/trac/lemon/browser/lemon-benchmark/generators/netgen) of NETGEN by Norbert Schlenker (1989). The original implementation was used to generate random minimum-cost flow, maximum flow, and assignment problems, exported in DIMACS graph format.

An alternate network generation algorithm is also included for generating grid-based graphs similar to those described for the test problems of:

> S. Sadeghi, A. Seifi, and E. Azizi. Trilevel shortest path network interdiction with partial fortification. _Computers & Industrial Engineering_, 106:400-411, 2017. [doi:10.1016/j.cie.2017.02.006](https://doi.org/10.1016/j.cie.2017.02.006).

## Project Status

This is a work in progress. It currently includes only a few necessary submodules and some of the overall framework, and it is not yet release-ready.
