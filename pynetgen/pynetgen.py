"""Main PyNETGEN module.

This file contains the main driver functions for the PyNETGEN procedures,
which are handled using the classes defined in the submodules.
"""

def generate(seed=1, problem=0, nodes=10, sources=3, sinks=3, density=30,
             mincost=10, maxcost=99, supply=1000, tsources=0, tsinks=0,
             hicost=0, capacitated=100, mincap=100, maxcap=1000):
    """The main NETGEN random network generation function.

    Keyword arguments:
    seed -- random number generator seed (default 1)
    problem -- problem type index (default 0)
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
    """

    pass

if __name__ == "__main__":
    ### Temporary demo code
    import util.random
    rando = util.random.RandomIterator(1, True)
    for i in range(10):
        print(rando.generate(1, 100))
    print('-'*20)
    randy = util.random.RandomIterator(1, False)
    for i in range(10):
        print(randy.generate(1, 100))
