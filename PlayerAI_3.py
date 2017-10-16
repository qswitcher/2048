from random import randint
from BaseAI_3 import BaseAI
from math import log
import time

timeLimit = 0.2 - 0.05
MAX_DEPTH = 4

def isOver(startTime):
    return time.clock() - startTime > timeLimit

def minimize(state, alpha, beta, startTime, depth = MAX_DEPTH):
    if isOver(startTime) or state.isGoal() or depth == 0:
        return (state, state.eval())
    
    (minChild, minUtility) = (None, float('inf'))

    # I'm a dumbass, the computer just inserts tiles, not UP, DOWN, LEFT, RIGHT
    for child in state.bestAiChildren():
        (_, utility) = maximize(child, alpha, beta, startTime, depth - 1)

        if utility < minUtility:
            (minChild, minUtility) = (child, utility)

        if minUtility <= alpha:
            break
        
        if minUtility < beta:
            beta = minUtility

    return (minChild, minUtility)

def maximize(state, alpha, beta, startTime, depth = MAX_DEPTH):
    if isOver(startTime) or state.isGoal() or depth == 0:
        return (state, state.eval())

    (maxChild, maxUtility) = (None, float('-inf'))

    for child in state.children(True):
        (_, utility) = minimize(child, alpha, beta, startTime, depth - 1)

        if utility > maxUtility:
            (maxChild, maxUtility) = (child, utility)
        
        if maxUtility >= beta:
            break

        if maxUtility > alpha:
            alpha = maxUtility

    return (maxChild, maxUtility)

def decision(state):
    (child, _) = maximize(state, float('-inf'), float('inf'), time.clock()) 

    # print("")
    # for k, v in child.eval(True).items():
    #     print(k.ljust(10), v)
    return child

def cellOccupied(grid, pos):
    return grid.getCellValue(pos) > 0

def smoothness(grid):
    result = 0
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
                    if (nextValue is not None) and (nextValue > 0):
                        targetValue = log(nextValue) / log(2)
                        result -= abs(value - targetValue)
    return result

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
                cv = grid.getCellValue((x, current))
                currentValue = log(grid.getCellValue((x, current))) / log(2)

            nextValue = 0
            if cellOccupied(grid, (x, nxt)):
                nv = grid.getCellValue((x, nxt))
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
                cv = grid.getCellValue((current, y))
                currentValue = log(grid.getCellValue((current, y))) / log(2)

            nextValue = 0
            if cellOccupied(grid, (nxt, y)):
                nv = grid.getCellValue((nxt, y))
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
    
    def isGoal(self):
        return len(self.grid.getAvailableMoves()) == 0

    def averageTileValue(self):
        averageTileValue = 0
        sumTiles = 0
        for i in range(4):
            for j in range(4):
                value = self.grid.getCellValue((i, j))
                averageTileValue += value
                if value > 0:
                    sumTiles += 1
        averageTileValue = log(averageTileValue/sumTiles)/log(2)
        return averageTileValue

    def eval(self, factored=False):
        coefs = self.coefs
        # max tile
        available = len(self.grid.getAvailableCells());
        factors = {
            'averageTile'    : coefs[0]*self.averageTileValue(),
            'available'  : coefs[1]*available,
            'monacity'   : coefs[2]*monacity(self.grid),
            'smoothness' : coefs[3]*smoothness(self.grid)
        }

        if factored:
            return factors
        return sum(factors.values())

    def bestAiChildren(self):
        # moves for 2 and 4
        children = []
        for value in [2,4]:
            for pos in self.grid.getAvailableCells():
                gridCopy = self.grid.clone()
                gridCopy.insertTile(pos, value)
                children.append(State(gridCopy, None, self.coefs))

        # sort by heuristic
        return sorted(children, key=lambda c: c.eval())


    def children(self, reversed=False):
        children = []

        for d in range(4):
            gridCopy = self.grid.clone()

            if gridCopy.move(d):
                children.append(State(gridCopy, d, self.coefs))
 
        # order them in order of which is the best move
        return sorted(children, key=lambda c: c.eval(), reverse=reversed)

class PlayerAI(BaseAI):
    def __init__(self, coefficients = [0, 10, 1, 0]):
        self.coefs = coefficients

    def getMove(self, grid):
        # moves = grid.getAvailableMoves()
        # return moves[randint(0, len(moves) - 1)] if moves else None
        return decision(State(grid, None, self.coefs)).move
