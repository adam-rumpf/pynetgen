"""Tools for iteratively generating pseudorandom integers.

This submodule defines classes for generating sequences of pseudorandom
numbers. The NetgenRandom class uses the random number generator from the
original C implementation of NETGEN, while the StandardRandom class uses
the random number generator from the Python standard library.
"""

import random

#=============================================================================

class StandardRandom:
    """Random number generator based on the Python standard library.
    
    This is a class for generating sequences of random integers using the
    Python standard library random module. It is initialized with a seed
    value (defaulting to a random value based on the system time) and it
    stores the previously-generated value.
    
    A subclass of this class, NetgenRandom, replaces the Python standard
    library random number generation with the pseudorandom generator from the
    original C implementation of NETGEN.
    """

    #-------------------------------------------------------------------------

    def __init__(self, seed=-1):
        """Random integer generator object constructor.

        Keyword arguments:
        seed -- nonnegative integer seed value (defaults to a seed chosen
            uniformly at random from [1,99999999] based on the current system
            time)

        This object maintains its original seed value for use in resetting, as
        well as its previously-generated value (before restricting to the
        requested range).
        """

        # Set attributes
        self.set_seed(seed=seed)

    #-------------------------------------------------------------------------

    def set_seed(self, seed=-1):
        """Sets the seed value of this random number generator.

        Keyword arguments:
        seed -- nonnegative integer seed value (defaults to a seed chosen
            uniformly at random from [1,99999999] by the Python standard
            library's random number generator)
        """

        # Validate and set seed value
        self.seed = int(seed)
        if self.seed <= 0:
            random.seed() # reseed RNG based on system time
            self.seed = random.randint(1, 99999999)
        self.reset() # reset previous value
    
    #-------------------------------------------------------------------------

    def reset(self):
        """Resets the previously-generated value to equal the seed."""

        self.previous = self.seed
        random.seed(self.seed)

    #-------------------------------------------------------------------------

    def generate(self, a, b):
        """Generates a random integer on [a,b].

        Positional arguments:
        a -- nonnegative integer lower bound of random number interval [a,b]
        b -- nonnegative integer lower bound of random number interval [a,b]

        Returns:
        random integer chosen uniformly at random from [a,b] by this object's
            random number generator based on its current seed
        
        Calling this method also updates this object's previously-generated
        value attribute (before restricting to the requested range).
        
        The bounds are meant to satisfy b >= a. In the case of b <= a, the
        output is always chosen to be b, but the random iterator is still
        updated.
        """

        # Ensure that a and b are nonnegative integers
        a = int(a)
        b = int(b)
        if a < 0 or b < 0:
            raise ValueError("random number bounds must be nonnegative")

        # Apply the standard library random number generator
        num = random.randint(min(a,b), max(a,b)) # choose a random number
        self.previous = num # update previous value

        # Decide which value to output
        if b <= a:
            return b
        else:
            return num

#=============================================================================

class NetgenRandom(StandardRandom):
    """Random number generator based on the original implementation of NETGEN.
    
    This is a subclass of the standard library random number generator defined
    above, but replaces its random number generator with the pseudorandom
    process used in the original C implementation of NETGEN by Norbert
    Schlenker. By using this, PyNETGEN is capeable of producing networks
    identical to those of NETGEN when given identical parameters and seeds.
    
    This generator is seeded in exactly the same way as StandardRandom, but
    generates its next random value by using its previously-generated value
    as a seed. The original seed is maintained only for use in resetting.
    """

    #-------------------------------------------------------------------------

    def generate(self, a, b):
        """Generates a random integer on [a,b] and updates the seed.

        Positional arguments:
        a -- nonnegative integer lower bound of random number interval [a,b]
        b -- nonnegative integer lower bound of random number interval [a,b]

        Returns:
        random integer chosen uniformly at random from [a,b] by this object's
            random number generator based on its current seed

        Calling this method also updates this object's previously-generated
        value attribute (before restricting to the requested range), which is
        in turn used as the seed for the next pseudorandom value.
        
        The bounds are meant to satisfy b >= a. In the case of b <= a, the
        output is always chosen to be b, but the random iterator is still
        updated.
        """

        # Ensure that a and b are nonnegative integers
        a = int(a)
        b = int(b)
        if a < 0 or b < 0:
            raise ValueError("random number bounds must be nonnegative")

        # C implementation public domain generator
        hi = 16807 * (self.previous >> 16)
        lo = 16807 * (self.previous & 0xffff)
        hi += lo >> 16
        lo &= 0xffff
        lo += hi >> 15
        hi &= 0x7fff
        lo -= 2147483647

        # Update previous value
        self.previous = (hi << 16) + lo
        if self.previous < 0:
            self.previous += 2147483647
        
        # Decide which value to output
        if b <= a:
            return b
        else:
            return a + self.previous % (b - a + 1)
