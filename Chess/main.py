"""
This is our main driver file. 
It will be responsble for handling user input and displaying the current GameState object.    
"""

import pygame as p
from Chess import engine
from AI_Move import get_best_move

Width = Height = 512
Dimension = 8  # Dimension of chess board are 8*8
SQ_Size = Height // Dimension
Max_fps = 15  # for animation
Images = {}

"""
Initialize a global dictionary of images. This will be called exactly once in the main
"""


def load_images():
    pieces = ["wP", "wR", "wN", "wB", "wK", "wQ", "bP", "bR", "bN", "bB", "bK", "bQ"]
    for piece in pieces:
        Images[piece] = p.transform.scale(
            p.image.load("Chess/Images/" + piece + ".png"), (SQ_Size, SQ_Size)
        )
    # Note: we can access an image by saying 'Images['wP']'


"""
Highlight square selected and moves for piece selected
"""


def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():  # تأكد إن في حاجة متأشرة
        r, c = sqSelected
        if gs.board[r][c][0] == (
            "w" if gs.WhiteToMove else "b"
        ):  # sqSelected is a piece that can be moved
            # highlight selected square
            s = p.Surface((SQ_Size, SQ_Size))
            s.set_alpha(
                100
            )  # قيمة الشفافية , لو بتساوي 0 فهي شفافة تماما ولو بتساوي 255 فهي معتمه
            s.fill(p.Color("blue"))
            screen.blit(s, (c * SQ_Size, r * SQ_Size))
            # highlight moves from that square
            s.fill(p.Color("yellow"))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_Size, move.endRow * SQ_Size))


"""
responsble  for all the graphics within a current game state.
"""


def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)  # Drow squares on the screen
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)  # Drow the pieces on top of those squares


"""
Drow the squares on the board. the top left square is always light.
"""


def drawBoard(screen):
    global colors
    colors = [p.Color(160, 110, 60), p.Color(245, 245, 220)]
    for r in range(Dimension):
        for c in range(Dimension):
            color = colors[((r + c) % 2)]
            p.draw.rect(
                screen, color, p.Rect(c * SQ_Size, r * SQ_Size, SQ_Size, SQ_Size)
            )


"""
Drow the pieces on the board using the current GameState.board 
"""


def drawPieces(screen, board):
    for r in range(Dimension):
        for c in range(Dimension):
            piece = board[r][c]
            if piece != "  ":
                screen.blit(
                    Images[piece], p.Rect(c * SQ_Size, r * SQ_Size, SQ_Size, SQ_Size)
                )


"""
Animating a move
"""


def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10  # Frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (
            move.startRow + dR * frame / frameCount,
            move.startCol + dC * frame / frameCount,
        )
        drawBoard(screen)
        drawPieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(
            move.endCol * SQ_Size, move.endRow * SQ_Size, SQ_Size, SQ_Size
        )
        p.draw.rect(screen, color, endSquare)
        # draw captured piece onto rectangle
        if move.pieceCaptured != "  ":
            screen.blit(Images[move.pieceCaptured], endSquare)
        # draw moving piece
        screen.blit(
            Images[move.pieceMoved], p.Rect(c * SQ_Size, r * SQ_Size, SQ_Size, SQ_Size)
        )
        p.display.flip()
        clock.tick(60)


def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color("Gray"))
    textLocation = p.Rect(0, 0, Width, Height).move(
        Width / 2 - textObject.get_width() / 2, Height / 2 - textObject.get_height() / 2
    )
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))


"""
The main driver for our code. This will handle user input and updating the graphics.
"""


def main():
    p.init()
    screen = p.display.set_mode((Width, Height))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = engine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False  # Variable for when move is made
    animate = False  # flag variable for when we should animate a move
    load_images()  # Only do this once, Before the while loop.
    running = True
    sqSelected = ()  # No square is selected, keep track of the last click of user (tuple: (row, col))
    playerClicks = []  # keep track  of player clicks (two tuple: [(6, 4), (4, 4)])
    gameOver = False
    playerOne = True  # If a human is playing white, then this will be True. If an AI is playing, then False
    playerTwo = False  # Same as above but for black

    while running:
        humanTurn = (gs.WhiteToMove and playerOne) or (not gs.WhiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # Mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()  # (x, y) location of mouse
                    col = location[0] // SQ_Size
                    row = location[1] // SQ_Size
                    if sqSelected == (
                        row,
                        col,
                    ):  # The user clicked the same square twice
                        sqSelected = ()  # Unselected
                        playerClicks = []  # Clear player clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)  # Append for 1st and 2nd clicks
                    if len(playerClicks) == 2:  # After 2nd Click
                        move = engine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()  # Reset user clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]

            # key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # Undo when 'z' is pressed
                    gs.undoMove()
                    moveMade = True
                    animate = False
                if e.key == p.K_r:  # reset the board when 'r' is pressed
                    gs = engine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

        # AI move finder
        if not gameOver and not humanTurn:
            AI_move = get_best_move(gs)
            if AI_move:
                gs.makeMove(AI_move)
                moveMade = True
                animate = True

        if moveMade:
            if animate:
                animateMove(gs.moveHistory[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)

        if gs.checkmate:
            gameOver = True
            if gs.WhiteToMove:
                drawText(screen, "Black wins by checkmate")
            else:
                drawText(screen, "White wins by checkmate")
        elif gs.stalemate:
            gameOver = True
            drawText(screen, "Stalemate")

        clock.tick(Max_fps)
        p.display.flip()


if __name__ == "__main__":
    main()
