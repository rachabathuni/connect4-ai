import connect4
import random

g_file_handle = None
g_records_data_handle = None
MAX_RECORDS = 1000000
MAX_RECORDS_PER_POSITION = int(MAX_RECORDS/41)
records = [0] * 42
DATA_FILE = "data/samples.csv"


def gen_rand_moves():
    board = connect4.Board()
    for n_move in range(0, 41):
        if board.check_win():
            return 0

        if records[n_move] < MAX_RECORDS_PER_POSITION:
            eng = connect4.Connect4Engine(board)
            e, m = eng.get_best_move()
            if e != connect4.SUCCESS:
                print("Failed to get best move (1)")
                return -1
            record_move(board, n_move, m)
            records[n_move] += 1
        
        free_columns = []
        for col in range(0, 7):
            if not board.is_column_full(col):
                free_columns.append(col)
    
        e = board.play(free_columns[random.randint(0, len(free_columns)-1)])
        if e != connect4.SUCCESS:
            print("Failed to play move")
            return -1

    return 0


def write_data_to_file(outstr):
    global g_file_handle
    if not g_file_handle:
        g_file_handle = open(DATA_FILE, "w")

    g_file_handle.write(outstr)
    g_file_handle.write("\n")
    g_file_handle.flush()


def record_move(board, n_moves, best_move):
    # We always want to capture "O" as the next move
    # This way the patterns are conssitent
    if n_moves % 2 == 0:
        comp = 1
    else:
        comp = 2

    outstr = ""
    separator = ""
    for r in range(board.rows):
        for c in range(board.columns):
            if board.board[r][c] == comp:
                outstr = outstr + separator + "1, 0"
            elif board.board[r][c] == 0:
                outstr = outstr + separator + "0, 0"
            else:
                outstr = outstr + separator + "0, 1"
            separator = ", "
    outstr = outstr + f", {best_move}"
    write_data_to_file(outstr)


def check_max_records_reached(recs, max_records):
    for i in recs:
        if i < max_records:
            return False
    return True


# Just for debugging if we have to restart the process
def dump_record_data():
    global g_records_data_handle
    if not g_records_data_handle:
        g_records_data_handle = open("records.txt", "w")

    g_records_data_handle.write("[")
    for r in records:
        g_records_data_handle.write(f"{r}, ")
    g_records_data_handle.write("]\n")


count = 0
while True:
    gen_rand_moves()
    # dump_record_data()
    count += 1
    if count % 100 == 0:
        print(records)

    if check_max_records_reached(records, MAX_RECORDS_PER_POSITION):
        break
