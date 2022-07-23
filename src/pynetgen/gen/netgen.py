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
        self.supply = int(supply)
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
        
        # Initialize random number generation object
        if rng == 0:
            self.Rng = NetgenRandom(seed)
        elif rng == 1:
            self.Rng = StandardRandom(seed)
        else:
            raise ValueError("RNG index must be 0 or 1")
        
        # Initialize attributes for temporary storage
        self._arc_count = 0 # number of arcs generated so far
        self._nodes_left = nodes - sinks + tsinks # nodes left to generate
        
        # Determine which type of problem to generate
        if ((self.sources - self.tsources + self.sinks - self.tsinks ==
            self.nodes) and sources - tsources == sinks - tsinks and
            sources == supply):
            self._create_assignment()
        elif mincap == 1.0 and maxcap == 1.0:
            self._create_problem(maxflow=True)
        else:
            self._create_problem(maxflow=False)
    
    #-------------------------------------------------------------------------
    
    def _create_problem(self, maxflow=False):
        """Generates a min-cost flow or max-flow problem.
        
        Keyword arguments:
        maxflow -- True for a max flow problem, False for min-cost flow
            (default False)
        """
        
        ### RNG test
        print("RNG test:")
        for i in range(10):
            print(self.Rng.generate(1, 3))
        self.Rng.set_seed(self.seed)
        print()
        
        # Initialize variables
        pred = [None for i in range(self.nodes)] # temporary node predecessors
        head = [None for i in range(self.density)] # temporary arc heads
        tail = head[:] # temporary arc tails
        self._from = head[:] # final arc tails
        self._to = head[:] # final arc heads
        self._c = head[:] # final arc costs
        self._u = head[:] # final arc capacities
        
        # Set supply values
        self.b = [0 for i in range(self.nodes)] # node supply values
        self._create_supply()
        
        # Form most of the network skeleton by forming chains of transshipment
        # nodes from the sources (stored via predecessor lists)
        
        # Point sources at selves
        for i in range(1, self.sources+1):
            pred[i] = i
        ###
        print("pred, after pointing sources at selves")
        print(pred)
        
        # Make an index list for the nodes
        IndList = IndexList(self.sources + 1, self.nodes - self.sinks)
        source = 1
        
        # Distribute the first 60% of transshipment nodes evenly among sources
        for i in range(self.nodes - self.sources - self.sinks,
                      int((4*(self.nodes-self.sources-self.sinks)+9)/10), -1):
            s = str(i) + ' ' + str(len(IndList)) + ' '###
            temp = self.Rng.generate(1, len(IndList))###
            s += str(temp) + ' '###
            node = IndList.pop(temp)
            s += str(node)###
            pred[node] = pred[source]
            pred[source] = node
            source += 1
            if source > self.sources:
                source = 1
            print(s)###
        print()###
        
        # Distribute the remaining transshipment nodes randomly
        while i > 1:
            i -= 1
            print("i=" + str(i) + ", index size=" + str(len(IndList)) + ", ")###
            temp = self.Rng.generate(1, len(IndList))###
            print("list index=" + str(temp) + ", ")###
            node = IndList.pop(temp)
            print("node=" + str(node) + ", SOURCES=" + str(self.sources) + ", ")###
            source = self.Rng.generate(1, self.sources)
            print("source=" + str(source))###
            pred[node] = pred[source]
            pred[source] = node
        
        del IndList
        
        ###
        print("pred, after the initial source chains:")
        print(pred)
        
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
            
            ###
            print("Source " + str(source) + " head/tail/pred:")
            print(head)
            print(tail)
            print(pred)
            
            # Choose number of sinks to link to this chain
            if self.nodes == self.sources + self.sinks:
                print("Case A")###
                sinks_per_source = int(self.sinks/self.sources) + 1
            else:
                print("Case B")###
                print("Sort count " + str(sort_count))###
                sinks_per_source = 2*int((sort_count*self.sinks)/
                                   (self.nodes - self.sources - self.sinks))
            sinks_per_source = max(2, min(sinks_per_source, self.sinks))
            print("Sinks per source: " + str(sinks_per_source) + "\n")###
            
            # Choose the sinks to link to this chain
            sinks = [None for i in range(self.nodes)]
            IndList = IndexList(self.nodes - self.sinks, self.nodes - 1)
            for i in range(sinks_per_source):
                temp = self.Rng.generate(1, len(IndList))###
                sinks[i] = IndList.pop(temp)
                print(str(temp) + ' ' + str(sinks[i]))###
            print("Sinks linked to source " + str(source))###
            print(sinks)###
            print("Predecessor list:")###
            print(pred)###
            
            # Ensure that any unselected sinks are chosen for the last source
            if source == self.sources and len(IndList) > 0:
                print("Last source.")###
                while len(IndList) > 0:
                    j = IndList.pop(1)
                    if self.b[j] == 0:
                        sinks[sinks_per_source] = j
                        sinks_per_source += 1
                print("Updated sink list:")###
                print(sinks)###
            
            del IndList
            
            # Distribute supply among the selected sinks
            print("="*60)###
            print("Predecessor list:")###
            print(pred)###
            print()###
            chain_length = sort_count
            supply_per_sink = self.b[source-1]//sinks_per_source
            print("Supply per sink: " + str(supply_per_sink) + "\n")###
            k = pred[source]
            print("Processing node " + str(k))###
            for i in range(sinks_per_source):
                sort_count += 1
                print(sort_count)###
                partial_supply = self.Rng.generate(1, supply_per_sink)
                print(partial_supply)###
                j = self.Rng.generate(0, sinks_per_source - 1)
                print(j)###
                tail[sort_count] = k
                head[sort_count] = sinks[i] + 1
                print("(" + str(tail[sort_count]) + "," + str(head[sort_count]) + ")")
                self.b[sinks[i]] -= partial_supply
                self.b[sinks[j]] -= supply_per_sink - partial_supply
                print(self.b)###
                k = source
                for j in range(self.Rng.generate(1, chain_length), 0, -1):
                    k = pred[k]
                    print("Processing node " + str(k))###
            self.b[sinks[0]] -= self.b[source-1] % sinks_per_source
            print("\nB: " + str(self.b) + "\n")###
            print("-"*60)###
            
            # Sort skeleton arcs into a canonical order
            print("Pre-sort tails/heads:")###
            print(tail)###
            print(head)###
            self._sort_skeleton(sort_count, tail, head)
            tail[sort_count+1] = 0
            print("Post-sort tails/heads:")###
            print(tail)###
            print(head)###
            
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
                        cap = max(self.b[source-1], self.mincap)
                    
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
        
        ###
        print("Assignment problem")###
    
    #-------------------------------------------------------------------------
    
    def _create_supply(self):
        """Sets supply values of all nodes."""
        
        supply_per_source = int(self.supply/self.sources)
        for i in range(self.sources):
            partial_supply = self.Rng.generate(1, supply_per_source)
            self.b[i] += partial_supply
            self.b[self.Rng.generate(0, self.sources-1)] += (supply_per_source
                                                             - partial_supply)
        self.b[self.Rng.generate(0, self.sources-1)] += (self.supply %
                                                         self.sources)
        
        ###
        print("b[], after create_supply()")
        print(self.b)
    
    #-------------------------------------------------------------------------
    
    def _sort_skeleton(self, sort_count, tail, head):
        """Conduct a shell sort of a portion of the skeleton arcs by tail."""
        
        m = sort_count
        print(sort_count)###
        m //= 2
        while m != 0:
            print("!")###
            k = sort_count - m
            for j in range(1, k+1):
                print("?")###
                i = j
                while i >= 1 and tail[i] > tail[i+m]:
                    print(f"({i},{j},{k}")###
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
