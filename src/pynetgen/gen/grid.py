"""Classes and methods for the grid-based network generation algorithm."""

from pynetgen.util.ilist import IndexList
from pynetgen.util.randit import NetgenRandom
from pynetgen.util.randit import StandardRandom
from pynetgen._version import __version__

import collections
import math

#=============================================================================

class GridNetworkGenerator:
    """A class for generating a grid-based graph.
    
    This class is meant to act as a container for carrying out the grid-based
    random network generation algorithm, with attributes for temporarily
    storing network parameters and methods for generating and exporting the
    resulting graph.
    """
    
    #-------------------------------------------------------------------------
    
    def __init__(self, seed=1, rows=3, columns=4, skeleton=1, diagonal=1,
                 reverse=0, wrap=0, mincost=10, maxcost=99, supply=1000,
                 hicost=0, capacitated=100, mincap=100, maxcap=1000, rng=0,
                 type=None):
        """Grid-based network object constructor.
        
        Keyword arguments:
        seed -- random number generator seed (default 1; -1 for random)
        nodes -- number of nodes (default 10)
        rows -- number of grid rows (default 3)
        columns -- number of grid columns (default 4)
        skeleton -- number of skeleton rows (default 1)
        diagonal -- whether to include diagonal arcs (bool; default 1)
        reverse -- whether to include arcs in the reverse direction
            (bool; default 0)
        wrap -- whether to wrap the row adjacencies like a cylinder
            (bool; efault 0)
        mincost -- minimum arc cost (default 10)
        maxcost -- maximum arc cost (default 99)
        supply -- total supply at the master supply node (default 1000)
        hicost -- percent of skeleton arcs (0-100) given maximum cost
            (default 0)
        capacitated -- percent of skeleton arcs (0-100) that are capacitated
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
        self.skeleton = int(skeleton)
        if self.skeleton < 0 or self.skeleton > self.rows:
            raise ValueError("skeleton rows must be between 0 and rows")
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
        
        # Arcs are stored in a queue of (tail, head, cost, capacity) tuples
        self._arcs = collections.deque()
        
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
        
        # Determine minimum capacities of skeleton rows
        skeleton_cap = self.supply
        if self.skeleton > 1:
            skeleton_cap = math.ceil(self.supply/self.skeleton)
        
        # Master source arcs
        for i in range(self.rows):
            self._make_arc(1, i+2, 0, self.supply)
        
        # West/East arcs
        for i in range(self.rows):
            for j in range(self.columns-1):
                c = self.Rng.generate(self.mincost, self.maxcost) # cost
                u = self.Rng.generate(self.mincap, self.maxcap) # capacity
                
                # Skeleton rows
                if i < self.skeleton:
                    # Roll for high cost
                    if self.Rng.generate(1, 100) <= self.hicost:
                        c = self.maxcost
                    # Roll for capacitated
                    if self.Rng.generate(1, 100) <= self.capacitated:
                        u = skeleton_cap
                    else:
                        u = self.supply
                
                self._make_arc(self._coord_id(i, j), self._coord_id(i, j+1),
                               c, u)
        
        # East/West arcs (only if using reverse arcs)
        if self.reverse:
            for i in range(self.rows):
                for j in range(self.columns-1):
                    c = self.Rng.generate(self.mincost, self.maxcost)
                    u = self.Rng.generate(self.mincap, self.maxcap)
                    self._make_arc(self._coord_id(i, j+1),
                                   self._coord_id(i, j), c, u)
        
        # North/South arcs
        for j in range(self.columns):
            for i in range(self.rows-1):
                c = self.Rng.generate(self.mincost, self.maxcost)
                u = self.Rng.generate(self.mincap, self.maxcap)
                self._make_arc(self._coord_id(i, j), self._coord_id(i+1, j),
                               c, u)
            
            # Handle wraparound
            if self.wrap:
                c = self.Rng.generate(self.mincost, self.maxcost)
                u = self.Rng.generate(self.mincap, self.maxcap)
                self._make_arc(self._coord_id(self.rows-1, j),
                               self._coord_id(0, j), c, u)
        
        # South/North arcs
        for j in range(self.columns):
            for i in range(self.rows-1):
                c = self.Rng.generate(self.mincost, self.maxcost)
                u = self.Rng.generate(self.mincap, self.maxcap)
                self._make_arc(self._coord_id(i+1, j), self._coord_id(i, j),
                               c, u)
            
            # Handle wraparound
            if self.wrap:
                c = self.Rng.generate(self.mincost, self.maxcost)
                u = self.Rng.generate(self.mincap, self.maxcap)
                self._make_arc(self._coord_id(0, j),
                               self._coord_id(self.rows-1, j), c, u)
        
        # Northwest/Southeast arcs (only if using diagonal arcs)
        if self.diagonal:
            for j in range(self.columns-1):
                for i in range(self.rows-1):
                    c = self.Rng.generate(self.mincost, self.maxcost)
                    u = self.Rng.generate(self.mincap, self.maxcap)
                    self._make_arc(self._coord_id(i, j),
                                   self._coord_id(i+1, j+1), c, u)
            
                # Handle wraparound
                if self.wrap:
                    c = self.Rng.generate(self.mincost, self.maxcost)
                    u = self.Rng.generate(self.mincap, self.maxcap)
                    self._make_arc(self._coord_id(self.rows-1, j),
                                   self._coord_id(0, j+1), c, u)
        
        # Southwest/Northeast arcs (only if using diagonal arcs)
        if self.diagonal:
            for j in range(self.columns-1):
                for i in range(self.rows-1):
                    c = self.Rng.generate(self.mincost, self.maxcost)
                    u = self.Rng.generate(self.mincap, self.maxcap)
                    self._make_arc(self._coord_id(i+1, j),
                                   self._coord_id(i, j+1), c, u)
            
                # Handle wraparound
                if self.wrap:
                    c = self.Rng.generate(self.mincost, self.maxcost)
                    u = self.Rng.generate(self.mincap, self.maxcap)
                    self._make_arc(self._coord_id(0, j),
                                   self._coord_id(self.rows-1, j+1), c, u)
        
        # Southeast/Northwest arcs (only if using diagonal and reverse arcs)
        if self.reverse and self.diagonal:
            for j in range(self.columns-1):
                for i in range(self.rows-1):
                    c = self.Rng.generate(self.mincost, self.maxcost)
                    u = self.Rng.generate(self.mincap, self.maxcap)
                    self._make_arc(self._coord_id(i+1, j+1),
                                   self._coord_id(i, j), c, u)
            
                # Handle wraparound
                if self.wrap:
                    c = self.Rng.generate(self.mincost, self.maxcost)
                    u = self.Rng.generate(self.mincap, self.maxcap)
                    self._make_arc(self._coord_id(0, j+1),
                                   self._coord_id(self.rows-1, j), c, u)
        
        # Northeast/Southwest arcs (only if using diagonal and reverse arcs)
        if self.reverse and self.diagonal:
            for j in range(self.columns-1):
                for i in range(self.rows-1):
                    c = self.Rng.generate(self.mincost, self.maxcost)
                    u = self.Rng.generate(self.mincap, self.maxcap)
                    self._make_arc(self._coord_id(i, j+1),
                                   self._coord_id(i+1, j), c, u)
            
                # Handle wraparound
                if self.wrap:
                    c = self.Rng.generate(self.mincost, self.maxcost)
                    u = self.Rng.generate(self.mincap, self.maxcap)
                    self._make_arc(self._coord_id(self.rows-1, j+1),
                                   self._coord_id(0, j), c, u)
        
        # Master sink arcs
        for i in range(self.rows):
            self._make_arc(self._coord_id(i, self.columns-1),
                           self._node_count, 0, self.supply)
    
    #-------------------------------------------------------------------------
    
    def _make_arc(self, tail, head, cost, cap):
        """Records a new arc and its attributes."""
        
        self._arcs.append((tail, head, cost, cap))
    
    #-------------------------------------------------------------------------
    
    def _coord_id(self, i, j):
        """Returns the node index located at a given grid position.
        
        Row and column numbers begin at 0.
        
        Index 1 is the master source, and the largest index is always the
        master sink. All remaining nodes are labeled according to their grid
        position, with the index ascending along each row from West to East
        and between rows from North to South.
        """
        
        return i*self.columns + j + 2
    
    #-------------------------------------------------------------------------
    
    def write(self, fname=None, markers=False):
        """Writes the completed network to a file (or prints to screen).
        
        Keyword arguments:
        fname -- output file path (default None, which prints to screen)
        markers -- whether to include comments within the output file to
            indicate the different types of arcs (default False)
        
        If markers are included, comments are added to indicate where
        certain ranges of special arcs begin and end, including: master source
        arcs, skeleton rows, and master sink arcs.
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
        f"c   Skeleton rows:        {self.skeleton}\n" +
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
            
            # Objective
            out += "c\nc  *** Maximum flow ***\nc\n"
            out += f"p max {self._node_count} {self._arc_count}\n"
            
            # Supply constraints
            out += "n 1 s\n" # master source
            out += f"n {self._node_count} t\n" # master sink
        
        # Handle min-cost flow problem
        else:
            
            # Objective
            out += "c\nc  *** Minimum cost flow ***\nc\n"
            out += f"p min {self._node_count} {self._arc_count}\n"
            
            # Supply constraints
            out += f"n 1 {self.supply}\n" # master source
            out += f"n {self._node_count} {-self.supply}\n" # master sink
        
        # Same arc attributes for both problem types
        for i in range(len(self._arcs)):
            a = self._arcs[i]
            if markers and i == 0:
                out += "c  *** Master source arcs begin here ***\n"
            if markers and i == self.rows:
                out += "c  *** Master source arcs end here ***\n"
                if self.skeleton > 0:
                    out += "c  *** Skeleton arcs begin here ***\n"
            if (markers and self.skeleton > 0 and
                i == self.rows + self.skeleton*(self.columns-1)):
                out += "c  *** Skeleton arcs end here ***\n"
            if markers and i == len(self._arcs) - self.rows:
                out += "c  *** Master sink arcs begin here ***\n"
            out += f"a {a[0]} {a[1]} {a[2]} {a[3]}\n"
            if markers and i == len(self._arcs) - 1:
                out += "c  *** Master sink arcs end here ***\n"
        
        # Write or print string
        if fname is None:
            print(out)
        else:
            with open(fname, 'w') as f:
                print(out[:-1], file=f)
        
        return 0
