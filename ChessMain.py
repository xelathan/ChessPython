"""
driver file - handles user input and displays current GameState object
"""
import sys

import pygame as p
import pygame.image

import ChessEngine

WIDTH = HEIGHT = 512
DIMENSION = 8   #Chessboard 8x8
SQ_SIZE = HEIGHT // DIMENSION   #Size of squares
MAX_FPS = 15    #For animations
IMAGES = {}

"""
Load Images - init global dictionary of images. Called once in the main file
Scales the Image too
"""

def loadImages():
    pieces = ["wp", "wR", "wN", "wB", "wK", "wQ", "bp", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load('chess_assets/' + piece + '.png'), (SQ_SIZE, SQ_SIZE))
    #Access Image by using key

"""
Main Driver - user input and update graphics
"""

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))

    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False    #flag var when a move is made

    loadImages()     #only do this once

    running = True
    sqSelected = ()     #no sq is selected initially
    playerClicks = []   #keeps track of player clicks (2 tuples : [(6, 4), (4, 4)])
    while running:
        for event in pygame.event.get():
            if event.type == p.QUIT:
                running = False
                sys.exit()

            elif event.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() #(x,y) location of the mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE

                if sqSelected == (row, col):    #user clicked the same square twice then deselect
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)     #append for both 1st and 2nd clicks

                if len(playerClicks) == 2:  #check to see if it is the 2nd click
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())
                    if move in validMoves:
                        gs.makeMove(move)
                        moveMade = True
                    sqSelected = ()
                    playerClicks = []

            elif event.type == p.KEYDOWN:
                if event.key == p.K_ESCAPE:
                    running = False
                    sys.exit()
                if event.key == p.K_z:
                    gs.undoMove()
                    moveMade = True

        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False
        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.update()

"""
responsible for all graphics on game screen
"""
def drawGameState(screen, gs):
    drawBoard(screen)
    drawPieces(screen, gs.board)

"""
draws squares on the board
"""
def drawBoard(screen):
    cellDimension = WIDTH // DIMENSION
    colors = [p.Color('white'), p.Color('gray')]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[(row + col) % 2]
            p.draw.rect(screen, color, p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


"""
draws pieces on the board using current game state board var
"""
def drawPieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


if __name__ == "__main__":
    main()