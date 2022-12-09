import pygame as p
from Chess import ChessEngine, RandomMove

WIDTH = 512
HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 160
IMAGES = {}


def loadImage():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bp", "wR", "wN", "wB", "wQ", "wK", "wp"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("Chess/image/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption("Chess _ Ngo Van Huy 20204657 _ IT1 _ 05 _ K65 _ HUST")
    clock = p.time.Clock()
    gs = ChessEngine.gameState()
    validMoves = gs.getValidMoved()
    moveMade = False
    animate = False
    loadImage()
    running = True
    sqSelected = ()
    playerClicks = []
    gameOver = False
    playerOne = True
    playerTwo = True

    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col):
                        sqSelected = ()
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)

                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []

                        if not moveMade:
                            playerClicks = [sqSelected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    animate = False
                    moveMade = True
                if e.key == p.K_r:
                    gs = ChessEngine.gameState()
                    validMoves = gs.getValidMoved()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False

        # AI Move thinking
        if not gameOver and not humanTurn:
            AIMove = RandomMove.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animation(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoved()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected)
        if gs.checkMate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Black wins by checkmate")
            else:
                drawText(screen, "White wins by checkmate")
        elif gs.staleMate:
            gameOver = True
            drawText(screen, "Stalemate")
        clock.tick(MAX_FPS)
        p.display.flip()


def hightlightSquares(screen, gs, validMoves, sqSelected):
    if len(gs.moveLog) > 0:
        lastMove = gs.moveLog[-1]
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(200)
        s.fill(p.Color("Light Blue"))
        screen.blit(s, (lastMove.endCol * SQ_SIZE, lastMove.endRow * SQ_SIZE))
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(50)
            s.fill(p.Color('green'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            s.set_alpha(150)
            s.fill(p.Color('light blue'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))


def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    hightlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs.board)


def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            color = colors[((i + j) % 2)]
            p.draw.rect(screen, color, p.Rect(j * SQ_SIZE, i * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    for i in range(DIMENSION):
        for j in range(DIMENSION):
            piece = board[i][j]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(j * SQ_SIZE, i * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def animation(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10
    framesCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(framesCount + 1):
        r, c = (move.startRow + dR * frame / framesCount, move.startCol + dC * frame / framesCount)
        drawBoard(screen)
        drawPieces(screen, board)

        color = colors[(move.startRow + move.endRow) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)

        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(160)


def drawText(screen, text):
    font = p.font.SysFont("Helvita", 32, True, False)
    textObject = font.render(text, False, p.Color('Gray'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObject.get_width() / 2,
                                                    HEIGHT / 2 - textObject.get_height() / 2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, False, p.Color('Black'))
    screen.blit(textObject, textLocation.move(2, 2))
    textObject = font.render(text, False, p.Color('Gray'))
    screen.blit(textObject, textLocation.move(4, 4))
    textObject = font.render(text, False, p.Color('Black'))
    screen.blit(textObject, textLocation.move(6, 6))

#
# if __name__ == "__main__":
#     main()
