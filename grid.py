from functools import cache
import os
import copy
from typing import List, Set, Tuple
import uuid

class Cell():
    def __init__(self):
        self.type = "plain"
        self.city = None
        self.units = []
        self.visible = True
        self.uuid = uuid.uuid4()

    def __eq__(self, other):
        return self.uuid == other.uuid
    
    def __hash__(self):
        return hash(self.uuid)

class Unit():
    movement = 1
    control = 1
    vision = 1
    def __init__(self, player):
        self.player = player
        self.uuid = uuid.uuid4()
    
    def __eq__(self, other):
        return self.uuid == other.uuid

def get_cell_position(board: List[List[Cell]], cell: Cell):
    for row_index, row in enumerate(board):
        for column_index, current_cell in enumerate(row):
            if current_cell == cell:
                return row_index, column_index
    raise ValueError("Cell not found on board")

def get_adjacent_cells(board: List[List[Cell]], cell: Cell) -> Set[Cell]:
    adjacent_cells = set()
    row, column = get_cell_position(board, cell)
    if row > 0:
        adjacent_cells.add(board[row-1][column])
    if row < len(board) - 1:
        adjacent_cells.add(board[row+1][column])
    if column > 0:
        adjacent_cells.add(board[row][column-1])
    if column < len(board[0]) - 1:
        adjacent_cells.add(board[row][column+1])
    return adjacent_cells

def get_cells_adjacent_to_set(board: List[List[Cell]], cells: Set[Cell]) -> Set[Cell]:
    adjacent_cells = set()
    for cell in cells:
        adjacent_cells.update(get_adjacent_cells(board, cell))
    return adjacent_cells - cells 

def get_cell_control(board: List[List[Cell]], cell: Cell) -> tuple[int, int]:
    player_1_control = 0
    player_2_control = 0
    cells_to_check = [cell]
    adjacent_cells = get_adjacent_cells(board, cell)
    cells_to_check.extend(adjacent_cells)
    for current_cell in cells_to_check:
        for unit in current_cell.units:
            if unit.player == 1:
                player_1_control += unit.control
            else:
                player_2_control += unit.control
    if player_1_control == 0 and player_2_control == 0:
        return None
    else:
        return player_1_control - player_2_control

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
    if row < 0 or row > 8 or column < 0 or column > 8:
        print("Invalid unit placement, unit cannot be added off grid.")
        raise ValueError("Unit cannot be placed outside the board")
    cell = board[row][column]
    if cell.type == "lake" or cell.type == "mountain":
        print("Invalid coordinates, unit cannot be placed on lake.")
        raise ValueError("Unit cannot be placed on lake or mountain")
    player = unit.player
    player_units = get_player_units(board, player)
    if len(player_units) == 7:
        raise ValueError("Player already has 7 units on the board")
    cell.units.append(unit)

def move_unit(board: List[List[Cell]], unit: Unit, end_row: int, end_column: int):
    starting_cell = get_unit_cell(board, unit)
    if not starting_cell:
        print("Unit not found on board")
        raise ValueError("Unit not found on board")
    starting_row, starting_column = get_cell_position(board, starting_cell)
    if abs(starting_row - end_row) +  abs(starting_column - end_column) > unit.movement:
        print("Unit cannot move that far")
        raise ValueError("Unit cannot move that far")
    starting_cell.units.remove(unit)
    try:
        add_unit(board, unit, end_row, end_column)
    except Exception as e:
        add_unit(board, unit, starting_row, starting_column)
        raise e

def remove_unit(board: List[List[Cell]], unit: Unit):
    cell = get_unit_cell(board, unit)
    cell.units.remove(unit)

def check_player_control(control_value: int, player: int) -> bool:
    if control_value is None:
        return False
    return control_value > 0 if player == 1 else control_value < 0

def check_player_controls_cell(board: List[List[Cell]], cell: Cell, player: int) -> bool:
    control_value = get_cell_control(board, cell)
    return check_player_control(control_value, player)

def get_contiguous_controlled_or_contested_cells(board: List[List[int]], cell: Cell, player: int) -> Set[Cell]:
    def controlled_or_contested(cell, player):
        control_value = get_cell_control(board, cell)
        return control_value == 0 or check_player_control(control_value, player)
    
    if controlled_or_contested(cell, player):
        contiguous_cells = {cell}
        while True:
            new_cells = get_cells_adjacent_to_set(board, contiguous_cells)
            contiguous_cells.update(new_cells)
            if not any(controlled_or_contested(new_cell, player) for new_cell in new_cells):
                break
            
        return contiguous_cells
    else:
        return set()

def get_opposing_player(player: int) -> int:
    return 1 if player == 2 else 2

def check_for_freedom(board: List[List[Cell]], cell: Cell, player: int) -> bool:
    opponent = get_opposing_player(player)
    if check_player_controls_cell(board, cell, opponent):
        return False
    contiguous_cells = get_contiguous_controlled_or_contested_cells(board, cell, player)
    adjacent_cells = get_cells_adjacent_to_set(board, contiguous_cells)
    if all(check_player_controls_cell(board, adjacent_cell, opponent) for adjacent_cell in adjacent_cells):
        return False
    return True

def resolve_units(board: List[List[Cell]]) -> int | None:
    while True:
        units_to_be_removed = []
        for row in board:
            for cell in row:
                if cell.units:
                    player_1_units = [unit for unit in cell.units if unit.player == 1]
                    if len(player_1_units) > 0:
                        if not check_for_freedom(board, cell, 1):
                            for unit in player_1_units:
                                units_to_be_removed.append(unit)
                    player_2_units = [unit for unit in cell.units if unit.player == 2]
                    if len(player_2_units) > 0:
                        if not check_for_freedom(board, cell, 2):
                            for unit in player_2_units:
                                units_to_be_removed.append(unit)

        if len(units_to_be_removed) == 0:
            break
        for unit in units_to_be_removed:
            remove_unit(board, unit)
    
def check_for_winner(board: List[List[Cell]]) -> int | None:
    winners = []
    for row in board:
        for cell in row:
            if cell.city:
                if not check_for_freedom(board, cell, cell.city):
                    winners.append(get_opposing_player(cell.city))
    if len(winners) == 1:
        print(f"Player {winners[0]} wins!")
        return winners[0]
    elif len(winners) == 2:
        print("It's a draw!")
        return 3
    return None

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
                if cell.type == "mountain" or cell.type == "lake":
                    line += f"   "
                else:
                    control_value = get_cell_control(board, cell)
                    if control_value is None:
                        line += " N "
                    else:
                        if control_value < 0:
                            line += f"{control_value} "
                        else:
                            line += f" {control_value} "
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

def create_standard_board() -> List[List[Cell]]:
    board = [[Cell() for _ in range(9)] for _ in range(9)]
    board[4][4].type = "mountain"
    board[2][2].type = "forest"
    board[6][6].type = "forest"
    board[2][6].type = "lake"
    board[6][2].type = "lake"
    return board

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

def player_turn(board: List[List[Cell]], player: int):
    clear_console()
    print_player_view(board, player)
    units = get_player_units(board, player)
    if player == 2:
        units.reverse()
    for unit in units:
        while True:
            row,column = get_unit_position(board, unit)
            if player == 2:
                row = 8 - row
                column = 8 - column
            player_move = input(f"{player}, Enter move for unit at {row}, {column} in format row, column, or enter to skip:")
            if not player_move:
                break
            split_move = player_move.split(",")
            end_row = int(split_move[0])
            end_column = int(split_move[1])
            if player == 2:
                end_row = 8 - end_row
                end_column = 8 - end_column
            try:
                move_unit(board, unit, end_row, end_column)
            except:
                print("Invalid move, please try again.")
                continue
            break
        clear_console()
        print_player_view(board, player)

if __name__ == "__main__":
    board = create_standard_board()
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
    while True:
        player_turn(board, 1)
        player_turn(board, 2)
        resolve_units(board)
        winner = check_for_winner(board)

        
