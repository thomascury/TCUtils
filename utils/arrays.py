class Array(object):
    def __init__(self, default_value=None):
        self._default_value = default_value
        self._inner = {}

    def __setitem__(self, coords, value):
        if not isinstance(coords, tuple):
            raise TypeError("%s coordinates should be a tuple of int values" % self.__class__.__name__)
        # print("Set coords:%s to value:%s"%(str(coords), str(value)))
        self._inner[coords] = value

    def __getitem__(self, coords):
        if not isinstance(coords, tuple):
            raise TypeError("%s coordinates should be a tuple of int values" % self.__class__.__name__)
        # print("Get coords:%s"%str(coords))
        return self._inner.get(coords, self._default_value)


class FixedDimArray(Array):
    """FixedDimArray is an Array
    which forces to use n dimensions
    coordinates to address its content"""
    def __init__(self, dimensions, default_value=None):
        super(FixedDimArray, self).__init__(default_value)
        self._dimensions = dimensions

    def __setitem__(self, coords, value):
        if not len(coords) == self._dimensions:
            raise KeyError("%s coordinates should be %s items tuple" % (self.__class__.__name__, self._dimensions))
        super(FixedDimArray, self).__setitem__(coords, value)

    def __getitem__(self, coords):
        if not len(coords) == self._dimensions:
            raise KeyError("%s coordinates should be %s items tuple" % (self.__class__.__name__, self._dimensions))
        return super(FixedDimArray, self).__getitem__(coords)


class Matrix(FixedDimArray):
    """Matrix is a symmetrical, fixed
    size 2 dimensions Array with all
    items initialized"""
    def __init__(self, size, initial_value):
        super(Matrix, self).__init__(2)
        self._size = size
        self._initial_value = initial_value
        self._initialize_board(initial_value)

    def _initialize_board(self, value):
        for y in range(self._size):
            for x in range(self._size):
                self[x, y] = value

    def __repr__(self):
        ret = "\n"
        for y in range(self._size):
            ret += "+" + "++++"*self._size + "\n"
            # ret += "+" + "   +"*self._size + "\n"
            ret += "+"
            for x in range(self._size):
                ret += " " + str(self[x, y]) + " +"
            ret += "\n"
            # ret += "+" + "   +"*self._size + "\n"
        ret += "+" + "++++"*self._size + "\n"
        return ret


class MathMatrix(Matrix):
    """MathMatrix is a Matrix with
    default value set to 0 and only
    accepting 0 or 1 as set value"""
    def __init__(self, size):
        super(MathMatrix, self).__init__(size, 0)

    def __setitem__(self, coords, value):
        if value not in (0, 1):
            raise ValueError("%s item value should be either 0 or 1" % self.__class__.__name__)
        super(MathMatrix, self).__setitem__(coords, value)


class TicTacToeBoard(Matrix):
    """TicTacToeBoard is a special
    Matrix of size 3, with default value
    set to ' ' and only accepting
    'X' or 'O' as set value"""
    def __init__(self):
        self._initializing = True
        super(TicTacToeBoard, self).__init__(3, " ")
        self._initializing = False

    def __setitem__(self, coords, value):
        if value not in ('X', 'O') and not (self._initializing and value == self._initial_value):
            raise ValueError("%s item value should be either 'X' or 'O'" % self.__class__.__name__)
        super(Matrix, self).__setitem__(coords, value)


def main():
    b = TicTacToeBoard()
    b[0, 1] = 'X'
    b[1, 2] = ' '
    print(b)

if __name__ == '__main__':
    main()
