import os
import copy
from typing import List

class Cell():
    def __init__(self):
        self.type = "plain"
        self.city = None
        self.units = []
        self.visible = True

class Unit():
    movement = 1
    control = 1
    vision = 1
    def __init__(self, player):
        self.player = player

def clear_console():
    os.system('cls' if os.name=='nt' else 'clear')

def print_board(board: List[List[Cell]]):
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
                control_player, control_value = get_cell_control(board, cell)
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
    board_copy = copy.deepcopy(board)
    for row in board_copy:
        for cell in row:
            cell.visible = get_cell_visibility(board, cell, player)
    if player == 2:
        #mirror the board
        for row in board_copy:
            row.reverse()
        board_copy.reverse()
        # flip all player related values
        for row in board_copy:
            for cell in row:
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

def get_cell_position(board: List[List[Cell]], cell: Cell):
    for row_index, row in enumerate(board):
        for column_index, cell in enumerate(row):
            if cell == cell:
                return row_index, column_index
    raise ValueError("Cell not found on board")

def get_adjacent_cells(board: List[List[Cell]], cell: Cell):
    adjacent_cells = []
    row, column = get_cell_position(board, cell)
    if row > 0:
        adjacent_cells.append(board[row-1][column])
    if row < len(board) - 1:
        adjacent_cells.append(board[row+1][column])
    if column > 0:
        adjacent_cells.append(board[row][column-1])
    if column < len(board[0]) - 1:
        adjacent_cells.append(board[row][column+1])
    return adjacent_cells

def get_cell_control(board: List[List[Cell]], cell: Cell) -> tuple[int, int]:
    player_1_control = 0
    player_2_control = 0
    cells_to_check = [cell]
    adjacent_cells = get_adjacent_cells(board, cell)
    cells_to_check.extend(adjacent_cells)
    for cell in cells_to_check:
        for unit in cell.units:
            if unit.player == 1:
                player_1_control += unit.control
            else:
                player_2_control += unit.control
    if player_1_control > player_2_control:
        return 1, player_1_control - player_2_control
    elif player_2_control > player_1_control:
        return 2, player_2_control - player_1_control
    else:
        return 0, 0

def get_cell_visibility(board: List[List[Cell]], cell: Cell, player: int):
    if cell.city == player:
        return True
    for unit in cell.units:
        if unit.player == player:
            return True
    adjacent_cells = get_adjacent_cells(board, cell)
    for adjacent_cell in adjacent_cells:
        for unit in adjacent_cell.units:
            if unit.player == player:
                return True
    return False

def get_player_units(board: List[List[Cell]], player) -> List[Unit]:
    units = []
    for row in board:
        for cell in row:
            for unit in cell.units:
                if unit.player == player:
                    units.append(unit)
    return units

def get_unit_position(board: List[List[Cell]], unit):
    for row_index, row in enumerate(board):
        for column, cell in enumerate(row):
            if unit in cell.units:
                return row_index, column
    return None
            
def get_unit_cell(board: List[List[Cell]], unit: Unit):
    for row in board:
        for cell in row:
            if unit in cell.units:
                return cell
    return None

def add_unit(board: List[List[Cell]], unit: Unit, row: int, column: int):
    cell = board[row][column]
    if cell.type == "lake":
        print("Invalid coordinates, unit cannot be placed on lake. Exiting...")
        raise ValueError("Unit cannot be placed on lake")
    player = unit.player
    player_units = get_player_units(board, player)
    if len(player_units) == 7:
        raise ValueError("Player already has 7 units on the board")
    cell.units.append(unit)

def move_unit(board: List[List[Cell]], unit: Unit, end_row: int, end_column: int):
    starting_cell = get_unit_cell(board, unit)
    if not starting_cell:
        raise ValueError("Unit not found on board")
    starting_cell.units.remove(unit)
    add_unit(board, unit, end_row, end_column)

board = [[Cell() for _ in range(9)] for _ in range(9)]
board[4][4].type = "mountain"
board[2][2].type = "forest"
board[6][6].type = "forest"
board[2][6].type = "lake"
board[6][2].type = "lake"

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

def place_units(board):
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
# place test cities
board[6][4].city = 1
board[2][4].city = 2
# place test units
add_unit(board, Unit(1), 7, 4)
add_unit(board, Unit(1), 7, 5)
add_unit(board, Unit(1), 7, 6)
add_unit(board, Unit(1), 8, 4)
add_unit(board, Unit(1), 8, 5)
add_unit(board, Unit(1), 8, 6)
add_unit(board, Unit(1), 8, 7)
add_unit(board, Unit(2), 1, 4)
add_unit(board, Unit(2), 1, 5)
add_unit(board, Unit(2), 1, 6)
add_unit(board, Unit(2), 0, 4)
add_unit(board, Unit(2), 0, 5)
add_unit(board, Unit(2), 0, 6)
add_unit(board, Unit(2), 0, 7)
print_board(board)
print_player_view(board, 1)
print_player_view(board, 2)
print(get_cell_control(board, board[8][3]))
# while True:
#     clear_console()
#     print_player_view(board, 1)
#     for unit in get_player_units(board, 1):
#         row,column = get_unit_position(board, unit)
#         player_1_move = input(f"Enter move for unit at {row}, {column} in format row, column:")
#         split_move = player_1_move.split(",")
#         end_row = int(split_move[0])
#         end_column = int(split_move[1])
#         move_unit(board, unit, end_row, end_column)

        
