"""The main PyNETGEN module.

This file contains the main driver functions for the PyNETGEN procedures,
which are handled using the classes defined in the submodules.
"""

def main():
    """The main driver for use when PyNETGEN is called from the console.
    
    This function is called when the main pynetgen.py file is executed as a
    script, or when it is called from the console using:
        $ pynetgen [args]
    
    This function attempts to parse any included command line arguments and
    then calls the main network generation function.
    """
    
    ###
    pass

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

    ### add support to choose an output file (default cwd)
    pass

if __name__ == "__main__":
    # Run main script to parse command line arguments and generate a network
    main()
    
    ### Temporary demo code
    import util.random
    rando = util.random.RandomIterator(1, True)
    for i in range(10):
        print(rando.generate(1, 100))
    print('-'*20)
    randy = util.random.RandomIterator(1, False)
    for i in range(10):
        print(randy.generate(1, 100))
    print('-'*20)
    import util.ilist
    mylist = util.ilist.IndexList(1, 8)
    print(mylist)
    print(len(mylist))
    print(mylist.pseudo_size)
    temp = mylist.choose_index(2)
    print(temp)
    print(mylist)
    print(mylist.pseudo_size)
    for i in range(20):
        mylist.pop()
    print(mylist.pseudo_size)
