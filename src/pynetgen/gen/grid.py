"""Classes and methods for the grid-based network generation algorithm."""

from pynetgen.util.ilist import IndexList
from pynetgen.util.randit import NetgenRandom
from pynetgen.util.randit import StandardRandom
from pynetgen._version import __version__

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
                 capacitated=100, mincap=100, maxcap=1000, rng=0,
                 type=None):
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
        type -- problem type override (default None); setting to an integer
            attempts to generate the specified type of problem and ignores the
            default behavior explained below:
            0: minimum-cost flow
            1: maximum flow
        
        All network parameters are integer.
        
        The problem type is implicitly chosen based on the network attributes
        (unless the "type" attribute is set). By default the problem is
        minimum-cost flow. It is a maximum flow problem if the total supply
        does not equal the number of sources, and if the minimum and maximum
        arc costs are both exactly 1.
        """
        
        # Validate inputs and convert to correct data types
        self.seed = int(seed)
        self.rows = int(rows)
        if self.rows < 1:
            raise ValueError("grid must have at least 1 row")
        self.columns = int(columns)
        if self.columns < 1:
            raise ValueError("grid must have at least 1 column")
        self.diagonal = bool(int(diagonal))
        self.reverse = bool(int(reverse))
        self.wrap = bool(int(wrap))
        self.mincost = int(mincost)
        self.maxcost = int(maxcost)
        if self.mincost > maxcost:
            raise ValueError("min cost cannot exceed max cost")
        self.supply = int(supply)
        self.hicost = int(hicost)
        if self.hicost < 0 or self.hicost > 100:
            raise ValueError("high cost percentage must be in [0,100]")
        self.capacitated = int(capacitated)
        if self.capacitated < 0 or self.capacitated > 100:
            raise ValueError("capacitated percentage must be in [0,100]")
        self.mincap = int(mincap)
        self.maxcap = int(maxcap)
        if self.mincap > self.maxcap:
            raise ValueError("min capacity cannot exceed max capacity")
        rng = int(rng)
        if type is not None:
            type = int(type)
            if type < 0 or type > 1:
                raise ValueError("problem type index must be 0, 1, or None")
        
        # Initialize random number generation object
        if rng == 0:
            Rng = NetgenRandom(seed)
        elif rng == 1:
            Rng = StandardRandom(seed)
        else:
            raise ValueError("RNG index must be 0 or 1")
        
        # Initialize random number generation object
        if rng == 0:
            self.Rng = NetgenRandom(seed)
        elif rng == 1:
            self.Rng = StandardRandom(seed)
        else:
            raise ValueError("RNG index must be 0 or 1")
        self.seed = self.Rng.seed # copy RNG's seed in case of -1
        
        # Initialize attributes for temporary storage
        self._type = 0 # problem type (0: mincost, 1: maxflow)
        self._arc_count = 0 # number of arcs generated
        self._node_count = rows*columns + 2 # number of nodes generated
        
        # Determine which type of problem to generate
        if type is not None:
            if (self.sources != self.supply and self.mincost == 1 and
                self.maxcost == 1):
                self._type = 1
            else:
                self._type = 0
        
        # Call the problem generation method
        self._create_problem()
    
    #-------------------------------------------------------------------------
    
    def _create_problem(self):
        """Generates a min-cost flow or max-flow problem."""
        
        ###
        pass
    
    #-------------------------------------------------------------------------
    
    def write(self, fname=None):
        """Writes the completed network to a file (or prints to screen).
        
        Keyword arguments:
        fname -- output file path (default None, which prints to screen)
        """
        
        # Begin to write output string
        out = (f"c PyNETGEN v{__version__}\n" +
        "c $ pip install pynetgen\nc\n" +
        "c  Grid-based flow network generation algorithm\n" +
        "c  Problem input parameters\n" +
        "c  " + "-"*37 + "\n" +
        f"c   Random seed:          {self.seed}\n" +
        f"c   Number of rows:       {self.rows}\n" +
        f"c   Number of columns:    {self.columns}\n" +
        f"c   Diagonal arcs (bool): {int(self.diagonal)}\n" +
        f"c   Backward arcs (bool): {int(self.reverse)}\n" +
        f"c   Wraparound (bool):    {int(self.wrap)}\n" +
        f"c   Minimum arc cost:     {self.mincost}\n" +
        f"c   Maximum arc cost:     {self.maxcost}\n" +
        f"c   Total supply:         {self.supply}\n" +
        "c   Skeleton arcs -\n" +
        f"c     With max cost:      {self.hicost}\n" +
        f"c     Capacitated:        {self.capacitated}\n" +
        f"c   Minimum arc capacity: {self.mincap}\n" +
        f"c   Maximum arc capacity: {self.maxcap}\n")
        
        # Handle max flow problem
        if self._type == 1:
            out += "c\nc  *** Maximum flow ***\nc\n"
            out += f"p max {self._node_count} {self._arc_count}\n"
            ###
        
        # Handle min-cost flow problem
        else:
            out += "c\nc  *** Minimum cost flow ***\nc\n"
            out += f"p min {self._node_count} {self._arc_count}\n"
            ###
        
        # Write or print string
        if fname is None:
            print(out)
        else:
            with open(fname, 'w') as f:
                print(out[:-1], file=f)
        
        return 0
