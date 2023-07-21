"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    X_count = 0
    O_count = 0
    for row in board:
        for space in row:
            if space == "X":
                X_count += 1
            elif space == "O":
                O_count += 1
    if X_count == O_count:
        return X
    elif X_count - O_count == 1:
        return O
    else:
        return None


def actions(board):
    moves = []
    for i in range(3):
        for j in range(3):
            if board[i][j] is None:
                moves.append((i, j))
    return moves


def deep_copy(board):
    copy = initial_state()
    for i in range(3):
        for j in range(3):
            copy[i][j] = board[i][j]
    return copy


def result(board, action):
    if board[action[0]][action[1]] is not None:
        raise ValueError
    result_board = deep_copy(board)
    result_board[action[0]][action[1]] = player(board)
    return result_board


def winner(board):
    for x in range(3):
        if board[x][0] is not None and board[x][0] == board[x][1] == board[x][2]:
            return board[x][0]
        elif board[0][x] is not None and board[0][x] == board[1][x] == board[2][x]:
            return board[0][x]
    if board[1][1] is not None:
        if board[0][0] == board[1][1] == board[2][2]:
            return board[0][0]
        elif board[2][0] == board[1][1] == board[0][2]:
            return board[2][0]
    return None


def full_board(board):
    for i in range(3):
        for j in range(3):
            if board[i][j] is None:
                return False
    return True


def terminal(board):
    return winner(board) is not None or full_board(board)


def utility(board):
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    return 0


def min_value(board):
    # if game is over, return game value
    if terminal(board):
        return (utility(board), None)
    # initial value infinity, any game should be smaller
    v = (math.inf, None)
    # iterate through all possible actions with current board,
    # find the action with the smallest maximum value
    for action in actions(board):
        t = max_value(result(board, action))
        if t[0] < v[0]:
            # if max value of current action is smaller than current
            # max value, save max value and action that led to it
            v = (t[0], action)
    # return value, action pair with the smallest max value
    return v


def max_value(board):
    # if game is over, return game value
    if terminal(board):
        return (utility(board), None)
    # initial value negative infinity, any game should be larger
    v = (-math.inf, None)
    # iterate through all possible actions with current board,
    # find the action with the largest minimum value
    for action in actions(board):
        t = min_value(result(board, action))
        if t[0] > v[0]:
            # if min value of current action is larger than current
            # min value, save min value and action that led to it
            v = (t[0], action)
    # return value, action pair with largest min value
    return v


def minimax(board):
    if player(board) == X:
        return max_value(board)[1]
    if player(board) == O:
        return min_value(board)[1]
