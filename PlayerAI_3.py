from random import randint
from BaseAI_3 import BaseAI
from math import log
import time

timeLimit = 0.15

def isOver(startTime):
    return time.clock() - startTime > timeLimit

def minimize(state, alpha, beta, startTime):
    if state.isGoal() or isOver(startTime):
        return (None, state.eval())
    
    (minChild, minUtility) = (None, float('inf'))

    for child in state.children():
        (_, utility) = maximize(child, alpha, beta, startTime)

        if utility < minUtility:
            (minChild, minUtility) = (child, utility)

        if minUtility <= alpha:
            break
        
        if minUtility < beta:
            beta = minUtility

    return (minChild, minUtility)

def maximize(state, alpha, beta, startTime):
    if state.isGoal() or isOver(startTime):
        return (None, state.eval())

    (maxChild, maxUtility) = (None, float('-inf'))

    for child in state.children(True):
        (_, utility) = minimize(child, alpha, beta, startTime)

        if utility > maxUtility:
            (maxChild, maxUtility) = (child, utility)
        
        if maxUtility >= beta:
            break

        if maxUtility > alpha:
            alpha = maxUtility

    return (maxChild, maxUtility)

def decision(state):
    (child, _) = maximize(state, float('-inf'), float('inf'), time.clock())
    return child

class State:
    def __init__(self, grid, move):
        self.grid = grid
        self.move = move

    def isGoal(self):
        return self.grid.getMaxTile() == 2048
    
    def eval(self):
        # compute score
        # figure out score based on 
        score = 0
        for i in range(4):
            for j in range(4): 
                p = self.grid.getCellValue((i, j))
                if p == 0:
                    continue
                elif p > 2:
                    score += (log(p)/log(2) - 1)*p 
                

        # available tiles
        available = len(self.grid.getAvailableCells())

        # clustering score
        clustering = 0
        total = 0
        for i in range(4):
            for j in range(4):
                current = self.grid.getCellValue((i, j))
                if current == 0:
                    continue

                for pos in [(i, j-1), (i, j+1), (i-1, j), (i+1, j)]:
                    value = self.grid.getCellValue(pos)
                    if value is not None:
                        clustering += abs(current - value)
                        total += 1
        if total > 0:
            clustering = clustering/total

        
        utility = score + log(score)*available - clustering if score > 0 else 0

        return max(utility, min(score, 1))

    def children(self, reversed=False):
        children = []
        for move in self.grid.getAvailableMoves():
            grid = self.grid.clone()
            grid.move(move)
            children.append(State(grid, move))
        return sorted(children, key=lambda c: c.eval(), reverse=reversed)

class PlayerAI(BaseAI):
    def getMove(self, grid):
        # moves = grid.getAvailableMoves()
        # return moves[randint(0, len(moves) - 1)] if moves else None
        return decision(State(grid, None)).move
