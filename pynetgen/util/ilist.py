"""List-like object for use in NETGEN.

This submodule submodule defines a minor modification of a list called an
"index list", as described in the original C implementation of NETGEN.
"""

#=============================================================================

class IndexList(list):
    """List-like class for choosing sequences of integers without repetition.

    This is an implementation of the "index list" described in the original C
    implementation of NETGEN. The original implementation consisted of a
    linked list, initialized as a sequence of consecutive integers, and
    equipped with methods for removing and returning elements at a specified
    index. It also maintained a "pseudo_size" attribute which incorporates the
    number of failed index removal attempts, and was necessary to correct for
    a bug in the initial description of NETGEN.

    This version is implemented as a subclass of Python's built-in list class.
    """

    #-------------------------------------------------------------------------

    def __init__(self, a=None, b=None):
        """Index list constructor.

        Keyword arguments:
        a -- integer index at which to begin the index list (default None)
        b -- integer index at which to end the index list (default None)

        The contents of the index list will be initialized as an ascending
        sequence of consecutive integers a, a+1, a+2, ..., b-1, b. It is
        assumed that b >= a.

        If either bound is left unspecified, the list will begin empty.
        """

        # Initialize list contents
        if a == None or b == None:

            # If missing a bound, initialize an empty list
            super().__init__()
            self.pseudo_size = 0

        else:

            # Otherwise verify bounds
            try:
                a = int(a)
                b = int(b)
                if b < a:
                    raise ValueError("index list bounds must satisfy b >= a")

                # If bounds are valid, initialize a list from a range
                super().__init__(range(a, b+1))
                self.pseudo_size = b - a + 1
            except TypeError:
                raise TypeError("index list bounds must be integer")
            except ValueError:
                raise TypeError("index list bounds must be integer")

### "Index list": ascending sequence of positive integers with the following operations:
### make_index_list() - makes a list of consecutive integers
### choose_index() - removes the kth element and removes it
### remove_index() - removes the kth index
### index_size() - returns number of stored elements
### pseudo_size() - (technical)
