from random import randint
from BaseAI_3 import BaseAI
from math import log
import time

timeLimit = 0.2 - 0.05
MAX_DEPTH = 4


def isOver(startTime):
    return time.clock() - startTime > timeLimit

def addToTable(child, utility, table):
    table[str(child.grid.map)] = utility

def getFromTable(child, table):
    if child is None:
        return None
    return table.get(str(child.grid.map), None)

def minimize(state, alpha, beta, startTime, depth, transposition_table):
    # kill recursion and discard value if timeout is reached
    if isOver(startTime):
        return (None, None)

    if state.isGoal() or depth == 0:
        return (state, state.eval())
    
    (minChild, minUtility) = (None, float('inf'))

    # I'm a dumbass, the computer just inserts tiles, not UP, DOWN, LEFT, RIGHT
    for child in state.bestAiChildren(transposition_table):
        (_, utility) = maximize(child, alpha, beta, startTime, depth - 1, transposition_table)
        # abandon recursion if timeout is reached
        if _ is None:
            return (None, None)

        if utility < minUtility:
            (minChild, minUtility) = (child, utility)

        if minUtility <= alpha:
            break
        
        if minUtility < beta:
            beta = minUtility

    addToTable(minChild, minUtility, transposition_table)

    return (minChild, minUtility)

def maximize(state, alpha, beta, startTime, depth, transposition_table = {}):
    if isOver(startTime):
        return (None, None)

    if state.isGoal() or depth == 0:
        return (state, state.eval())

    (maxChild, maxUtility) = (None, float('-inf'))

    for child in state.children(transposition_table):
        (_, utility) = minimize(child, alpha, beta, startTime, depth - 1, transposition_table)
        # abandon recursion if timeout is reached
        if _ is None:
            return (None, None)

        if utility > maxUtility:
            (maxChild, maxUtility) = (child, utility)
        
        if maxUtility >= beta:
            break

        if maxUtility > alpha:
            alpha = maxUtility

    addToTable(maxChild, maxUtility, transposition_table)

    return (maxChild, maxUtility)

def decision(state):
    start = time.clock()
    maxDepth = 1
    best = state

    while not isOver(start):
        (child, score) = maximize(state, float('-inf'), float('inf'), start, maxDepth) 
        if child is None or child.move is None:
            break
        best = child
        maxDepth += 1
    return best
    # for k, v in child.eval(True).items():
        # print(k.ljust(10), v)
    # return child

def cellOccupied(grid, pos):
    return grid.getCellValue(pos) > 0

def gradient(grid):
    mask = [[-3, -2, -1, 0],
            [-2, -1, 0,  1],
            [-1, 0, 1, 0],
            [0, 1, 2, 3]]

    value = 0
    for x in range(4):
        for y in range(4):
            cv = grid.getCellValue((x, y))
            if cv > 0:
                value += mask[x][y]*log(cv)/log(2)
    return value

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

def safe_log(value):
    if value > 0:
        return log(value)/log(2)
    return 0

def bestUtility(child, table):
    value = getFromTable(child, table)
    return child.eval() if value is None else value

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
            cv = grid.getCellValue((x, current))
            while nxt<4 and cv == 0:
                nxt += 1

            if nxt>=4:
                nxt -= 1
            
            currentValue = safe_log(cv)

            nv = grid.getCellValue((x, nxt))
            nextValue = safe_log(nv)

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
            cv = grid.getCellValue((current, y))
            while nxt<4 and cv == 0:
                nxt += 1

            if nxt>=4:
                nxt -= 1
            
            currentValue = safe_log(cv)

            nextValue = 0
            nv = grid.getCellValue((nxt, y))
            nextValue = safe_log(nv)

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
        if available > 0:
            available = log(available)
        else:
            available = -10000000

        corners = []
        for i in range(0, 4, 3):
            for j in range(0, 4, 3):
                corners.append(self.grid.getCellValue((i, j)))

        factors = {
            'maxValue'    : coefs[0]*log(self.grid.getMaxTile())/log(2),
            'available'  : coefs[1]*available,
            'monacity'   : coefs[2]*monacity(self.grid),
            'smoothness' : coefs[3]*smoothness(self.grid),
            'gradient':  coefs[4]*gradient(self.grid)
        }

        if factored:
            return factors
        return sum(factors.values())

    def bestAiChildren(self, table):
        # moves for 2 and 4
        children = []
        for value in [2,4]:
            for pos in self.grid.getAvailableCells():
                gridCopy = self.grid.clone()
                gridCopy.insertTile(pos, value)
                children.append(State(gridCopy, None, self.coefs))

        # sort by heuristic
        return sorted(children, key=lambda c: bestUtility(c, table))


    def children(self, table):
        children = []

        for d in range(0, 4):
            gridCopy = self.grid.clone()

            if gridCopy.move(d):
                children.append(State(gridCopy, d, self.coefs))
 
        # order them in order of which is the best move
        return sorted(children, key=lambda c: bestUtility(c, table), reverse=True)

class PlayerAI(BaseAI):
    #  'maxValue'    : coefs[0]*log(self.grid.getMaxTile())/log(2),
    #         'available'  : coefs[1]*available,
    #         'monacity'   : coefs[2]*monacity(self.grid),
    #         'smoothness' : coefs[3]*smoothness(self.grid),
    #         'gradient'
    # 0.1 1 1
    def __init__(self, coefficients = [0, 1, 0.4, 0.25, 0], debug = False):
        self.coefs = coefficients
        self.debug = debug

    def getMove(self, grid):
        # moves = grid.getAvailableMoves()
        # return moves[randint(0, len(moves) - 1)] if moves else None
        move =  decision(State(grid, None, self.coefs)).move
        if self.debug:
            self.printEval(grid)
        return move

    def printEval(self, grid):
        print('\ncoefs')
        for k, v in State(grid, None, self.coefs).eval(True).items():
            print(k.ljust(10), v)
