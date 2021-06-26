"""Tools for generating pseudorandom integers.

This submodule defines a class for generating sequences of pseudorandom
numbers. Options allow it to use either the Python standard library's random
number generator or a copy of the random number generator from the original C
implementation of NETGEN.
"""

import random

#=============================================================================

class RandomIterator:
    """A class for generating sequences of pseudorandom integers.

    This class is initialized with a seed integer and includes a method for
    generating a random integer based on the previous seed value. This both
    outputs a pseudorandom integer chosen from the specified interval and
    replaces the current seed value.

    An option allows the RandomIterator object to utilize either the Python
    standard library's random functions, or a copy of the random number
    generator from the original C implementation of NETGEN by Norbert
    Schlenker. In this way PyNETGEN is capeable of producing networks
    identical to those of NETGEN when given identical parameters and seeds.
    """

    #-------------------------------------------------------------------------

    def __init__(self, seed=-1, pseudo=True):
        """Random integer generator object constructor.

        Keyword arguments:
        seed -- nonnegative integer seed value (defaults to a seed chosen
            uniformly at random from [1,99999999] by the Python standard
            library's random number generator)
        pseudo -- boolean value indicating whether to use the original C
            implementation's random number generator over the Python standard
            library's random number generator (default True); if True the C
            implementation's generator is used; if False the random module
            is used

        The RandomIterator object maintains a seed attribute which is
        overwritten whenever its generate() function is called. If the C
        implementation's generator is used, then two RandomIterator objects
        initialized with identical seeds will produce identical sequences of
        seed values as their generate() methods are called repeatedly.
        """

        # Set attributes
        self.set_seed(seed=seed)
        self.pseudo = pseudo

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
            self.seed = random.randint(1, 99999999)

    #-------------------------------------------------------------------------

    def generate(self, a, b):
        """Generates a random integer on [a,b] and updates the seed.

        Positional arguments:
        a -- nonnegative integer lower bound of random number interval [a,b]
        b -- nonnegative integer lower bound of random number interval [a,b]

        Returns:
        random integer chosen uniformly at random from [a,b] by this object's
            random number generator based on its current seed

        Calling this method also overwrites this object's seed value with one
        generated from its current seed value.
        """

        # Ensure that a and b are nonnegative integers satisfying b >= a >= 0
        a = int(a)
        b = int(b)
        if a < 0:
            raise ValueError("random number bounds must be nonnegative")
        if b <= a:
            return b

        # Choose which random number generator to use
        if self.pseudo == True:

            # C implementation public domain generator
            hi = 16807 * (self.seed >> 16)
            lo = 16807 * (self.seed & 0xffff)
            hi += lo >> 16
            lo &= 0xffff
            lo += hi >> 15
            hi &= 0x7fff
            lo -= 2147483647

            # Update seed value
            self.seed = (hi << 16) + lo
            if self.seed  < 0:
                self.seed += 2147483647

            return a + self.seed % (b - a + 1)

        else:

            # Python standard library random generator
            state = random.getstate() # save state
            random.seed(self.seed) # apply this object's seed
            num = random.randint(a, b) # choose a random number

            # Update seed value
            random.seed(self.seed)
            self.set_seed(-1) # overwrite seed
            random.setstate(state) # reload state

            return num
