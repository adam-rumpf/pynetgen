"""A copy of the random number generator from the C implementation of NETGEN.

This is a copy of the random integer generation function from the original C
implementation of NETGEN by Norbert Schlenker. It acts as the default RNG for
PyNETGEN, meaning that the C implementation and PyNETGEN will both produce
identical networks given the same set of inputs and the same RNG seed.
"""

import random

def netgen_random(a, b, seed=0):
    """Generates a random integer in the interval [a,b].
    
    Positional arguments:
    a -- nonnegative integer lower bound of random number interval (inclusive)
    b -- nonnegative integer upper bound of random number interval (inclusive,
        assumed to be greater than or equal to a)
    
    Keyword arguments:
    seed -- seed value
    
    Returns:
    random integer on the interval [a,b]
    
    The primary purpose of this function within NETGEN is for generating a
    deterministic sequence of pseudorandom values within the network
    generation process. Because of this it is expected that the previous
    output of netgen_random() will be stored and used as the seed argument
    the next time that netgen_random() is called.
    """
    
    # Ensure that a and b are nonnegative integers satisfying b >= a >= 0
    a = int(a)
    b = int(b)
    if a < 0:
        raise ValueError("random number bounds must be nonnegative")
    if b <= a:
        return b
    
    # RNG algorithm
    hi = 16807 * (seed >> 16)
    lo = 16807 * (seed & 0xffff)
    hi += lo >> 16
    lo &= 0xffff
    lo += hi >> 15
    hi &= 0x7fff
    lo -= 2147483647
    if (seed == (hi << 16) + lo) < 0:
        seed += 2147483647
    return a + seed % (b - a + 1)
