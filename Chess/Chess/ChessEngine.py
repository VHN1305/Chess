class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.moveFuntions = {
            "p": self.getPawnMoves,
            "R": self.getRockMoves,
            "N": self.getKnightMoves,
            "B": self.getBishopMoves,
            "Q": self.getQueenMoves,
            "K": self.getKingMoves
        }
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.inCheck = False
        self.pin = []
        self.checks = []
        self.promotion = False
        self.empassantPossible = ()
        self.empassantPossible_log = [self.empassantPossible]
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                            self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

    def makeMove(self, move, promotedPiece = 'Q'):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        self.whiteToMove = not self.whiteToMove
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)

        if move.isPawnPromotion:
            self.promotion = True
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + promotedPiece
            self.promotion = False

        if move.isEmPassantMove:
            self.board[move.startRow][move.endCol] = '--'
        if move.pieceMoved[1] == 'p' and abs(move.endRow - move.startRow) == 2:
            self.empassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.empassantPossible = ()

        # self.empassantPossible_log.append(self.empassantPossible)

        if move.isCastleMove:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = '--'

            else:
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = '--'

        self.updateCastling(move)
        self.castleRightLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                                self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)

            if move.isEmPassantMove:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.empassantPossible = (move.endRow, move.endCol)

            if move.pieceMoved[1] == 'p' and abs(move.endRow - move.startRow) == 2:
                self.empassantPossible = ()

            self.castleRightLog.pop()
            self.currentCastlingRight = self.castleRightLog[-1]

            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'

            self.checkMate = False
            self.staleMate = False

    def updateCastling(self, move):
        if move.pieceCaptured == "wR":
            if move.endCol == 0:  # left rook
                self.currentCastlingRight.wqs = False
            elif move.endCol == 7:  # right rook
                self.currentCastlingRight.wks = False
        elif move.pieceCaptured == "bR":
            if move.endCol == 0:  # left rook
                self.currentCastlingRight.bqs = False
            elif move.endCol == 7:  # right rook
                self.currentCastlingRight.bks = False

        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wqs = False
            self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bqs = False
            self.currentCastlingRight.bks = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False

    def getValidMoves(self):
        temp_castle_rights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                          self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)

        moves = []
        self.inCheck, self.pin, self.checks = self.checkForPinsAndCheck()

        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
        if self.inCheck:
            if len(self.checks) == 1:
                moves = self.allGetPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + i * check[2], kingCol + i * check[3])
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break

                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K':
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])

            else:
                self.getKingMoves(kingRow, kingCol, moves)

        else:
            moves = self.allGetPossibleMoves()
            if self.whiteToMove:
                self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
            else:
                self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        if len(moves) == 0:
            if self.inCheckk():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False

        self.currentCastlingRight = temp_castle_rights
        return moves

    def inCheckk(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    def squareUnderAttack(self, row, col):
        self.whiteToMove = not self.whiteToMove
        opponentMoves = self.allGetPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in opponentMoves:
            if move.endRow == row and move.endCol == col:
                return True
        return False

    def allGetPossibleMoves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                color = self.board[row][col][0]
                if (color == "b" and not self.whiteToMove) or (color == "w" and self.whiteToMove):
                    piece = self.board[row][col][1]
                    self.moveFuntions[piece](row, col, moves)
        return moves

    def checkForPinsAndCheck(self):
        pin = []
        checks = []
        incheck = False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:
                            break

                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'p' and (
                                        (enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or \
                                (i == 1 and type == 'K'):
                            if possiblePin == ():
                                incheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:
                                pin.append(possiblePin)
                                break
                        else:
                            break
                else:
                    break
        knighMoves = ((-2, -1), (-2, 1), (-1, 2), (-1, -2), (1, 2), (1, -2), (2, -1), (2, 1))
        for m in knighMoves:
            endRow = startRow + m[0]
            endCol = startCol + m[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    incheck = True
                    checks.append((endRow, endCol, m[0], m[1]))

        return incheck, pin, checks

    def getPawnMoves(self, row, col, moves):
        # piecePinned = False
        # pinDirection = ()
        # for i in range(len(self.pin) - 1, -1, -1):
        #     if self.pin[i][0] == r and self.pin[i][1] == c:
        #         piecePinned = True
        #         pinDirection = (self.pin[i][2], self.pin[i][3])
        #         self.pin.remove(self.pin[i])
        #         break
        # if self.whiteToMove:
        #     kingRow, kingCol = self.whiteKingLocation
        # else:
        #     kingRow, kingCol = self.blackKingLocation
        #
        # if self.whiteToMove:
        #     if self.board[r - 1][c] == '--':
        #         if not piecePinned or pinDirection == (-1, 0):
        #             moves.append(Move((r, c), (r - 1, c), self.board))
        #             if r == 6 and self.board[r - 2][c] == '--':
        #                 moves.append(Move((r, c), (r - 2, c), self.board))
        #
        #     if c - 1 >= 0:
        #         if not piecePinned or pinDirection == (-1, -1):
        #             if self.board[r - 1][c - 1][0] == 'b':
        #                 moves.append(Move((r, c), (r - 1, c - 1), self.board))
        #             elif (r - 1, c - 1) == self.empassantPossible:
        #                 moves.append(Move((r, c), (r - 1, c - 1), self.board, empassantMove=True))
        #
        #     if c + 1 <= 7:
        #         if not piecePinned or pinDirection == (-1, 1):
        #             if self.board[r - 1][c + 1][0] == 'b':
        #                 moves.append(Move((r, c), (r - 1, c + 1), self.board))
        #
        #             elif (r - 1, c + 1) == self.empassantPossible:
        #                 moves.append(Move((r, c), (r - 1, c + 1), self.board, empassantMove=True))
        #
        # else:
        #     if self.board[r + 1][c] == '--':
        #         if not piecePinned or pinDirection == (1, 0):
        #             moves.append(Move((r, c), (r + 1, c), self.board))
        #             if r == 1 and self.board[r + 2][c] == '--':
        #                 moves.append(Move((r, c), (r + 2, c), self.board))
        #
        #     if c - 1 >= 0:
        #         if not piecePinned or pinDirection == (1, -1):
        #             if self.board[r + 1][c - 1][0] == 'w':
        #                 moves.append(Move((r, c), (r + 1, c - 1), self.board))
        #
        #             elif (r + 1, c - 1) == self.empassantPossible:
        #                 moves.append(Move((r, c), (r + 1, c - 1), self.board, empassantMove=True))
        #
        #     if c + 1 <= 7:
        #         if not piecePinned or pinDirection == (1, 1):
        #             if self.board[r + 1][c + 1][0] == 'w':
        #                 moves.append(Move((r, c), (r + 1, c + 1), self.board))
        #
        #             elif (r + 1, c + 1) == self.empassantPossible:
        #                 moves.append(Move((r, c), (r + 1, c + 1), self.board, empassantMove=True))
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pin) - 1, -1, -1):
            if self.pin[i][0] == row and self.pin[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pin[i][2], self.pin[i][3])
                self.pin.remove(self.pin[i])
                break

        if self.whiteToMove:
            move_amount = -1
            startRow = 6
            enemy_color = "b"
            king_row, king_col = self.whiteKingLocation
        else:
            move_amount = 1
            startRow = 1
            enemy_color = "w"
            king_row, king_col = self.blackKingLocation

        if self.board[row + move_amount][col] == "--":  # 1 square pawn advance
            if not piece_pinned or pin_direction == (move_amount, 0):
                moves.append(Move((row, col), (row + move_amount, col), self.board))
                if row == startRow and self.board[row + 2 * move_amount][col] == "--":  # 2 square pawn advance
                    moves.append(Move((row, col), (row + 2 * move_amount, col), self.board))
        if col - 1 >= 0:  # capture to the left
            if not piece_pinned or pin_direction == (move_amount, -1):
                if self.board[row + move_amount][col - 1][0] == enemy_color:
                    moves.append(Move((row, col), (row + move_amount, col - 1), self.board))
                if (row + move_amount, col - 1) == self.empassantPossible:
                    attacking_piece = blocking_piece = False
                    if king_row == row:
                        if king_col < col:  # king is left of the pawn
                            # inside: between king and the pawn;
                            # outside: between pawn and border;
                            inside_range = range(king_col + 1, col - 1)
                            outside_range = range(col + 1, 8)
                        else:  # king right of the pawn
                            inside_range = range(king_col - 1, col, -1)
                            outside_range = range(col - 2, -1, -1)
                        for i in inside_range:
                            if self.board[row][i] != "--":  # some piece beside en-passant pawn blocks
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[row][i]
                            if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((row, col), (row + move_amount, col - 1), self.board, empassantMove=True))
        if col + 1 <= 7:  # capture to the right
            if not piece_pinned or pin_direction == (move_amount, +1):
                if self.board[row + move_amount][col + 1][0] == enemy_color:
                    moves.append(Move((row, col), (row + move_amount, col + 1), self.board))
                if (row + move_amount, col + 1) == self.empassantPossible:
                    attacking_piece = blocking_piece = False
                    if king_row == row:
                        if king_col < col:  # king is left of the pawn
                            # inside: between king and the pawn;
                            # outside: between pawn and border;
                            inside_range = range(king_col + 1, col)
                            outside_range = range(col + 2, 8)
                        else:  # king right of the pawn
                            inside_range = range(king_col - 1, col + 1, -1)
                            outside_range = range(col - 1, -1, -1)
                        for i in inside_range:
                            if self.board[row][i] != "--":  # some piece beside en-passant pawn blocks
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[row][i]
                            if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((row, col), (row + move_amount, col + 1), self.board, empassantMove=True))

    def getRockMoves(self, row, col, moves):
        piecePinned = False
        pinDirections = ()
        for i in range(len(self.pin) - 1, -1, -1):
            if self.pin[i][0] == row and self.pin[i][1] == col:
                piecePinned = True
                pinDirections = (self.pin[i][2], self.pin[i][3])
                if self.board[row][col][1] != 'Q':
                    self.pin.remove(self.pin[i])
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        negativeColor = 'b' if self.whiteToMove else 'w'
        for direction in directions:
            for i in range(1, 8):
                endRow = row + direction[0] * i
                endCol = col + direction[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    if not piecePinned or pinDirections == direction or pinDirections == (-direction[0], -direction[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--':
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                        elif endPiece[0] == negativeColor:
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    def getKnightMoves(self, row, col, moves):
        piecePinned = False
        for i in range(len(self.pin) - 1, -1, -1):
            if self.pin[i][0] == row and self.pin[i][1] == col:
                piecePinned = True
                self.pin.remove(self.pin[i])
                break
        directions = ((-1, -2), (-1, 2), (-2, -1), (-2, 1), (1, 2), (1, -2), (2, 1), (2, -1))
        color = 'w' if self.whiteToMove else 'b'
        for direction in directions:
            endRow = row + direction[0]
            endCol = col + direction[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != color:
                        moves.append(Move((row, col), (endRow, endCol), self.board))
            # else:
            #     break

    def getBishopMoves(self, row, col, moves):
        piecePinned = False
        pinDirections = ()
        for i in range(len(self.pin) - 1, -1, -1):
            if self.pin[i][0] == row and self.pin[i][1] == col:
                piecePinned = True
                pinDirections = (self.pin[i][2], self.pin[i][3])
                self.pin.remove(self.pin[i])
                break
        directions = ((-1, 1), (1, -1), (1, 1), (-1, -1))
        negativeColor = 'b' if self.whiteToMove else 'w'
        for direction in directions:
            for i in range(1, 8):
                endRow = row + direction[0] * i
                endCol = col + direction[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    if not piecePinned or pinDirections == direction or pinDirections == (-direction[0], -direction[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == '--':
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                        elif endPiece[0] == negativeColor:
                            moves.append(Move((row, col), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break

    def getQueenMoves(self, row, col, moves):
        self.getRockMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)
        # directions = ((-1, 1), (1, -1), (1, 1), (-1, -1), (-1, 0), (1, 0), (0, -1), (0, 1))
        # negativeColor = 'b' if self.whiteToMove else 'w'
        # for direction in directions:
        #     for i in range(1, 8):
        #         endRow = row + direction[0] * i
        #         endCol = col + direction[1] * i
        #         if 0 <= endRow <= 7 and 0 <= endCol <= 7:
        #             endPiece = self.board[endRow][endCol]
        #             if endPiece == '--':
        #                 moves.append(Move((row, col), (endRow, endCol), self.board))
        #             elif endPiece[0] == negativeColor:
        #                 moves.append(Move((row, col), (endRow, endCol), self.board))
        #                 break
        #             else:
        #                 break
        #         else:
        #             break

    def getKingMoves(self, row, col, moves):
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = "w" if self.whiteToMove else "b"
        for i in range(8):
            end_row = row + row_moves[i]
            end_col = col + col_moves[i]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    if ally_color == "w":
                        self.whiteKingLocation = (end_row, end_col)
                    else:
                        self.blackKingLocation = (end_row, end_col)
                    in_check, pins, checks = self.checkForPinsAndCheck()
                    if not in_check:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    if ally_color == "w":
                        self.whiteKingLocation = (row, col)
                    else:
                        self.blackKingLocation = (row, col)

    def getCastleMoves(self, row, col, moves):
        # if self.inCheck:
        if self.squareUnderAttack(row, col):
            return  # cant castle
        if (self.whiteToMove and self.currentCastlingRight.wks) or (
                not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(row, col, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (
                not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(row, col, moves)

    def getKingsideCastleMoves(self, row, col, moves):
        if self.board[row][col + 1] == '--' and self.board[row][col + 2] == '--':
            if not self.squareUnderAttack(row, col + 1) and not self.squareUnderAttack(row, col + 2):
                moves.append(Move((row, col), (row, col + 2), self.board, isCaslteMove=True))

    def getQueensideCastleMoves(self, row, col, moves):
        if self.board[row][col - 1] == '--' and self.board[row][col - 2] == '--' and self.board[row][col - 3] == '--':
            if not self.squareUnderAttack(row, col - 1) and not self.squareUnderAttack(row, col - 2):
                moves.append(Move((row, col), (row, col - 2), self.board, isCaslteMove=True))


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, empassantMove=False, isCaslteMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (
                    self.pieceMoved == 'bp' and self.endRow == 7)

        self.isEmPassantMove = empassantMove

        if self.isEmPassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'

        self.isCastleMove = isCaslteMove

        self.moveId = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveId == other.moveId
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, row, col):
        return self.colToFiles[col] + self.rowToRanks[row]
