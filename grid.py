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
        for cell in row:
            if cell.visible:
                if len(cell.units) > 0:
                    unit = cell.units[0]
                    line += f"({unit.player})"
                else:
                    line += ("   ")
                control_player, control_value = cell.get_control()
                if cell.type == "mountain" or cell.type == "lake":
                    line += f"   "
                else:
                    line += f"{control_player}:{control_value}"
                if len(cell.units) > 1:
                    unit = cell.units[1]
                    line += f"({unit.player})"
                else:
                    line += ("   ")
                line += "|"
            else:
                line += " " * cell_width + "|"
        print(line)
        line = "|"
        for cell in row:
            new_line = ""
            # Check if the current cell is the middle cell for the "mountain"
            if cell.type == "mountain":
                cell_content = "    ^    "
            elif cell.type == "forest":
                cell_content = "   ) (   "
            elif cell.type == "lake":
                cell_content = "   ~~~   "
            elif cell.type == "plain":
                if cell.visible and cell.city:
                    cell_content = f"   [{cell.city}]   "
                else:
                    cell_content = " " * cell_width

            new_line += cell_content + "|"
            line += new_line
        print(line)
        line = "|"
        for cell in row:
            if cell.visible:
                if len(cell.units) == 3:
                    unit = cell.units[2]
                    line += f"({unit.player})      " + "|"
                elif len(cell.units) > 3:
                    unit_1 = cell.units[2]
                    unit_2 = cell.units[3]
                    line += f"({unit_1.player})   ({unit_2.player})" + "|"
                else:
                    line += (" " * cell_width) + "|"
            else:
                line += " " * cell_width + "|"
        print(line)
        # Print the horizontal separator after each row
        print(horizontal_separator)

def print_player_view(board, player):
    if player == 1:
        other_player = 2
    else:
        other_player = 1
    board_copy = copy.deepcopy(board)
    #check visibility
    for row in board_copy:
        for cell in row:
            if player == 1:
                if not cell.player_1_visibility:
                    cell.visible = False
            elif player == 2:
                if not cell.player_2_visibility:
                    cell.visible = False
    if player == 2:
        #mirror the board
        for row in board_copy:
            row.reverse()
        board_copy.reverse()
        # flip all player related values
        for row in board_copy:
            for cell in row:
                cell.player_1_control, cell.player_2_control = cell.player_2_control, cell.player_1_control
                cell.player_1_visibility, cell.player_2_visibility = cell.player_2_visibility, cell.player_1_visibility
                for unit in cell.units:
                    if unit.player == 1:
                        unit.player = 2
                    else:
                        unit.player = 1
                if cell.city:
                    if cell.city == 1:
                        cell.city = 2
                    else:
                        cell.city = 1

    print_board(board_copy)

def add_unit(board, unit, row, column):
    cell = board[row][column]
    if cell.type == "lake":
        print("Invalid coordinates, unit cannot be placed on lake. Exiting...")
        raise SystemExit
    cell.units.append(unit)
    if unit.player == 1:
        cell.player_1_control += unit.control
        cell.player_1_visibility = True
    else:
        cell.player_2_control += unit.control
        cell.player_2_visibility = True
    # also apply control to immediately adjacent cells
    if row > 0:
        cell = board[row-1][column]
        if unit.player == 1:
            cell.player_1_control += unit.control
            cell.player_1_visibility = True
        else:
            cell.player_2_control += unit.control
            cell.player_2_visibility = True
    if row < len(board) - 1:
        cell = board[row+1][column]
        if unit.player == 1:
            cell.player_1_control += unit.control
            cell.player_1_visibility = True
        else:
            cell.player_2_control += unit.control
            cell.player_2_visibility = True
    if column > 0:
        cell = board[row][column-1]
        if unit.player == 1:
            cell.player_1_control += unit.control
            cell.player_1_visibility = True
        else:
            cell.player_2_control += unit.control
            cell.player_2_visibility = True
    if column < len(board[0]) - 1:
        cell = board[row][column+1]
        if unit.player == 1:
            cell.player_1_control += unit.control
            cell.player_1_visibility = True
        else:
            cell.player_2_control += unit.control
            cell.player_2_visibility = True

class Cell():
    def __init__(self):
        self.type = "plain"
        self.city = None
        self.units = []
        self.player_1_control = 0
        self.player_2_control = 0
        self.player_1_visibility = False
        self.player_2_visibility = False
        self.visible = True

    
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
    p2_city_row = int(player_2_city.split(",")[0])
    p2_city_column = int(player_2_city.split(",")[1])
    if p2_city_row < 6 or p2_city_row > 8 or p2_city_column < 0 or p2_city_column > 8:
        print("Invalid city placement, city should be built on the last 3 rows. Exiting...")
        raise SystemExit

    # mirror player 2 city coordinates
    p2_city_row = 8 - p2_city_row
    p2_city_column = 8 - p2_city_column
    cell = board[p2_city_row][p2_city_column]
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
    while True:
        player_1_unit = input(f"Player 1, enter unit coordinates for {i} in format row, column: ")
        p1_unit_row = int(player_1_unit.split(",")[0])
        p1_unit_column = int(player_1_unit.split(",")[1])
        if p1_unit_row < 6 or p1_unit_row > 8 or p1_unit_column < 0 or p1_unit_column > 8:
            print("Invalid unit placement, unit should be built on the grid.")
            continue
        try:
            add_unit(board, Unit(1), p1_unit_row, p1_unit_column)
        except:
            continue
        clear_console()
        print_player_view(board, 1)
        break
clear_console()
print_player_view(board, 2)
for i in range(7):
    while True:
        player_2_unit = input(f"Player 2, enter unit coordinates for {i} in format row, column: ")
        p2_unit_row = int(player_2_unit.split(",")[0])
        p2_unit_column = int(player_2_unit.split(",")[1])
        if p2_unit_row < 6 or p2_unit_row > 8 or p2_unit_column < 0 or p2_unit_column > 8:
            print("Invalid unit placement, unit should be built on the grid.")
            continue
        
        p2_unit_row = 8 - p2_unit_row
        p2_unit_column = 8 - p2_unit_column
        try:
            add_unit(board, Unit(2), p2_unit_row, p2_unit_column)
        except:
            continue
        clear_console()
        print_player_view(board, 2)
        break
print_board(board)