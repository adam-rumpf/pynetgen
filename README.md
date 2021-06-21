# PyNETGEN

<a href="https://github.com/adam-rumpf/netgen-python/search?l=python"><img src="https://img.shields.io/badge/language-python-blue?logo=python&logoColor=white"/></a> <a href="https://github.com/adam-rumpf/netgen-python/releases"><img src="https://img.shields.io/github/v/release/adam-rumpf/netgen-python"/></a> <a href="https://github.com/adam-rumpf/netgen-python/blob/main/LICENSE"><img src="https://img.shields.io/github/license/adam-rumpf/netgen-python"/></a> <a href="https://github.com/adam-rumpf/netgen-python/commits/main"><img src="https://img.shields.io/maintenance/yes/2021"/></a>

A Python implementation of NETGEN (Klingman et al. 1974) for generating random network flows problem instances.

## Introduction

PyNETGEN is a Python implementation of NETGEN, a random network flows problem instance generator defined in:

> D. Klingman, A. Napier, and J. Stutz. NETGEN: A Program for generating large scale capacitated assignment, transportation, and minimum cost flow network problems. _Management Science_, 20(5):814-821, 1974. [doi:10.1287/mnsc.20.5.814](https://doi.org/10.1287/mnsc.20.5.814).

This package is based on a [C implementation](https://lemon.cs.elte.hu/trac/lemon/browser/lemon-benchmark/generators/netgen) of NETGEN by Norbert Schlenker (1989). The original implementation was used to generate random minimum-cost flow, maximum flow, and assignment problems, exported in a standardized text file format.

## Usage

PyNETGEN can be used in two ways:

1. The main script, `netgen.py`, can be called from the command line to produce a random problem instance text file. This is equivalent to the behavior of the original C implementation (and PyNETGEN even includes the same custom random number generator as the C implementation, so that both produce identical networks given the same seed).

2. PyNETGEN can be imported like any other Python package using `import pynetgen`, making a variety of network storage and generation tools available. This allows flow networks to be generated, imported, exported, and edited while being maintained in memory through use of some simple network classes.
