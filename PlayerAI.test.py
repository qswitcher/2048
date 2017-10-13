import unittest
from PlayerAI_3 import *
from Grid_3 import *
from Displayer_3 import *

class TestPlayerAI(unittest.TestCase):

    def test_minimize(self):
        displayer 	= Displayer()
        gridValues = [[4, 8, 2, 0],
            [256, 64, 32, 4],
            [1024, 256, 64, 2],
            [512, 32, 16, 8]]
        grid = Grid()
        for i in range(4):
            for j in range(4):
                grid.insertTile((i, j), gridValues[i][j]) 
        displayer.display(grid)

        ai = PlayerAI()
        self.assertEqual(ai.getMove(grid), 2)


if __name__ == '__main__':
    unittest.main()