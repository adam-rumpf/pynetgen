"""List-like object for use in NETGEN.

This submodule defines a minor modification of a list called an "index list",
as described in the original C implementation of NETGEN.
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
    Be aware that the behavior of this class is not defined for methods other
    than those required by NETGEN, which include:
        __init__, pop
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
            self._pseudo_size = 0

        else:

            # Otherwise verify that bounds are numeric
            try:
                a = int(a)
                b = int(b)
            except (TypeError, ValueError):
                raise TypeError("index list bounds must be integer")
            
            # Verify that bound values are valid
            if b < a:
                raise ValueError("index list bounds must satisfy b >= a")
            
            # If bounds are valid, initialize a list from a range
            super().__init__(range(a, b+1))
            self._pseudo_size = super().__len__()

    #-------------------------------------------------------------------------

    def pop(self, index=-1):
        """Removes and returns an item at a given index.

        Keyword arguments:
        index -- index of the element to remove (default last)

        The index list behavior of this class is mostly unchanged from that of
        lists, except that it returns 0 rather than raising an exception when
        an invalid index is chosen, and calling it always reduces the pseudo
        size.

        Aliases: pop, choose_index, remove_index
        """

        # Decrement pseudo size (unless already zero)
        if self._pseudo_size > 0:
            self._pseudo_size -= 1

        # Attempt to pop the specified element
        try:
            # Pop element if valid
            return super().pop(index)
        except IndexError:
            # Return 0 if not
            return 0

    # Aliases
    choose_index = pop
    remove_index = pop

    #-------------------------------------------------------------------------

    @property
    def pseudo_size(self):
        """Pseudo size attribute required by NETGEN.

        The index list's pseudo size is usually simply equal to its length,
        but it decrements whenever an attempt is made to remove an element
        from the list, regardless of whether the attempt was successful.

        The pseudo size is prohibited from decreasing below 0.
        """

        return max(self._pseudo_size, 0)

    @pseudo_size.setter
    def pseudo_size(self, num):
        self._pseudo_size = num
