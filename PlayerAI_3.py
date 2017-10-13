from random import randint
from BaseAI_3 import BaseAI
from math import log
import time

timeLimit = 0.16

def isOver(startTime):
    return time.clock() - startTime > timeLimit

def minimize(state, alpha, beta, startTime):
    if isOver(startTime):
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
    if isOver(startTime):
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

def cellOccupied(grid, pos):
    return grid.getCellValue(pos) > 0

def smoothness(grid):
    value = 0
    for x in range(4):
        for y in range(4):
            if cellOccupied(grid, (x, y)):
                value = log(grid.getCellValue((x,y))) /log(2)
                for vector in [(1,0),(0,1)]:
                    nextPoint = (x + vector[0], y + vector[1])

                    # proceed in the next direction while it's empty
                    while grid.getCellValue(nextPoint) == 0:
                        nextPoint = (nextPoint[0] + vector[0], nextPoint[1] + vector[1])
                    nextValue = grid.getCellValue(nextPoint)
                    if nextValue is not None and nextValue > 0:
                        targetValue = log(nextValue) / log(2)
                        value -= abs(value - targetValue)
    return value

def monacity(grid):
    # measures how monotonic the grid is. This means the values of the tiles are strictly increasing
    # or decreasing in both the left/right and up/down directions
    # scores for all four directions
    totals = [0, 0, 0, 0]

    # up/down direction
    for x in range(4):
        current = 0
        nxt = current+1
        while nxt <4:
            while nxt<4 and not cellOccupied(grid, (x, nxt)):
                nxt += 1

            if nxt>=4:
                nxt -= 1
            currentValue = 0
            if cellOccupied(grid, (x, current)):
                currentValue = log(grid.getCellValue((x, current))) / log(2)

            nextValue = 0
            if cellOccupied(grid, (x, nxt)):
                nextValue = log(grid.getCellValue((x, nxt))) / log(2)

            if currentValue > nextValue:
                totals[0] += nextValue - currentValue
            elif nextValue > currentValue:
                totals[1] += currentValue - nextValue
            
            current = nxt
            nxt += 1

    # left right
    for y in range(4):
        current = 0
        nxt = current+1
        while nxt <4:
            while nxt<4 and not cellOccupied(grid, (nxt, y)):
                nxt += 1

            if nxt>=4:
                nxt -= 1
            currentValue = 0
            if cellOccupied(grid, (current, y)):
                currentValue = log(grid.getCellValue((current, y))) / log(2)

            nextValue = 0
            if cellOccupied(grid, (nxt, y)):
                nextValue = log(grid.getCellValue((nxt, y))) / log(2)

            if currentValue > nextValue:
                totals[2] += nextValue - currentValue
            elif nextValue > currentValue:
                totals[3] += currentValue - nextValue
            
            current = nxt
            nxt += 1

    return max(totals[0], totals[1]) + max(totals[2], totals[3])

class State:
    def __init__(self, grid, move, coefs):
        self.grid = grid
        self.move = move
        self.coefs = coefs
    
    def eval(self):
        # max tile
        maxTileValue = self.grid.getMaxTile()

        # available tiles
        available = len(self.grid.getAvailableCells())

        # monacity
        monacityValue = monacity(self.grid)

        # smoothness
        smoothnessValue = smoothness(self.grid)

        # print(maxTileValue, 2.7*log(available), monacityValue, 0.1*smoothnessValue)
        return maxTileValue + 2.7*log(available) + monacityValue + 0.1*smoothnessValue


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
