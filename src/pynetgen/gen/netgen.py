"""Classes and methods for the NETGEN network generation algorithm."""

from pynetgen.util.ilist import IndexList
from pynetgen.util.randit import NetgenRandom
from pynetgen.util.randit import StandardRandom
from pynetgen._version import __version__

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
                    rng=0, type=None):
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
        capacitated -- percent of skeleton arcs (0-100) that are capacitated
            (default 100)
        mincap -- minimum arc capacity (default 100)
        maxcap -- maximum arc capacity (default 1000)
        rng -- index of random network generator to use (default 0),
            including:
            0: the original NETGEN pseudorandom number generator
            1: the Python standard library random number generator
        type -- problem type override (default None); setting to an integer
            attempts to generate the specified type of problem and ignores the
            default behavior explained below:
            0: minimum-cost flow
            1: maximum flow
            2: transportation
        
        All keyword arguments besides the RNG selection and the file name are
        identical to those of the original C implementation of NETGEN. All
        network parameters are integer.
        
        The problem type is implicitly chosen based on the network attributes
        (unless the "type" attribute is set). By default the problem is
        minimum-cost flow. It is a transportation problem instead if the total
        number of sources and sinks equals the total number of nodes, and if
        no transshipment sources or sinks are specified. It is a maximum flow
        problem if it is not a transportation problem, and if the minimum and
        maximum arc costs are both exactly 1.
        """
        
        # Validate inputs and convert to correct data types
        self.seed = int(seed)
        self.nodes = int(nodes)
        if self.nodes < 0:
            raise ValueError("node count must be nonnegative")
        self.sources = int(sources)
        if self.sources < 0:
            raise ValueError("source count must be nonnegative")
        self.sinks = int(sinks)
        if self.sinks < 0:
            raise ValueError("sink count must be nonnegative")
        if self.sources + self.sinks > self.nodes:
            raise ValueError("source/sink count cannot exceed node count")
        self.density = int(density)
        if self.density < 1:
            raise ValueError("arc count must be nonnegative")
        if self.nodes > self.density:
            raise ValueError("node count must exceed arc count")
        self.mincost = int(mincost)
        self.maxcost = int(maxcost)
        if self.mincost > self.maxcost:
            raise ValueError("min cost cannot exceed max cost")
        self.supply = max(int(supply), 0)
        self.tsources = int(tsources)
        if self.tsources < 0:
            raise ValueError("transshipment source count must be nonnegative")
        if self.tsources > self.sources:
            raise ValueError("transshipment sources cannot exceed sources")
        self.tsinks = int(tsinks)
        if self.tsinks < 0:
            raise ValueError("transshipment sink count must be nonnegative")
        if self.tsinks > self.sinks:
            raise ValueError("transshipment sinks cannot exceed sinks")
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
            if type < 0 or type > 2:
                raise ValueError("problem type index must be 0-2 or None")
        
        # Initialize random number generation object
        if rng == 0:
            self.Rng = NetgenRandom(seed)
        elif rng == 1:
            self.Rng = StandardRandom(seed)
        else:
            raise ValueError("RNG index must be 0 or 1")
        self.seed = self.Rng.seed # copy RNG's seed in case of -1
        
        # Initialize attributes for temporary storage
        self._arc_count = 0 # number of arcs generated so far
        self._nodes_left = self.nodes - self.sinks + self.tsinks # nodes to gen
        self._b = [0 for i in range(self.nodes)] # node supply values
        self._type = 0 # problem type (0: mincost, 1: maxflow, 2:assignment)
        self._from = [None for i in range(self.density)] # final arc tails
        self._to = self._from[:] # final arc heads
        self._c = self._from[:] # final arc costs
        self._u = self._from[:] # final arc capacities
        
        # Determine which type of problem to generate
        if type is None:
            if ((self.sources - self.tsources + self.sinks - self.tsinks ==
                self.nodes) and self.sources - self.tsources ==
                self.sinks - self.tsinks and self.sources == self.supply):
                self._type = 2
            elif self.mincost == 1 and self.maxcost == 1:
                self._type = 1
            else:
                self._type = 0
        
        # Choose the correct problem generation method
        if type == 2:
            self._create_assignment()
        self._create_problem()
    
    #-------------------------------------------------------------------------
    
    def _create_problem(self):
        """Generates a min-cost flow or max-flow problem."""
        
        # Initialize variables
        pred = [None for i in range(self.nodes)] # temporary node predecessors
        head = self._from[:] # temporary arc heads
        tail = self._from[:] # temporary arc tails
        
        # Set supply values
        self._create_supply()
        
        # Form most of the network skeleton by forming chains of transshipment
        # nodes from the sources (stored via predecessor lists)
        
        # Point sources at selves
        for i in range(1, self.sources+1):
            pred[i] = i
        
        # Make an index list for the nodes
        IndList = IndexList(self.sources + 1, self.nodes - self.sinks)
        source = 1
        
        # Distribute the first 60% of transshipment nodes evenly among sources
        for i in range(self.nodes - self.sources - self.sinks,
                      int((4*(self.nodes-self.sources-self.sinks)+9)/10), -1):
            node = IndList.pop(self.Rng.generate(1, len(IndList)))
            pred[node] = pred[source]
            pred[source] = node
            source += 1
            if source > self.sources:
                source = 1
        
        # Distribute the remaining transshipment nodes randomly
        while i > 1:
            i -= 1
            node = IndList.pop(self.Rng.generate(1, len(IndList)))
            source = self.Rng.generate(1, self.sources)
            pred[node] = pred[source]
            pred[source] = node
        
        del IndList
        
        # Link each source chain to sinks, assign skeletal arc capacities
        # and costs, then complete the network with random arcs
        
        # Process each source chain
        for source in range(1, self.sources+1):
           
            sort_count = 0 # number of nodes visited in current chain
            node = pred[source] # transshipment node at end of current chain
            
            # Record heads/tails by traversing the chain backwards
            while node != source:
                sort_count += 1
                head[sort_count] = node
                tail[sort_count] = pred[node]
                node = pred[node]
            
            # Choose number of sinks to link to this chain
            if self.nodes == self.sources + self.sinks:
                sinks_per_source = int(self.sinks/self.sources) + 1
            else:
                sinks_per_source = 2*int((sort_count*self.sinks)/
                                   (self.nodes - self.sources - self.sinks))
            sinks_per_source = max(2, min(sinks_per_source, self.sinks))
            
            # Choose the sinks to link to this chain
            sinks = [None for i in range(self.nodes)]
            IndList = IndexList(self.nodes - self.sinks, self.nodes - 1)
            for i in range(sinks_per_source):
                sinks[i] = IndList.pop(self.Rng.generate(1, len(IndList)))
            
            # Ensure that any unselected sinks are chosen for the last source
            if source == self.sources and len(IndList) > 0:
                while len(IndList) > 0:
                    j = IndList.pop(1)
                    if self._b[j] == 0:
                        sinks[sinks_per_source] = j
                        sinks_per_source += 1
            
            del IndList
            
            # Distribute supply among the selected sinks
            chain_length = sort_count
            supply_per_sink = self._b[source-1]//sinks_per_source
            k = pred[source]
            for i in range(sinks_per_source):
                sort_count += 1
                partial_supply = self.Rng.generate(1, supply_per_sink)
                j = self.Rng.generate(0, sinks_per_source - 1)
                tail[sort_count] = k
                head[sort_count] = sinks[i] + 1
                self._b[sinks[i]] -= partial_supply
                self._b[sinks[j]] -= supply_per_sink - partial_supply
                k = source
                for j in range(self.Rng.generate(1, chain_length), 0, -1):
                    k = pred[k]
            self._b[sinks[0]] -= self._b[source-1] % sinks_per_source
            
            # Sort skeleton arcs into a canonical order
            self._sort_skeleton(sort_count, tail, head)
            tail[sort_count+1] = 0
            
            # Assign attributes to skeleton arcs
            i = 1
            while i <= sort_count:

                IndList = IndexList(self.sources-self.tsources+1, self.nodes)
                IndList.remove(tail[i])
                it = tail[i]
                
                while it == tail[i]:
                
                    IndList.remove(head[i])
                    
                    # Determine capacity
                    cap = self.supply
                    if self.Rng.generate(1, 100) <= self.capacitated:
                        cap = max(self._b[source-1], self.mincap)
                    
                    # Determine cost
                    cost = self.maxcost
                    if self.Rng.generate(1, 100) > self.hicost:
                        cost = self.Rng.generate(self.mincost, self.maxcost)
                    
                    # Record attributes
                    self._from[self._arc_count] = it
                    self._to[self._arc_count] = head[i]
                    self._c[self._arc_count] = cost
                    self._u[self._arc_count] = cap
                    
                    self._arc_count += 1
                    i += 1
                
                self._pick_head(IndList, it)
                del IndList
            
        # Complete network with random arcs
        for i in range(self.nodes - self.sinks + 1,
                       self.nodes - self.sinks + self.tsinks):
            IndList = IndexList(self.sources-self.tsources+1, self.nodes)
            IndList.remove(i)
            self._pick_head(IndList, i)
            del IndList
        
        return self._arc_count
    
    #-------------------------------------------------------------------------
    
    def _create_assignment(self):
        """Generates an assignment problem."""
        
        for source in range(self.nodes/2):
            self._b[source] = 1
        while source < self.nodes:
            self._b[source] = -1
            source += 1
        
        Skeleton = IndexList(self.sources+1, self.nodes)
        for source in range(1, self.nodes/2 + 1):
            index = Skeleton.pop(self.Rng.generate(1, len(Skeleton)))
            
            self._from[self._arc_count] = source
            self._to[self._arc_count] = index
            self._c[self._arc_count] = self.Rng.generate(self.mincost,
                                                         self.maxcost)
            self._u[self._arc_count] = 1
            self._arc_count += 1
            
            IndList = IndexList(self.sources+1, self.nodes)
            IndList.remove(index)
            self._pick_head(IndList, source)
            
            del IndList
        
        del Skeleton
    
    #-------------------------------------------------------------------------
    
    def _create_supply(self):
        """Sets supply values of all nodes."""
        
        supply_per_source = int(self.supply/self.sources)
        for i in range(self.sources):
            partial_supply = self.Rng.generate(1, supply_per_source)
            self._b[i] += partial_supply
            self._b[self.Rng.generate(0, self.sources-1)] += (supply_per_source
                                                             - partial_supply)
        self._b[self.Rng.generate(0, self.sources-1)] += (self.supply %
                                                         self.sources)
    
    #-------------------------------------------------------------------------
    
    def _sort_skeleton(self, sort_count, tail, head):
        """Conduct a shell sort of a portion of the skeleton arcs by tail."""
        
        m = sort_count
        m //= 2
        while m != 0:
            k = sort_count - m
            for j in range(1, k+1):
                i = j
                while i >= 1 and tail[i] > tail[i+m]:
                    tail[i], tail[i+m] = tail[i+m], tail[i]
                    head[i], head[i+m] = head[i+m], head[i]
                    i -= m
            m //= 2
    
    #-------------------------------------------------------------------------
    
    def _pick_head(self, IList, desired_tail):
        """Pick the next skeleton head during skeleton arc generation."""
        
        non_sources = self.nodes - self.sources + self.tsources
        remaining_arcs = self.density - self._arc_count
        
        self._nodes_left -= 1
        if 2*self._nodes_left >= remaining_arcs:
            return None
        
        if ((remaining_arcs+non_sources-IList.pseudo_size-1)/
            (self._nodes_left+1) >= non_sources - 1):
            limit = non_sources
        else:
            upper_bound = 2*(remaining_arcs/(self._nodes_left + 1) - 1)
            while True:
                limit = self.Rng.generate(1, upper_bound)
                if self._nodes_left == 0:
                    limit = remaining_arcs
                if self._nodes_left*(non_sources-1) >= remaining_arcs - limit:
                    break
        
        while limit > 0:
            limit -= 1
            index = IList.pop(self.Rng.generate(1, IList.pseudo_size))
            cap = self.supply
            if self.Rng.generate(1, 100) <= self.capacitated:
                cap = self.Rng.generate(self.mincap, self.maxcap)
        
            if 1 <= index and index <= self.nodes:
                self._from[self._arc_count] = desired_tail
                self._to[self._arc_count] = index
                self._c[self._arc_count] = self.Rng.generate(self.mincost,
                                                             self.maxcost)
                self._u[self._arc_count] = cap
                self._arc_count += 1
    
    #-------------------------------------------------------------------------
    
    def write(self, fname=None):
        """Writes the completed network to a file (or prints to screen).
        
        Keyword arguments:
        fname -- output file path (default None, which prints to screen)
        """
        
        # Begin to write output string
        out = (f"c PyNETGEN v{__version__}\n" +
        "c $ pip install pynetgen\nc\n" +
        "c  NETGEN flow network generation algorithm\n" +
        "c  Problem input parameters\n" +
        "c  " + "-"*37 + "\n" +
        f"c   Random seed:          {self.seed}\n" +
        f"c   Number of nodes:      {self.nodes}\n" +
        f"c   Source nodes:         {self.sources}\n" +
        f"c   Sink nodes:           {self.sinks}\n" +
        f"c   Number of arcs:       {self.density}\n" +
        f"c   Minimum arc cost:     {self.mincost}\n" +
        f"c   Maximum arc cost:     {self.maxcost}\n" +
        f"c   Total supply:         {self.supply}\n" +
        "c   Transshipment -\n" +
        f"c     Sources:            {self.tsources}\n" +
        f"c     Sinks:              {self.tsinks}\n" +
        "c   Skeleton arcs -\n" +
        f"c     With max cost:      {self.hicost}\n" +
        f"c     Capacitated:        {self.capacitated}\n" +
        f"c   Minimum arc capacity: {self.mincap}\n" +
        f"c   Maximum arc capacity: {self.maxcap}\n")
        
        # Handle assignment problem
        if self._type == 2:
            out += "c\nc  *** Assignment ***\nc\n"
            out += f"p asn {self.nodes} {self._arc_count}\n"
            for i in range(self.nodes):
                if self._b[i] > 0:
                    out += f"n {i+1}\n"
            for i in range(self._arc_count):
                out += f"a {self._from[i]} {self._to[i]} {self._c[i]}\n"
        
        # Handle max flow problem
        elif self._type == 1:
            out += "c\nc  *** Maximum flow ***\nc\n"
            out += f"p max {self.nodes} {self._arc_count}\n"
            for i in range(self.nodes):
                if self._b[i] > 0:
                    out += f"n {i+1} s\n"
                elif self._b[i] < 0:
                    out += f"n {i+1} t\n"
            for i in range(self._arc_count):
                out += f"a {self._from[i]} {self._to[i]} {self._u[i]}\n"
        
        # Handle min-cost flow problem
        else:
            out += "c\nc  *** Minimum cost flow ***\nc\n"
            out += f"p min {self.nodes} {self._arc_count}\n"
            for i in range(self.nodes):
                if self._b[i] != 0:
                    out += f"n {i+1} {self._b[i]}\n"
            for i in range(self._arc_count):
                out += (f"a {self._from[i]} {self._to[i]} 0 {self._u[i]}" +
                        f" {self._c[i]}\n")
        
        # Write or print string
        if fname is None:
            print(out)
        else:
            with open(fname, 'w') as f:
                print(out[:-1], file=f)
        
        return 0
