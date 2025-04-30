"""
This class is responsible for storing all the information about the current State Of a chess game.
It will also be responsble for determineing the valid moves at the current state.
It will also keep a move Log.
"""


class GameState:
    def __init__(self):
        # Board is an 8*8 2d list, each element of the list has 2 characters.
        # The first character represents the color of the piece, 'b' or 'w'
        # The first character represents the type of the piece, 'K', 'Q', 'R', 'B', 'N' or 'P'
        # "  " represents an empty space with no piece.
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
            ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
            ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
            ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.moveFunctions = {
            "P": self.getPawnMoves,
            "R": self.getRookMoves,
            "N": self.getKnightMoves,
            "B": self.getBishopMoves,
            "Q": self.getQueenMoves,
            "K": self.getKingMoves,
        }
        self.WhiteToMove = True
        self.moveHistory = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.enpassantPossible = ()  # Coordinates for the square where en passant capture is possible

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "  "
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveHistory.append(move)
        self.WhiteToMove = not self.WhiteToMove  # Swap players
        # Update the king's location if moved
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        # Pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

        # Enpassant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "  "  # Capturing the pawn

        # Update enpassantPossible variable
        if (
            move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2
        ):  # Only on 2 square pawn advances
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

    """
    Undo the last move made
    """

    def undoMove(self):
        if len(self.moveHistory) != 0:  # بنتأكد اننااتحركنا عشان اما نرجع
            move = self.moveHistory.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.WhiteToMove = not self.WhiteToMove  # Switch turns back

            # Update the king's possition if needed
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            # undo en passant move
            if move.isEnpassantMove:
                self.board[move.endRow][
                    move.endCol
                ] = "  "  # leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            # undo 2 square pawn advance
            if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()

    """
    الحركات اما يكون مثلا الملك في حالة (كــش ملك)  
    """

    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        # (1) Generate all possible moves
        moves = self.getAllPossibleMoves()
        # (2) for each move, make the move
        for i in range(len(moves) - 1, -1, -1):  # When removing from list go backwords
            self.makeMove(moves[i])
            # (3) generate all opponent's moves
            # (4) for each of your opponent's moves, see if they attack your king
            self.WhiteToMove = not self.WhiteToMove
            if self.inCheck():
                moves.remove(
                    moves[i]
                )  # (5) if they do attack your king, not a valid move
            self.WhiteToMove = not self.WhiteToMove
            self.undoMove()
        if len(moves) == 0:  # either checkmate or stalemate
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.enpassantPossible = tempEnpassantPossible
        return moves

    """
    Determine if the current player is in check
    """

    def inCheck(self):
        if self.WhiteToMove:
            return self.squareUnderAttack(
                self.whiteKingLocation[0], self.whiteKingLocation[1]
            )
        else:
            return self.squareUnderAttack(
                self.blackKingLocation[0], self.blackKingLocation[1]
            )

    """
    Determine if the enemy can attack the square r, c 
    """

    def squareUnderAttack(self, r, c):
        self.WhiteToMove = not self.WhiteToMove  # switch to ipponent's turn
        oppMoves = self.getAllPossibleMoves()
        self.WhiteToMove = not self.WhiteToMove  # Switch turns back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:  # Square is under attack
                return True
        return False

    """
    الحركات دون مراعاة (كــش ملك)
    """

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):  # Number of rows
            for c in range(len(self.board[r])):  # Number of columns in given rows
                turn = self.board[r][c][0]
                if (turn == "w" and self.WhiteToMove) or (
                    turn == "b" and not self.WhiteToMove
                ):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](
                        r, c, moves
                    )  # calls the appropriate move function based on piece type
        return moves

    """
    Get all the "pawn" moves for the "pawn" located at row, column and add these moves to the list
    """

    def getPawnMoves(self, r, c, moves):
        if self.WhiteToMove:  # white Pawn moves
            if self.board[r - 1][c] == "  ":  # 1 square pawn advance
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "  ":  # 2 square pawn advance
                    moves.append(Move((r, c), (r - 2, c), self.board))

            if c - 1 >= 0:  # Capture to the left
                if self.board[r - 1][c - 1][0] == "b":  # enemy piece to capture
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enpassantPossible:
                    moves.append(
                        Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove=True)
                    )

            if c + 1 <= 7:  # capture to the right
                if self.board[r - 1][c + 1][0] == "b":  # enemy piece to capture
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassantPossible:
                    moves.append(
                        Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove=True)
                    )

        else:  # Black pawn moves
            if self.board[r + 1][c] == "  ":  # 1 square move
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "  ":  # 2 square pawn advance
                    moves.append(Move((r, c), (r + 2, c), self.board))
            # capture
            if c - 1 >= 0:  # Capture to the left
                if self.board[r + 1][c - 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.enpassantPossible:
                    moves.append(
                        Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove=True)
                    )

            if c + 1 <= 7:  # Capture to the right
                if self.board[r + 1][c + 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.enpassantPossible:
                    moves.append(
                        Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove=True)
                    )

        # Add pawn promotions latter

    """
    Get all the "Rook" moves for the "Rook" located at row, column and add these moves to the list
    """

    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))  # Up, Left, Down, Right
        enemyColor = "b" if self.WhiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # On board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "  ":  #
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # Empty space valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # Friendly piece invalid
                        break
                else:  # Off board
                    break

    """
        Get all the "Knight" moves for the "Knight" located at row, column and add these moves to the list
    """

    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.WhiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # Not an ally piece (empty or enmy piece)
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    """
        Get all the "Bishop" moves for the "Bishop" located at row, column and add these moves to the list
    """

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # اربع اتجاهات
        enemyColor = "b" if self.WhiteToMove else "w"
        for d in directions:
            for i in range(1, 8):  # Bishop can move max of 7 squares
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  # بتشيك لو موجود علي البورد
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "  ":  #
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # Empty space valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:  # Friendly piece invalid
                        break
                else:  # Off board
                    break

    """
        Get all the "Queen" moves for the "Queen" located at row, column and add these moves to the list
    """

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    """
        Get all the "Knight" moves for the "Knight" located at row, column and add these moves to the list
    """

    def getKingMoves(self, r, c, moves):
        kingmoves = (
            (-1, -1),
            (-1, 0),
            (-1, 1),
            (0, -1),
            (0, 1),
            (1, -1),
            (1, 0),
            (1, 1),
        )
        allyColor = "w" if self.WhiteToMove else "b"
        for i in range(8):
            endRow = r + kingmoves[i][0]
            endCol = c + kingmoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # Not an ally piece (empty or enmy piece)
                    moves.append(Move((r, c), (endRow, endCol), self.board))


class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # Pawn promotion
        self.isPawnPromotion = (self.pieceMoved == "wP" and self.endRow == 0) or (
            self.pieceMoved == "bP" and self.endRow == 7
        )
        # En passant -> حركة خاصة لأكل البيدق في الشطرنج
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "wP" if self.pieceMoved == "bP" else "bP"

        self.moveID = (
            self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
        )

    """
    Overriding the equals method 
    """

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(
            self.endRow, self.endCol
        )

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
