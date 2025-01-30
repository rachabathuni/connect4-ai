import sys
import connect4

board = connect4.Board()
board.print_board()
while True:
    player = board.next_player
    if board.is_full():
        print("No more moves")
        sys.exit(0)

    while True:
        print(f"Player: {connect4.PLAYER_TEXT[player]}")
        userin = input("Enter column: ")
        try:
            col = int(userin.strip())
        except ValueError:
            print("Invalid entry")
            continue

        if col < 0 or col > 6:
            print("Invalid column")
            continue

        if board.get_chips_in_column(col) >= 6:
            print("Column full")
            continue
        break

    ret = board.play(col)
    if ret != connect4.SUCCESS:
        print("Failed to make move")
        sys.exit(0)

    ret = board.check_win()
    board.print_board()
    if ret:
        print("User won!")
        sys.exit(0)

    if board.is_full():
        print("No more moves")
        sys.exit(0)

    print("Thinking...")
    eng = connect4.Connect4Engine(board)
    err, move = eng.get_best_move()
    ret = board.play(move)
    if ret != connect4.SUCCESS:
        print("Failed to make move")
        sys.exit(0)

    ret = board.check_win()
    board.print_board()
    if ret:
        print("Computer won!")
        sys.exit(0)
