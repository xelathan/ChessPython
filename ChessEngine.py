"""
store info about current game state of the chess game
also determines the valid moves at the current state. Keeps a move log
"""


class GameState():
    def __init__(self):
        # Board is an 8x8 2D list - each element has 2 chars
        # 1st char represents the color(black, white) and the 2nd char represents the type: Q, K, B, N, R, p
        # -- is an empty space
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
        self.whiteToMove = True
        self.moveLog = []
        self.moveFunctions = {"p": self.getPawnMoves, "R": self.getRookMoves, "N": self.getKnightMoves,
                              "B": self.getBishopMoves, "Q": self.getQueenMoves, "K": self.getKingMoves}
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)  # log the move so we can undo it if we want
        # update king's location if moved
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        self.whiteToMove = not self.whiteToMove  # swap players

    def undoMove(self):
        if len(self.moveLog) > 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            # update king's location if moved
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.endRow, move.endCol)
            elif move.pieceMoved == "bK":
                self.whiteKingLocation = (move.endRow, move.endCol)
            self.whiteToMove = not self.whiteToMove  # switch turns back

    """
    All moves considering checks
    """

    def getValidMoves(self):
        # 1. Generate all possilbe moves
        moves = self.getAllPossibleMoves()
        # 2. for each move make the move
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            # 3. generate all opponents move
            # 4. for each of the opponents move see if they attack your king
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                # 5. if they do attack your king it's not a valid move
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

            if len(moves) == 0:
                if self.inCheck():
                    self.checkMate = True
                else:
                    self.staleMate = True
            else:
                self.checkMate = False
                self.staleMate = False
        return moves

    """
    Determine if the current player is in check
    """
    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    """
    Determine if the enemy can attack the square r, c
    """
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove  # switch turns to opponent
        oppMoves = self.getAllPossibleMoves()  # get opponent moves
        self.whiteToMove = not self.whiteToMove  # switch back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:  # square is under attack
                return True
        return False
        pass

    """
    All moves without considering checks
    """

    def getAllPossibleMoves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    pieceType = self.board[row][col][1]
                    self.moveFunctions[pieceType](row, col,
                                                  moves)  # calls the appropriate move function based on piece type

        return moves

    """
    Get all pawn moves at the row and col and add these to the list
    """

    def getPawnMoves(self, row, col, moves):
        if self.whiteToMove:  # when a white pawn moves
            if self.board[row - 1][col] == "--":  # 1 square pawn advance
                moves.append(Move((row, col), (row - 1, col), self.board))
                if row == 6 and self.board[row - 2][col] == "--":  # 2 square pawn advance
                    moves.append(Move((row, col), (row - 2, col), self.board))
            if col - 1 >= 0:  # pawn captures diagonally left
                if self.board[row - 1][col - 1][0] == "b":
                    moves.append(Move((row, col), (row - 1, col - 1), self.board))
            if col + 1 <= 7:  # pawn captures diagonally right
                if self.board[row - 1][col + 1][0] == "b":
                    moves.append(Move((row, col), (row - 1, col + 1), self.board))
        else:
            if self.board[row + 1][col] == "--":
                moves.append(Move((row, col), (row + 1, col), self.board))
                if row == 1 and self.board[row + 2][col] == "--":
                    moves.append(Move((row, col), (row + 2, col), self.board))
            if col - 1 >= 0:
                if self.board[row + 1][col - 1][0] == "w":  # pawn captures diagonally left
                    moves.append(Move((row, col), (row + 1, col - 1), self.board))
            if col + 1 <= 7:
                if self.board[row + 1][col + 1][0] == "w":
                    moves.append(Move((row, col), (row + 1, col + 1), self.board))

    def getRookMoves(self, row, col, moves):
        enemyColor = "b" if self.whiteToMove else "w"
        if row > 0:  # Check backwards
            for r in reversed((range(0, row))):
                if self.board[r][col] == "--":
                    moves.append(Move((row, col), (r, col), self.board))
                elif self.board[r][col][0] == enemyColor:
                    moves.append(Move((row, col), (r, col), self.board))
                    break
                else:
                    break
        if row < 7:  # Check forwards
            for r in range(row + 1, len(self.board)):
                if self.board[r][col] == "--":
                    moves.append(Move((row, col), (r, col), self.board))
                elif self.board[r][col][0] == enemyColor:
                    moves.append(Move((row, col), (r, col), self.board))
                    break
                else:
                    break
        if col > 0:  # Check left
            for c in reversed((range(0, col))):
                if self.board[row][c] == "--":
                    moves.append(Move((row, col), (row, c), self.board))
                elif self.board[row][c][0] == enemyColor:
                    moves.append(Move((row, col), (row, c), self.board))
                    break
                else:
                    break
        if col < 7:  # Check Right
            for c in range(col + 1, len(self.board)):
                if self.board[row][c] == "--":
                    moves.append(Move((row, col), (row, c), self.board))
                elif self.board[row][c][0] == enemyColor:
                    moves.append(Move((row, col), (row, c), self.board))
                    break
                else:
                    break

    def getKnightMoves(self, row, col, moves):
        enemyColor = "b" if self.whiteToMove else "w"
        if col > 0:
            if row < 6:  # backwards left long l
                if self.board[row + 2][col - 1] == "--" or self.board[row + 2][col - 1][0] == enemyColor:
                    moves.append(Move((row, col), (row + 2, col - 1), self.board))
            if row > 1:  # forwards left long l
                if self.board[row - 2][col - 1] == "--" or self.board[row - 2][col - 1][0] == enemyColor:
                    moves.append(Move((row, col), (row - 2, col - 1), self.board))
        if col < 7:
            if row < 6:  # backwards right long l
                if self.board[row + 2][col + 1] == "--" or self.board[row + 2][col + 1][0] == enemyColor:
                    moves.append(Move((row, col), (row + 2, col + 1), self.board))
            if row > 1:  # forwards right long l
                if self.board[row - 2][col + 1] == "--" or self.board[row - 2][col + 1][0] == enemyColor:
                    moves.append(Move((row, col), (row - 2, col + 1), self.board))
        if col > 1:
            if row > 0:  # forwards left horizontal l
                if self.board[row - 1][col - 2] == "--" or self.board[row - 1][col - 2][0] == enemyColor:
                    moves.append(Move((row, col), (row - 1, col - 2), self.board))
            if row < 7:  # backwards left horizontal l
                if self.board[row + 1][col - 2] == "--" or self.board[row + 1][col - 2][0] == enemyColor:
                    moves.append(Move((row, col), (row + 1, col - 2), self.board))
        if col < 6:
            if row > 0:
                if self.board[row - 1][col + 2] == "--" or self.board[row - 1][col + 2][0] == enemyColor:
                    moves.append(Move((row, col), (row - 1, col + 2), self.board))
            if row < 7:
                if self.board[row + 1][col + 2] == "--" or self.board[row + 1][col + 2][0] == enemyColor:
                    moves.append(Move((row, col), (row + 1, col + 2), self.board))
        pass

    def getBishopMoves(self, row, col, moves):
        enemyColor = "b" if self.whiteToMove else "w"
        if row > 0:
            if col > 0:
                try:
                    for r in reversed(range(0, row)):
                        for c in reversed(range(0, col)):
                            if abs(row - r) == abs(col - c):
                                if self.board[r][c] == "--":
                                    moves.append(Move((row, col), (r, c), self.board))
                                elif self.board[r][c][0] == enemyColor:
                                    moves.append(Move((row, col), (r, c), self.board))
                                    raise StopIteration
                                else:
                                    raise StopIteration
                except StopIteration:
                    pass
            if col < 7:
                try:
                    for r in reversed(range(0, row)):
                        for c in range(col + 1, len(self.board[0])):
                            if abs(row - r) == abs(col - c):
                                if self.board[r][c] == "--":
                                    moves.append(Move((row, col), (r, c), self.board))
                                elif self.board[r][c][0] == enemyColor:
                                    moves.append(Move((row, col), (r, c), self.board))
                                    raise StopIteration
                                else:
                                    raise StopIteration
                except StopIteration:
                    pass

        if row < 7:
            if col > 0:
                try:
                    for r in range(row + 1, len(self.board)):
                        for c in reversed(range(0, col)):
                            if abs(row - r) == abs(col - c):
                                if self.board[r][c] == "--":
                                    moves.append(Move((row, col), (r, c), self.board))
                                elif self.board[r][c][0] == enemyColor:
                                    moves.append(Move((row, col), (r, c), self.board))
                                    raise StopIteration
                                else:
                                    raise StopIteration
                except StopIteration:
                    pass
            if col < 7:
                try:
                    for r in range(row + 1, len(self.board)):
                        for c in range(col + 1, len(self.board[0])):
                            if abs(row - r) == abs(col - c):
                                if self.board[r][c] == "--":
                                    moves.append(Move((row, col), (r, c), self.board))
                                elif self.board[r][c][0] == enemyColor:
                                    moves.append(Move((row, col), (r, c), self.board))
                                    raise StopIteration
                                else:
                                    raise StopIteration
                except StopIteration:
                    pass


        pass

    def getQueenMoves(self, row, col, moves):
        self.getRookMoves(row, col, moves)
        self.getBishopMoves(row, col , moves)
        pass

    def getKingMoves(self, row, col, moves):
        enemyColor = "b" if self.whiteToMove else "w"
        if col > 0:
            if self.board[row][col - 1] == "--" or self.board[row][col - 1][0] == enemyColor:
                moves.append(Move((row, col), (row, col - 1), self.board))
            if row > 0:
                if self.board[row - 1][col - 1] == "--" or self.board[row - 1][col - 1][0] == enemyColor:
                    moves.append(Move((row, col), (row - 1, col - 1), self.board))
            if row < 7:
                if self.board[row + 1][col - 1] == "--" or self.board[row + 1][col - 1][0] == enemyColor:
                    moves.append(Move((row, col), (row + 1, col - 1), self.board))
        if row > 0:
            if self.board[row - 1][col] == "--" or self.board[row - 1][col][0] == enemyColor:
                moves.append(Move((row, col), (row - 1, col), self.board))
        if row < 7:
            if self.board[row + 1][col] == "--" or self.board[row + 1][col][0] == enemyColor:
                moves.append(Move((row, col), (row + 1, col), self.board))
        if col < 7:
            if self.board[row][col + 1] == "--" or self.board[row][col + 1][0] == enemyColor:
                moves.append(Move((row, col), (row, col + 1), self.board))
            if row < 7:
                if self.board[row + 1][col + 1] == "--" or self.board[row + 1][col + 1][0] == enemyColor:
                    moves.append(Move((row, col), (row + 1, col + 1), self.board))
            if row > 0:
                if self.board[row - 1][col + 1] == "--" or self.board[row - 1][col + 1][0] == enemyColor:
                    moves.append(Move((row, col), (row - 1, col + 1), self.board))


class Move():
    # maps keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    """
    Override equals method
    """

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]
