
import pygame
import tkinter
from tkinter import messagebox
from queue import PriorityQueue
from timeit import default_timer as timer

ROWS = 40
WIDTH_PER_SQUARE = 18
WINDOW_DIMENSION = ROWS * WIDTH_PER_SQUARE

pygame.init()
root = pygame.display.set_mode((WINDOW_DIMENSION, WINDOW_DIMENSION))
pygame.display.set_caption('PATH FINDER')


COLORS = {
    'white' : (255, 255, 255) ,
    'black' : (0, 0, 0) ,
    'orange' : (255, 140, 0) ,
    'pink' : (255, 105, 180) ,
    'darkslategrey' : (47, 79, 79) ,
    'red' : (220, 20, 60) ,
    'green' : (144, 238, 144) ,
    'purple' : (128, 0, 128)
}



class Square :
    
    def __init__ ( self, row, col, width ) :
        self.row = row
        self.col = col
        self.x = width * col
        self.y = width * row
        self.width = width
        self.color = COLORS['white']
        self.isObstacle = False
        self.isChecked = False
        self.neighbours = list()
        
    def draw ( self, window ) :
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.width))
        
    def getPos ( self ) :
        return (self.row, self.col)
        
    def updateNeighbours ( self, grid ) :
        if self.row < ROWS-1 and not grid[self.row+1][self.col].isObstacle :
            self.neighbours.append( grid[self.row+1][self.col] )
            
        if self.row > 0 and not grid[self.row-1][self.col].isObstacle :
            self.neighbours.append( grid[self.row-1][self.col] )
            
        if self.col < ROWS-1 and not grid[self.row][self.col+1].isObstacle :
            self.neighbours.append( grid[self.row][self.col+1] )
            
        if self.col > 0 and not grid[self.row][self.col-1].isObstacle :
            self.neighbours.append( grid[self.row][self.col-1] )



def makeGrid ( rows, width ) :
    grid = list()
    
    for row in range(rows) :
        grid.append(list())
        
        for col in range(rows) :
            grid[row].append( Square(row, col, width) )
            
    return grid



def drawGrid (window) :
    for x in range(0,ROWS) : # HORIZONTAL LINES
        pygame.draw.line(window, COLORS['darkslategrey'], (0, x*WIDTH_PER_SQUARE), (WINDOW_DIMENSION, x*WIDTH_PER_SQUARE), 2)
        
    for x in range(0,ROWS) : # VERTICAL LINES
        pygame.draw.line(window, COLORS['darkslategrey'], (x*WIDTH_PER_SQUARE, 0), (x*WIDTH_PER_SQUARE, WINDOW_DIMENSION), 2)
    


def draw_screen (window, grid) :
    root.fill(COLORS['white'])
    
    for row in grid :
        for square in row :
            square.draw(window)
            
    drawGrid(window)
        
    pygame.display.update()



def getPositionInGrid(coordinate) :
    return coordinate[1]//WIDTH_PER_SQUARE, coordinate[0]//WIDTH_PER_SQUARE



def createStartNode(grid, pos) :
    grid[pos[0]][pos[1]].color = COLORS['orange']
    return pos
    
    
def createEndNode(grid, pos) :
   
    grid[pos[0]][pos[1]].color = COLORS['pink']
    return pos
    
    
def createObstacle(grid, position, start, end) :
    
    pos = getPositionInGrid(position)
    if pos != start.getPos() and pos != end.getPos() :
        grid[pos[0]][pos[1]].color = COLORS['black']
        grid[pos[0]][pos[1]].isObstacle = True
        
        
def removeObstacle(grid, position) :
    
    pos = getPositionInGrid(position)
    square = grid[pos[0]][pos[1]]
    if square.isObstacle :
        square.color = COLORS['white']
        square.isObstacle = False
        
        
def resetTerminal(grid, pos, start, end) :
    square = grid[pos[0]][pos[1]]
    
    if square == start :    
        square.color = COLORS['white']
        return 0
        
    if square == end :    
        square.color = COLORS['white']
        return 1
    
    return -1
        
        

def h_score (node1, node2) :
    x1, y1 = node1.getPos()
    x2, y2 = node2.getPos()
    
    return abs(x2-x1) + abs(y2-y1)
    
    

def runAlgorithm(window, grid, start, end, showVis) :
    startTime = timer()
    gScores = dict()
    
    for row in grid :
        for square in row :
            square.updateNeighbours(grid)
            gScores[square] = float('inf')
            
    gScores[start] = 0
    openSet = PriorityQueue()
    path = dict()
    counter = 0
    openSet.put((h_score(start,end), counter, start))
    openSetTracker = { start }
    
    while len(openSetTracker) :
        currentNode = openSet.get()[2]
        openSetTracker.remove(currentNode)
        
        for event in pygame.event.get() :
            if event.type == pygame.QUIT :
                return False, -1
        
        if currentNode == end :
            current = end
            while current != start :
                current.color = COLORS['purple']
                current = path[current]
                
            start.color = COLORS['orange']
            end.color = COLORS['pink']
            draw_screen(window, grid)
            endTime = timer()
            return True, endTime-startTime
        
        for ng in currentNode.neighbours :
            if not ng.isChecked :
                h = h_score(ng, end)
                g = gScores[currentNode] + 1
                f = h + g
                ng.isChecked = True
                
                if g < gScores[ng] :
                    gScores[ng] = g
                    counter += 1
                    path[ng] = currentNode
                    
                    if not ng in openSetTracker :
                        openSet.put((f, counter, ng))
                        openSetTracker.add(ng)
                        if showVis : ng.color = COLORS['green']
                start.color = COLORS['orange']   
            if showVis : draw_screen(window, grid)
    
    endTime = timer()
    return False, endTime-startTime


def showPopup() :
    popup = tkinter.Tk()
    popup.withdraw()
    showVis = messagebox.askyesno('', 'Do you want the program to show the visualization alongwith the path ?')
    popup.destroy()
    popup.mainloop()
    return showVis
    
    
def main(window) :
    grid = makeGrid(ROWS, WIDTH_PER_SQUARE)
    
    run = True
    startNode = None
    endNode = None
    algoRunning = False
    
    while run :
        
        for event in pygame.event.get() :
            
            if event.type == pygame.QUIT :
                run = False
                
            if event.type == pygame.MOUSEBUTTONDOWN and not algoRunning :
                mousePosition = pygame.mouse.get_pos()
                pos = getPositionInGrid(mousePosition)
                
                if not startNode and ( (endNode and pos != endNode.getPos()) or not endNode ) :
                
                    startNodePos = createStartNode(grid, pos)
                    startNode = grid[startNodePos[0]][startNodePos[1]]
                    
                elif not endNode and ( (startNode and pos != startNode.getPos()) or not startNode ) :
                    endNodePos = createEndNode(grid, pos)
                    endNode = grid[endNodePos[0]][endNodePos[1]]
                    
                elif startNode and endNode :
                    result = resetTerminal(grid, pos, startNode, endNode)
                    if result == 0 : startNode = None
                    if result == 1 : endNode = None
                    
            if event.type == pygame.KEYUP :
                if event.key == pygame.K_SPACE and startNode and endNode :
                    algoRunning = True
                    showVis = showPopup()
                    print ('\nRUNNING THE A* ALGORITHM ...')
                    success, time = runAlgorithm(window, grid, startNode, endNode, showVis)
                    if time == -1 :
                        print('ALGORITHM WAS STOPPED ARBITRARILY !')
                        run = False
                        break
                    print('ALGORITHM COMPLETED IN {:.5f} SECONDS .'.format(time))
                    if success : print('SHORTEST PATH BETWEEN THE TWO TERMINAL NODES WAS FOUND !')
                    else : print('NO PATH WAS FOUND BETWEEN THE TWO TERMINAL NODES !')
                    print('CLICK ON BACKSPACE TO RESTART ...\n')
                    
                if event.key == pygame.K_BACKSPACE :
                    startNode = None
                    endNode = None
                    grid = makeGrid(ROWS, WIDTH_PER_SQUARE)
                    algoRunning = False
        
        if pygame.mouse.get_pressed()[2] and startNode and endNode and not algoRunning :
            mousePosition = pygame.mouse.get_pos()
            createObstacle(grid, mousePosition, startNode, endNode)
            
            
        if pygame.mouse.get_pressed()[0] and not algoRunning :
            mousePosition = pygame.mouse.get_pos()
            removeObstacle(grid, mousePosition)
        
        draw_screen(window, grid)
    
    pygame.quit()
    
 
 
main(root)
 