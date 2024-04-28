import os
import copy

def clear_console():
    os.system('cls' if os.name=='nt' else 'clear')

def print_board(board):
    cell_width = 9
    # Define the horizontal separator
    horizontal_separator = ("+"+("-"*cell_width)) * len(board[0]) + "+"

    # Print the top border
    print(horizontal_separator)

    # Print each row
    for row in board:
        line = "|"
        for col in row:
            if len(col.units) > 0:
                unit = col.units[0]
                line += f"({unit.player})"
            else:
                line += ("   ")
            control_player, control_value = col.get_control()
            if col.type == "mountain" or col.type == "lake":
                line += f"   "
            else:
                line += f"{control_player}:{control_value}"
            if len(col.units) > 1:
                unit = col.units[1]
                line += f"({unit.player})"
            else:
                line += ("   ")
            line += "|"
        print(line)
        line = "|"
        for col in row:
            new_line = ""
            # Check if the current cell is the middle cell for the "mountain"
            if col.type == "mountain":
                cell_content = "    ^    "
            elif col.type == "forest":
                cell_content = "   ) (   "
            elif col.type == "lake":
                cell_content = "   ~~~   "
            elif col.type == "plain":
                if col.city:
                    cell_content = f"   [{col.city}]   "
                else:
                    cell_content = " " * cell_width

            new_line += cell_content + "|"
            line += new_line
        print(line)
        line = "|"
        for col in row:
            if len(col.units) == 3:
                unit = col.units[2]
                line += f"({unit.player})      " + "|"
            elif len(col.units) > 3:
                unit_1 = col.units[2]
                unit_2 = col.units[3]
                line += f"({unit_1.player})   ({unit_2.player})" + "|"
            else:
                line += (" " * cell_width) + "|"
        print(line)
        # Print the horizontal separator after each row
        print(horizontal_separator)

def print_player_view(board, player):
    if player == 1:
        other_player = 2
    else:
        other_player = 1
    board_copy = copy.deepcopy(board)
    #clear other player city and units from board
    for row in board_copy:
        for cell in row:
            if cell.city == other_player:
                cell.city = None
            for unit in cell.units:
                if unit.player == other_player:
                    cell.units.remove(unit)
    if player == 2:
        #mirror the board
        for row in board_copy:
            row.reverse()
        board_copy.reverse()
    print_board(board_copy)

def add_unit(board, unit, row, column):
    cell = board[row][column]
    cell.units.append(unit)
    if unit.player == 1:
        cell.player_1_control += unit.control
    else:
        cell.player_2_control += unit.control
    # also apply control to immediately adjacent cells
    if row > 0:
        cell = board[row-1][column]
        if unit.player == 1:
            cell.player_1_control += unit.control
        else:
            cell.player_2_control += unit.control
    if row < len(board) - 1:
        cell = board[row+1][column]
        if unit.player == 1:
            cell.player_1_control += unit.control
        else:
            cell.player_2_control += unit.control
    if column > 0:
        cell = board[row][column-1]
        if unit.player == 1:
            cell.player_1_control += unit.control
        else:
            cell.player_2_control += unit.control
    if column < len(board[0]) - 1:
        cell = board[row][column+1]
        if unit.player == 1:
            cell.player_1_control += unit.control
        else:
            cell.player_2_control += unit.control

class Cell():
    def __init__(self):
        self.type = "plain"
        self.city = None
        self.units = []
        self.player_1_control = 0
        self.player_2_control = 0
        self.player_1_visibility = 0
        self.player_2_visibility = 0
    
    def get_control(self):
        if self.player_1_control > self.player_2_control:
            return 1, self.player_1_control - self.player_2_control
        elif self.player_2_control > self.player_1_control:
            return 2, self.player_2_control - self.player_1_control
        else:
            return 0, 0

class Unit():
    movement = 1
    control = 1
    vision = 1
    def __init__(self, player):
        self.player = player

board = [[Cell() for _ in range(9)] for _ in range(9)]
board[4][4].type = "mountain"
board[2][2].type = "forest"
board[6][6].type = "forest"
board[2][6].type = "lake"
board[6][2].type = "lake"

# set player 1 visibility = 1 for bottom 3 rows
for row in board[6:]:
    for cell in row:
        cell.player_1_visibility = 1

# set player 2 visibility = 1 for top 3 rows
for row in board[:3]:
    for cell in row:
        cell.player_2_visibility = 1

def place_cities(board):
    # Call the function with the board
    print_board(board)
    player_1_city = input("Player 1, enter city coordinates in format row, column: ")
    p1_city_row = int(player_1_city.split(",")[0])
    p1_city_column = int(player_1_city.split(",")[1])
    if p1_city_row < 6 or p1_city_row > 8 or p1_city_column < 0 or p1_city_column > 8:
        print("Invalid city placement, city should be built on the last 3 rows. Exiting...")
        raise SystemExit

    cell = board[p1_city_row][p1_city_column]
    if cell.type != "plain":
        print("Invalid coordinates, city should be built on a plain. Exiting...")
        raise SystemExit

    cell.city = 1
    clear_console()
    #print_master_view(board)
    print_player_view(board, 2)
    player_2_city = input("Player 2, enter city coordinates in format row, column: ")
    p1_city_row = int(player_2_city.split(",")[0])
    p1_city_column = int(player_2_city.split(",")[1])
    if p1_city_row < 6 or p1_city_row > 8 or p1_city_column < 0 or p1_city_column > 8:
        print("Invalid city placement, city should be built on the last 3 rows. Exiting...")
        raise SystemExit

    # mirror player 2 city coordinates
    p1_city_row = 8 - p1_city_row
    p1_city_column = 8 - p1_city_column
    cell = board[p1_city_row][p1_city_column]
    if cell.type != "plain":
        print("Invalid coordinates, city should be built on a plain. Exiting...")
        raise SystemExit

    cell.city = 2

# place test cities
board[6][4].city = 1
board[2][4].city = 2

print_player_view(board, 1)
# get player 1 input to place 7 units
for i in range(7):
    player_1_unit = input(f"Player 1, enter unit coordinates for {i} in format row, column: ")
    p1_unit_row = int(player_1_unit.split(",")[0])
    p1_unit_column = int(player_1_unit.split(",")[1])
    if p1_unit_row < 0 or p1_unit_row > 8 or p1_unit_column < 0 or p1_unit_column > 8:
        print("Invalid unit placement, unit should be built on the grid. Exiting...")
        raise SystemExit

    cell = board[p1_unit_row][p1_unit_column]
    if cell.type == "lake":
        print("Invalid coordinates, unit cannot be placed on lake. Exiting...")
        raise SystemExit

    add_unit(board, Unit(1), p1_unit_row, p1_unit_column)
    clear_console()
    print_player_view(board, 1)