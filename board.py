import random
import numpy
import math
from scipy import signal

KERNEL = [[1, 1, 1],
          [1, 0, 1],
          [1, 1, 1]]

class Tile:

    def __init__(self):
        self.bombsSurrounding = 0
        self.bomb = False
        self.flag = False
        self.revealed = False

    def setBomb(self, new: bool):
        self.bomb = new

    def placeBomb(self):
        self.setBomb(True)

    def hasBomb(self):
        return self.bomb

    def setSurrounding(self, new: int):
        self.bombsSurrounding = new

    def getSurrounding(self):
        return self.bombsSurrounding

    def reveal(self):
        self.revealed = True 
    
    def isRevealed(self):
        return self.revealed

    def toggleFlag(self):
        self.flag = not self.flag
        return self.flag

    def hasFlag(self):
        return self.flag

class Board:
    
    def __init__(self, width: int, height: int, numBombs: int):
        self.width = width 
        self.height = height
        self.numBombs = numBombs
        self.TileGrid = []
        self.bombGrid = numpy.zeros((self.width, self.height))
        self.convGrid = numpy.zeros((self.width, self.height))
        # Populating with empty cells
        for i in range(width):
            col = []
            for j in range(height):
                col.append(Tile())
            self.TileGrid.append(col)

    def generate_bombs(self, xi, yi):
        bombCoords = []
        # Determining coordinates for bombs
        for i in range(self.numBombs):
            x = y = -1
            while (x, y) in bombCoords or x == -1\
                    or (x, y) == (xi, yi) or\
                    math.sqrt((xi - x)**2 + (yi - y)**2) < 2:
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
            bombCoords.append((x, y))
        # Placing bombs
        for coord in bombCoords:
            x = coord[0]
            y = coord[1]
            self.TileGrid[coord[0]][coord[1]].placeBomb()
            self.bombGrid[x][y] = 1
        # Calculating sums
        self._convolve()

    def reset(self):
        self.TileGrid = []
        self.bombGrid = numpy.zeros((self.width, self.height))
        self.convGrid = numpy.zeros((self.width, self.height))
        # Populating with empty cells
        for i in range(self.width):
            col = []
            for j in range(self.height):
                col.append(Tile())
            self.TileGrid.append(col)

    def _convolve(self):           
        self.convGrid = signal.convolve2d(self.bombGrid, KERNEL, 'same')
        for i in range(self.width):
            for j in range(self.height):
                self.TileGrid[i][j].setSurrounding(int(self.convGrid[i][j]))