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
    if player_1_control == 0 and player_2_control == 0 and not cell.city:
        return None
    else:
        return player_1_control - player_2_control

def get_cell_visibility(board: List[List[Cell]], cell: Cell, player: int):
    if cell.city == player:
        return True
    for unit in cell.units:
        if unit.player == player:
            return True
    if cell.type != "forest":
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

def add_unit(board: List[List[Cell]], unit: Unit, cell: Cell):
    if cell.type == "lake" or cell.type == "mountain":
        print("Invalid coordinates, unit cannot be placed on lake.")
        raise ValueError("Player already has 7 units on the board")
    player = unit.player
    player_units = get_player_units(board, player)
    if len(player_units) == 7:
        raise ValueError("Player already has 7 units on the board")
    cell.units.append(unit)

def validate_unit_move(board: List[List[Cell]], unit: Unit, target_cell: Cell):
    starting_cell = get_unit_cell(board, unit)
    if not starting_cell:
        print("Unit not found on board")
        return False
    if target_cell.type == "lake" or target_cell.type == "mountain":
        print("Invalid coordinates, unit cannot be placed on lake.")
        return False
    starting_row, starting_column = get_cell_position(board, starting_cell)
    end_row, end_column = get_cell_position(board, target_cell)
    if abs(starting_row - end_row) +  abs(starting_column - end_column) > unit.movement:
        print("Unit cannot move that far")
        return False
    return True


def move_unit(board: List[List[Cell]], unit: Unit, target_cell: Cell):
    if validate_unit_move(board, unit, target_cell):
        starting_cell = get_unit_cell(board, unit)
        starting_cell.units.remove(unit)
        try:
            add_unit(board, unit, target_cell)
        except Exception as e:
            add_unit(board, unit, starting_cell)
            raise e
    else:
        raise ValueError("Invalid move")

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
            new_controlled_or_contested_cells = {new_cell for new_cell in new_cells if controlled_or_contested(new_cell, player)}
            if not new_controlled_or_contested_cells:
                break
            contiguous_cells.update(new_controlled_or_contested_cells)
            
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
        return winners[0]
    elif len(winners) == 2:
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
    for index,row in enumerate(board):
        line = "|"
        for cell in row:
            if cell.visible:
                if len(cell.units) > 6:
                    number_of_player_1_units = len([unit for unit in cell.units if unit.player == 1])
                    if number_of_player_1_units > 0:
                        line += f"1x{number_of_player_1_units}"
                    else:
                        line += "   "
                elif len(cell.units) > 0:
                    unit = cell.units[0]
                    if unit in cell.units:
                        line += f"({unit.player})"
                else:
                    line += "   "
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
                if len(cell.units) > 6:
                    number_of_player_2_units = len([unit for unit in cell.units if unit.player == 2])
                    if number_of_player_2_units > 0:
                        line += f"2x{number_of_player_2_units}"
                    else:
                        line += "   "
                elif len(cell.units) > 1:
                    unit = cell.units[1]
                    if unit in cell.units:
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
            if cell.visible and len(cell.units) > 2 and len(cell.units) < 7:
                unit = cell.units[2]
                if unit in cell.units:
                    new_line += f"({unit.player})"
            else:
                new_line = " " * 3
            # Check if the current cell is the middle cell for the "mountain"
            if cell.type == "mountain":
                cell_content = "^^^"
            elif cell.type == "forest":
                cell_content = ") ("
            elif cell.type == "lake":
                cell_content = "~~~"
            elif cell.type == "plain":
                if cell.visible and cell.city:
                    cell_content = f"[{cell.city}]"
                else:
                    cell_content = " " * 3
            
            if cell.visible and len(cell.units) > 3 and len(cell.units) < 7:
                unit = cell.units[3]
                if unit in cell.units:
                    cell_content += f"({unit.player})"
            else:
                cell_content += " " * 3

            new_line += cell_content + "|"
            line += new_line
        print(line)
        line = "|"
        for cell_index,cell in enumerate(row):
            if cell.visible:
                if len(cell.units) > 4 and len(cell.units) < 7:
                    unit = cell.units[4]
                    if unit in cell.units:
                        line += f"({unit.player})"
                else:
                    line += (" " * 3)
                if len(cell.units) > 5 and len(cell.units) < 7:
                    unit = cell.units[5]
                    if unit in cell.units:
                        line += f"({unit.player})"
                else:
                    line += (" " * 3)
            else:
                line += (" " * (cell_width-3)) 
            line += f"{index},{cell_index}"+ "|"
        print(line)
        # Print the horizontal separator after each row
        print(horizontal_separator)

def print_player_view(board, player):
    board_copy = copy.deepcopy(board)
    for row in board_copy:
        for cell in row:
            cell.visible = get_cell_visibility(board_copy, cell, player)
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

def validate_user_input_coordinates(user_input: str) -> Tuple[int, int]:
    row = int(user_input.split(",")[0])
    column = int(user_input.split(",")[1])
    if row < 0 or row > 8 or column < 0 or column > 8:
        print("Invalid input, row and column must be between 0 and 8")
        return None
    return row, column


def get_player_coordinate_input(message: str) -> Tuple[int, int] | None:
    while True:
        try:
            user_input = input(message)
            return validate_user_input_coordinates(user_input)
        except Exception:
            print("Invalid input, please enter row and column as integers separated by a comma")
            continue

def place_city(board: List[List[Cell]], player: int):
    while True:
        row, column = get_player_coordinate_input(f"Player {player}, enter city coordinates in format row, column: ")
        if row < 6 or column > 8:
            print("Invalid city placement, city should be built on the last 3 rows")
            continue
        if player == 2:
            row = 8 - row
            column = 8 - column
        cell = board[row][column]
        if cell.type != "plain":
            print("Invalid coordinates, city should be built on a plain")
            continue
        cell.city = player
        break

def place_cities(board):
    # Call the function with the board
    print_player_view(board, 1)
    place_city(board, 1)
    switch_players()
    print_player_view(board, 2)
    place_city(board, 2)

def place_player_units(board: List[List[Cell]], player: int):
    for i in range(7):
        while True:
            row, column = get_player_coordinate_input(f"Player {player}, enter unit coordinates for {i} in format row, column: ")
            if row < 6 or row > 8:
                print("Invalid unit placement, unit should be built on the last 3 rows.")
                continue
            if player == 2:
                row = 8 - row
                column = 8 - column
            try:
                target_cell = board[row][column]
                add_unit(board, Unit(player), target_cell)
            except Exception as e:
                print(e)
                continue
            clear_console()
            print_player_view(board, player)
            break

def place_units(board):
    print_player_view(board, 1)
    place_player_units(board, 1)
    clear_console()
    input("Give board to player 2, then press enter to continue")
    clear_console()
    print_player_view(board, 2)
    place_player_units(board, 2)

def get_player_moves(board: List[List[Cell]], player: int) -> list[tuple[Unit, Cell]]:
    clear_console()
    print_player_view(board, player)
    units = get_player_units(board, player)
    if player == 2:
        units.reverse()
    player_moves = []
    for unit in units:
        while True:
            for player_move in player_moves:
                (old_unit, target_cell) = player_move
                unit_cell = get_unit_cell(board, old_unit)
                unit_cell_row, unit_cell_col = get_cell_position(board, unit_cell)
                target_cell_row, target_cell_col = get_cell_position(board, target_cell)
                if player == 2:
                    unit_cell_row = 8 - unit_cell_row
                    unit_cell_col = 8 - unit_cell_col
                    target_cell_row = 8 - target_cell_row
                    target_cell_col = 8 - target_cell_col
                print(f"Moving unit from {unit_cell_row}, {unit_cell_col} to {target_cell_row}, {target_cell_col}")
            row,column = get_unit_position(board, unit)
            if player == 2:
                row = 8 - row
                column = 8 - column
            input_string = input(f"{player}, Enter move for unit at {row}, {column} in format row, column, or enter to skip:")
            if not input_string:
                break
            end_row, end_column = validate_user_input_coordinates(input_string)
            if player == 2:
                end_row = 8 - end_row
                end_column = 8 - end_column
            target_cell = board[end_row][end_column]
            if validate_unit_move(board, unit, target_cell):
                player_moves.append((unit, target_cell))
                break
            else:
                print("Invalid move, please try again.")
                continue
        clear_console()
        print_player_view(board, player)
    return player_moves

def switch_players():
    clear_console()
    input("Give board to other player, then press enter to continue")
    clear_console()

def place_starter_units(board: List[List[Cell]]):
    board[7][1].city = 1
    board[1][7].city = 2
    for i in range(7):
        add_unit(board, Unit(1), board[8][i])
        add_unit(board, Unit(2), board[0][8-i])

if __name__ == "__main__":
    board = create_standard_board()
    # place_cities(board)
    # switch_players()
    # place_units(board)
    # switch_players()
    place_starter_units(board)
    winner = None
    while winner is None:
        player_moves = []
        player_moves.extend(get_player_moves(board, 1))
        switch_players()
        player_moves.extend(get_player_moves(board, 2))
        for player_move in player_moves:
            (unit, target_cell) = player_move
            move_unit(board, unit, target_cell)
        resolve_units(board)
        winner = check_for_winner(board)
        switch_players()
    if winner == 3:
        print("Game ended in a draw")
    else:
        print(f"Player {winner} wins!")

        
