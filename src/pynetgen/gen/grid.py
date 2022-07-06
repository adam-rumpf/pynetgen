"""Classes and methods for the grid-based network generation algorithm."""

from pynetgen.util.ilist import IndexList
from pynetgen.util.randit import NetgenRandom
from pynetgen.util.randit import StandardRandom

#=============================================================================

class GridNetworkGenerator:
    """A class for generating a grid-based graph.
    
    This class is meant to act as a container for carrying out the grid-based
    random network generation algorithm, with attributes for temporarily
    storing network parameters and methods for generating and exporting the
    resulting graph.
    """
    
    #-------------------------------------------------------------------------
    
    def __init__(self, seed=1, rows=3, columns=4, diagonal=1, reverse=1,
                 wrap=0, mincost=10, maxcost=99, supply=1000, hicost=0,
                 capacitated=100, mincap=100, maxcap=1000, rng=0):
        """Grid-based network object constructor.
        
        Keyword arguments:
        seed -- random number generator seed (default 1; -1 for random)
        nodes -- number of nodes (default 10)
        rows -- number of grid rows (default 3)
        columns -- number of grid columns (default 4)
        diagonal -- whether to include diagonal arcs (default 1)
        reverse -- whether to include arcs in the reverse direction
            (default 1)
        wrap -- whether to wrap the row adjacencies like a cylinder
            (default 0)
        mincost -- minimum arc cost (default 10)
        maxcost -- maximum arc cost (default 99)
        supply -- total supply at the master supply node (default 1000)
        hicost -- percent of skeleton arcs (0-100) given maximum cost
            (default 0)
        capacitated -- percent of arcs (0-100) that are capacitated
            (default 100)
        mincap -- minimum arc capacity (default 100)
        maxcap -- maximum arc capacity (default 1000)
        rng -- index of random network generator to use (default 0), including:
            0: the original NETGEN pseudorandom number generator
            1: the Python standard library random number generator
        """
        
        # Validate inputs and convert to correct data types
        seed = int(seed)
        rows = int(rows)
        if rows < 1:
            raise ValueError("grid must have at least 1 row")
        columns = int(columns)
        if columns < 1:
            raise ValueError("grid must have at least 1 column")
        diagonal = bool(int(diagonal))
        reverse = bool(int(reverse))
        wrap = bool(int(wrap))
        mincost = float(mincost)
        maxcost = float(maxcost)
        if mincost > maxcost:
            raise ValueError("min cost cannot exceed max cost")
        supply = float(supply)
        hicost = float(hicost)/100
        if hicost < 0 or hicost > 1:
            raise ValueError("high cost percentage must be in [0,100]")
        capacitated = float(capacitated)/100
        if capacitated < 0 or capacitated > 1:
            raise ValueError("capacitated percentage must be in [0,100]")
        mincap = float(mincap)
        maxcap = float(maxcap)
        if mincap > maxcap:
            raise ValueError("min capacity cannot exceed max capacity")
        rng = int(rng)
        
        # Initialize random number generation object
        if rng == 0:
            Rng = NetgenRandom(seed)
        elif rng == 1:
            Rng = StandardRandom(seed)
        else:
            raise ValueError("RNG index must be 0 or 1")
        
        ###
        print([seed, rows, columns, diagonal, reverse, wrap, mincost, maxcost,
               supply, hicost, capacitated, mincap, maxcap, rng])
        print(Rng.generate(0, 100))
