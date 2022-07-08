"""Classes and methods for the NETGEN network generation algorithm."""

from pynetgen.util.ilist import IndexList
from pynetgen.util.randit import NetgenRandom
from pynetgen.util.randit import StandardRandom

#=============================================================================

class NetgenNetworkGenerator:
    """A class for implementing the NETGEN random network generator.
    
    This class is meant to act as a container for carrying out the NETGEN
    random network generation algorithm, with attributes for temporarily
    storing network parameters and methods for generating and exporting the
    resulting graph.
    """
    
    #-------------------------------------------------------------------------
    
    def __init__(self, seed=1, nodes=10, sources=3, sinks=3, density=30,
                    mincost=10, maxcost=99, supply=1000, tsources=0, tsinks=0,
                    hicost=0, capacitated=100, mincap=100, maxcap=1000,
                    rng=0):
        """NETGEN network object constructor.
        
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
        hicost -- percent of skeleton arcs (0-100) given maximum cost
            (default 0)
        capacitated -- percent of arcs (0-100) that are capacitated
            (default 100)
        mincap -- minimum arc capacity (default 100)
        maxcap -- maximum arc capacity (default 1000)
        rng -- index of random network generator to use (default 0),
            including:
            0: the original NETGEN pseudorandom number generator
            1: the Python standard library random number generator
        """
        
        # Validate inputs and convert to correct data types
        seed = int(seed)
        nodes = int(nodes)
        if nodes < 0:
            raise ValueError("node count must be nonnegative")
        sources = int(sources)
        if sources < 0:
            raise ValueError("source count must be nonnegative")
        sinks = int(sinks)
        if sinks < 0:
            raise ValueError("sink count must be nonnegative")
        if sources + sinks > nodes:
            raise ValueError("source/sink count cannot exceed node count")
        density = int(density)
        if density < 1:
            raise ValueError("arc count must be nonnegative")
        if nodes > density:
            raise ValueError("node count must exceed arc count")
        mincost = float(mincost)
        maxcost = float(maxcost)
        if mincost > maxcost:
            raise ValueError("min cost cannot exceed max cost")
        supply = float(supply)
        tsources = int(tsources)
        if tsources < 0:
            raise ValueError("transshipment source count must be nonnegative")
        if tsources > sources:
            raise ValueError("transshipment sources cannot exceed sources")
        tsinks = int(tsinks)
        if tsinks < 0:
            raise ValueError("transshipment sink count must be nonnegative")
        if tsinks > sinks:
            raise ValueError("transshipment sinks cannot exceed sinks")
        hicost = float(hicost)/100 # convert percent into fraction
        if hicost < 0 or hicost > 1:
            raise ValueError("high cost percentage must be in [0,100]")
        capacitated = float(capacitated)/100 # convert percent into fraction
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
        
        # Initialize attributes for temporary storage
        self._arc_count = 0 # number of arcs generated so far
        self._nodes_left = nodes - sinks + tsinks # nodes left to generate
        
        ###
        print([seed, nodes, sources, sinks, density,
                    mincost, maxcost, supply, tsources, tsinks,
                    hicost, capacitated, mincap, maxcap, rng])
        print(Rng.generate(0, 100))
