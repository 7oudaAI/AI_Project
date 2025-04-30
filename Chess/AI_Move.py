from Chess.engine import GameState, Move

"""
دي الدالة اللي بتقيم حالة اللوحة دلوقتي
لو النتيجة موجبة يبقى الأبيض في وضع أحسن
لو النتيجة سالبة يبقى الأسود في وضع أحسن
"""


def evaluate_board(game_state):

    piece_values = {
        "P": 1,
        "N": 3,
        "B": 3,
        "R": 5,
        "Q": 9,
        "K": 0,
    }

    score = 0

    for row in range(8):
        for col in range(8):
            piece = game_state.board[row][col]
            if piece != "  ":
                value = piece_values[piece[1]]
                if piece[0] == "w":
                    score += value
                else:
                    score -= value

    return score


def alpha_beta_search(game_state, depth, alpha, beta, maximizing_player):

    if depth == 0 or game_state.checkmate or game_state.stalemate:
        return evaluate_board(game_state), None

    valid_moves = game_state.getValidMoves()

    if maximizing_player:
        best_value = float("-inf")
        best_move = None

        for move in valid_moves:
            game_state.makeMove(move)
            value, _ = alpha_beta_search(game_state, depth - 1, alpha, beta, False)
            game_state.undoMove()

            if value > best_value:
                best_value = value
                best_move = move

            alpha = max(alpha, best_value)
            if beta <= alpha:
                break

        return best_value, best_move

    else:
        best_value = float("inf")
        best_move = None
        for move in valid_moves:
            game_state.makeMove(move)
            value, _ = alpha_beta_search(game_state, depth - 1, alpha, beta, True)
            game_state.undoMove()

            if value < best_value:
                best_value = value
                best_move = move

            beta = min(beta, best_value)
            if beta <= alpha:
                break

        return best_value, best_move


"""
دي الدالة اللي بنستدعيها عشان نجيب أحسن حركة

"""


def get_best_move(game_state, depth=3):

    _, best_move = alpha_beta_search(
        game_state,
        depth,
        float("-inf"),
        float("inf"),
        game_state.WhiteToMove,
    )
    return best_move
