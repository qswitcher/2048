from random import randint
from BaseAI_3 import BaseAI
from math import log
import time

timeLimit = 0.18

def isOver(startTime):
    return time.clock() - startTime > timeLimit

class State:
    def __init__(self, grid, move, coefs, alpha, beta),:
        self.grid = grid
        self.move = move
        self.coefs = coefs
    
    def eval(self):
        # compute score
        # figure out score based on 
        # score = 0
        # for i in range(4):
        #     for j in range(4): 
        #         p = self.grid.getCellValue((i, j))
        #         if p == 0:
        #             continue
        #         elif p > 2:
        #             score += (log(p)/log(2) - 1)*p 
                

        # available tiles
        available = len(self.grid.getAvailableCells())
        # clustering score
        # clustering = 0
        # total = 0
        # for i in range(4):
        #     for j in range(4):
        #         current = self.grid.getCellValue((i, j))
        #         if current == 0:
        #             continue

        #         for pos in [(i, j-1), (i, j+1), (i-1, j), (i+1, j)]:
        #             value = self.grid.getCellValue(pos)
        #             if value is not None:
        #                 clustering += abs(current - value)
        #                 total += 1
        # if total > 0:
        #     clustering = clustering/total

        # monacity

        # smoothness


        
        return log(self.grid.getMaxTile()) + 2.7*available 


    def children(self, reversed=False):
        children = []
        for move in self.grid.getAvailableMoves():
            grid = self.grid.clone()
            grid.move(move)
            children.append(State(grid, move, self.coefs))
        return sorted(children, key=lambda c: c.eval(), reverse=reversed)

class PlayerAI(BaseAI):
    def __init__(self, coefficients = [1, 1, 1]):
        self.coefs = coefficients

    def getMove(self, grid):
        # moves = grid.getAvailableMoves()
        # return moves[randint(0, len(moves) - 1)] if moves else None
        return decision(State(grid, None, self.coefs)).move
