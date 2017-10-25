from Grid_3       import Grid
from ComputerAI_3 import ComputerAI
from PlayerAI_3   import PlayerAI
from Displayer_3  import Displayer
from random       import randint
import threading
from multiprocessing import Pool
import pprint
import time

defaultInitialTiles = 2
defaultProbability = 0.9

actionDic = {
    0: "UP",
    1: "DOWN",
    2: "LEFT",
    3: "RIGHT"
}

(PLAYER_TURN, COMPUTER_TURN) = (0, 1)

# Time Limit Before Losing
timeLimit = 0.2
allowance = 0.05

class GameManager:
    def __init__(self, size = 4):
        self.grid = Grid(size)
        self.possibleNewTiles = [2, 4]
        self.probability = defaultProbability
        self.initTiles  = defaultInitialTiles
        self.computerAI = None
        self.playerAI   = None
        self.displayer  = None
        self.over       = False
        self.timesup = False

    def setComputerAI(self, computerAI):
        self.computerAI = computerAI

    def setPlayerAI(self, playerAI):
        self.playerAI = playerAI

    def setDisplayer(self, displayer):
        self.displayer = displayer

    def updateAlarm(self, currTime):
        if currTime - self.prevTime > timeLimit + allowance:
            print('Time exceeded')
            self.over = True
            self.timesup = True
        else:
            while time.clock() - self.prevTime < timeLimit + allowance:
                pass

            self.prevTime = time.clock()

    def start(self):
        for i in range(self.initTiles):
            self.insertRandonTile()

        # self.displayer.display(self.grid)

        # Player AI Goes First
        turn = PLAYER_TURN
        maxTile = 0

        self.prevTime = time.clock()

        while not self.isGameOver() and not self.over:
            # Copy to Ensure AI Cannot Change the Real Grid to Cheat
            gridCopy = self.grid.clone()

            move = None

            if turn == PLAYER_TURN:
                move = self.playerAI.getMove(gridCopy)

                # Validate Move
                if move != None and move >= 0 and move < 4:
                    if self.grid.canMove([move]):
                        self.grid.move(move)

                        # Update maxTile
                        maxTile = self.grid.getMaxTile()
                    else:
                        print("Invalid PlayerAI Move")
                        self.over = True
                else:
                    print("Invalid PlayerAI Move - 1")
                    self.over = True
            else:
                move = self.computerAI.getMove(gridCopy)

                # Validate Move
                if move and self.grid.canInsert(move):
                    self.grid.setCellValue(move, self.getNewTileValue())
                else:
                    print("Invalid Computer AI Move")
                    self.over = True

            # if not self.over:
            #     self.displayer.display(self.grid)

            # Exceeding the Time Allotted for Any Turn Terminates the Game
            self.updateAlarm(time.clock())

            turn = 1 - turn
        if self.timesup:
            print('Time ran out!')
            return -1

        return maxTile

    def isGameOver(self):
        return not self.grid.canMove()

    def getNewTileValue(self):
        if randint(0,99) < 100 * self.probability:
            return self.possibleNewTiles[0]
        else:
            return self.possibleNewTiles[1];

    def insertRandonTile(self):
        tileValue = self.getNewTileValue()
        cells = self.grid.getAvailableCells()
        if len(cells) > 0:
            cell = cells[randint(0, len(cells) - 1)]
            self.grid.setCellValue(cell, tileValue)

def run(coefs):
    
    results = []
    for i in range(20):
        gameManager = GameManager()
        playerAI  	= PlayerAI(coefs)
        computerAI  = ComputerAI()
        displayer 	= Displayer()

        gameManager.setDisplayer(displayer)
        gameManager.setPlayerAI(playerAI)
        gameManager.setComputerAI(computerAI)
        result = gameManager.start()
        print('result=', result)
        if result < 1024:
            print('Failed coefficients ', coefs)
            break
        # displayer.display(gameManager.grid)
        # playerAI.printEval(gameManager.grid)
        results.append(result)

    if len(results) >= 20:
        print('winner!', coefs)
        print('results', results)

    return {'coefs': coefs, 'results': results}

def main():
    # 0 1 1 0.1
    # 'maxTile'
    # 'available'
    # 'monacity'
    # 'smoothness'
    # 'gradient'
    a = [0] # [0.8, 1, 1.2, 1.5, 2.0]
    b = [1]
    c = [0.4] 
    d = [0.17, 0.175, 0.18, 0.185, 0.19, 0.195, 0.20, 0.205, 0.210, 0.215, 0.22, 0.225, 0.23] #[0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]
    e = [0]
    # a, b, c, d, e = [0], [1], [2], [2], [0]

    coefs = []
    for ai in a:
        for bi in b:
            for ci in c:
                for di in d:
                    for ei in e:
                        coefs.append([ai, bi, ci, di, ei])
    with Pool(8) as p:
        results = p.map(run, coefs)
        pp = pprint.PrettyPrinter(indent = 2)
        pp.pprint(results)

if __name__ == '__main__':
    main()
