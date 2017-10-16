import unittest
from PlayerAI_3 import *
from Grid_3 import *
from Displayer_3 import *

class TestPlayerAI(unittest.TestCase):

    def test_monacity1(self):
        # displayer 	= Displayer()
        gridValues = [[2, 2, 4, 0],
                      [8, 4, 0, 0],
                      [2, 0, 0, 0],
                      [0, 0, 0, 0]]
        grid = Grid()
        for i in range(4):
            for j in range(4):
                grid.insertTile((i, j), gridValues[i][j]) 
        # displayer.display(grid)

        # -4 penalty
        self.assertEquals(monacity(grid), -4)

    def test_monacity2(self):
        # displayer 	= Displayer()
        gridValues = [[2, 0, 0, 0],
                      [0, 0, 0, 0],
                      [0, 0, 0, 0],
                      [0, 0, 0, 0]]
        grid = Grid()
        for i in range(4):
            for j in range(4):
                grid.insertTile((i, j), gridValues[i][j]) 
        # displayer.display(grid)

        self.assertEquals(monacity(grid), 0)

    def test_monacity3(self):
        # displayer 	= Displayer()
        gridValues = [[8, 4, 2, 0],
                      [4, 2, 0, 0],
                      [2, 0, 0, 0],
                      [0, 0, 0, 0]]
        grid = Grid()
        for i in range(4):
            for j in range(4):
                grid.insertTile((i, j), gridValues[i][j]) 
        # displayer.display(grid)

        # perfectly monotonic, so zero penalty
        self.assertEquals(monacity(grid), 0)

    def test_monacity4(self):
        # displayer 	= Displayer()
        gridValues = [[0, 0, 0, 0],
                      [0, 8, 4, 2],
                      [0, 4, 2, 0],
                      [0, 2, 0, 0]]
        grid = Grid()
        for i in range(4):
            for j in range(4):
                grid.insertTile((i, j), gridValues[i][j]) 
        # displayer.display(grid)

        # perfectly monotonic, so zero penalty
        self.assertEquals(monacity(grid), -10)

    def test_smoothness1(self):
        # displayer 	= Displayer()
        gridValues = [[2, 2, 2, 2],
                      [2, 2, 2, 2],
                      [2, 2, 2, 2],
                      [2, 2, 2, 2]]
        grid = Grid()
        for i in range(4):
            for j in range(4):
                grid.insertTile((i, j), gridValues[i][j]) 

        self.assertEquals(smoothness(grid), 0)
        
    def test_smoothness2(self):
        # displayer 	= Displayer()
        gridValues = [[2, 2, 2, 0],
                      [2, 2, 0, 2],
                      [2, 4, 2, 2],
                      [2, 2, 2, 2]]
        grid = Grid()
        for i in range(4):
            for j in range(4):
                grid.insertTile((i, j), gridValues[i][j]) 

        self.assertEquals(smoothness(grid), -4)


if __name__ == '__main__':
    unittest.main()