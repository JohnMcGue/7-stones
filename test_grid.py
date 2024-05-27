import pytest
import grid

@pytest.fixture
def board():
    return grid.create_standard_board()

def test_unit_dies_when_cell_is_controlled_by_opponent(board):
    player_1_unit = grid.Unit(1)
    grid.add_unit(board, player_1_unit, 6, 6)
    player_2_unit = grid.Unit(2)
    player_2_unit_2 = grid.Unit(2)
    grid.add_unit(board, player_2_unit, 6, 6)
    grid.add_unit(board, player_2_unit_2, 6, 6)
    grid.resolve_units(board)
    grid.print_board(board)
    cell = board[6][6]
    assert grid.check_player_controls_cell(board, cell, 2)
    assert player_1_unit not in cell.units

def test_get_contiguous_controlled_cells_returns_appropriate_cells_for_one_unit(board):
    player_1_unit = grid.Unit(1)
    grid.add_unit(board, player_1_unit, 6, 6)
    contiguous_cells = grid.get_contiguous_controlled_or_contested_cells(board, board[6][6], 1)
    expected_contiguous_cells = set(grid.get_adjacent_cells(board, board[6][6]))
    expected_contiguous_cells.add(board[6][6])
    assert contiguous_cells == expected_contiguous_cells
    expected_adjacent_cells = {board[6][4], board[6][8], board[4][6], board[8][6], board[5][5], board[7][7], board[5][7], board[7][5]}
    assert grid.get_cells_adjacent_to_set(board, contiguous_cells) == expected_adjacent_cells

def test_get_contiguous_controlled_cells_returns_appropriate_cells_for_two_units(board):
    player_1_unit = grid.Unit(1)
    grid.add_unit(board, player_1_unit, 6, 6)
    player_1_unit_2 = grid.Unit(1)
    grid.add_unit(board, player_1_unit_2, 6, 7)
    contiguous_cells = grid.get_contiguous_controlled_or_contested_cells(board, board[6][6], 1)
    expected_contiguous_cells = set(grid.get_adjacent_cells(board, board[6][6]))
    expected_contiguous_cells.update(set(grid.get_adjacent_cells(board, board[6][7])))
    assert contiguous_cells == expected_contiguous_cells
    expected_adjacent_cells = {board[6][4], board[5][5], board[4][6], board[4][7], board[5][8], board[7][8], board[8][7], board[8][6], board[7][5]}
    assert grid.get_cells_adjacent_to_set(board, contiguous_cells) == expected_adjacent_cells

def test_get_contiguous_controlled_cells_for_no_unit(board):
    contiguous_cells = grid.get_contiguous_controlled_or_contested_cells(board, board[6][6], 1)
    assert contiguous_cells == set()

def test_get_contiguous_controlled_cells_returns_appropriate_cells_for_neutral_square(board):
    player_1_unit = grid.Unit(1)
    grid.add_unit(board, player_1_unit, 6, 6)
    player_2_unit = grid.Unit(2)
    grid.add_unit(board, player_2_unit, 5, 6)
    player_2_unit_2 = grid.Unit(2)
    grid.add_unit(board, player_2_unit_2, 7, 4)
    player_2_unit_3 = grid.Unit(2)
    grid.add_unit(board, player_2_unit_3, 8, 7)
    player_2_unit_4 = grid.Unit(2)
    grid.add_unit(board, player_2_unit_4, 5, 8)
    grid.print_board(board)
    contiguous_cells = grid.get_contiguous_controlled_or_contested_cells(board, board[6][6], 1)
    print(contiguous_cells)
    expected_contiguous_cells = set(grid.get_adjacent_cells(board, board[6][6]))
    expected_contiguous_cells.update({board[6][6]})
    assert contiguous_cells == expected_contiguous_cells
    expected_adjacent_cells = {board[6][4], board[5][5], board[4][6], board[5][7], board[6][8], board[7][7], board[8][6], board[7][5]}
    adjacent_cells = grid.get_cells_adjacent_to_set(board, contiguous_cells)
    for cell in adjacent_cells:
        print(grid.get_cell_position(board, cell))
    assert adjacent_cells == expected_adjacent_cells

def test_unit_dies_when_surrounding_cells_are_controlled_by_opponent(board):
    player_1_unit = grid.Unit(1)
    grid.add_unit(board, player_1_unit, 6, 6)
    player_2_unit = grid.Unit(2)
    grid.add_unit(board, player_2_unit, 7, 7)
    player_2_unit_2 = grid.Unit(2)
    grid.add_unit(board, player_2_unit_2, 7, 7)
    player_2_unit_3 = grid.Unit(2)
    grid.add_unit(board, player_2_unit_3, 5, 5)
    player_2_unit_4 = grid.Unit(2)
    grid.add_unit(board, player_2_unit_4, 5, 5)
    cell = board[6][6]
    assert grid.check_player_controls_cell(board, cell, 1)
    adjacent_cells = grid.get_adjacent_cells(board, cell)
    for adjacent_cell in adjacent_cells:
        assert grid.check_player_controls_cell(board, adjacent_cell, 2)
    grid.resolve_units(board)
    assert player_1_unit not in cell.units

def test_simultaneous_deaths(board):
    player_1_unit = grid.Unit(1)
    grid.add_unit(board, player_1_unit, 6, 6)
    player_1_unit_2 = grid.Unit(1)
    grid.add_unit(board, player_1_unit_2, 6, 6)
    player_2_unit_0 = grid.Unit(2)
    grid.add_unit(board, player_2_unit_0, 6, 6)
    player_2_unit = grid.Unit(2)
    grid.add_unit(board, player_2_unit, 7, 7)
    player_2_unit_2 = grid.Unit(2)
    grid.add_unit(board, player_2_unit_2, 7, 7)
    player_2_unit_3 = grid.Unit(2)
    grid.add_unit(board, player_2_unit_3, 5, 5)
    player_2_unit_4 = grid.Unit(2)
    grid.add_unit(board, player_2_unit_4, 5, 5)
    grid.resolve_units(board)
    cell = board[6][6]
    assert player_1_unit not in cell.units
    assert player_1_unit_2 not in cell.units
    assert player_2_unit_0 not in cell.units

def test_unit_dies_when_surrounded_even_if_unit_square_is_neutral(board):
    player_1_unit = grid.Unit(1)
    grid.add_unit(board, player_1_unit, 6, 6)
    player_2_unit = grid.Unit(2)
    grid.add_unit(board, player_2_unit, 5, 6)
    player_2_unit_2 = grid.Unit(2)
    grid.add_unit(board, player_2_unit_2, 7, 4)
    player_2_unit_3 = grid.Unit(2)
    grid.add_unit(board, player_2_unit_3, 8, 7)
    player_2_unit_4 = grid.Unit(2)
    grid.add_unit(board, player_2_unit_4, 5, 8)
    grid.resolve_units(board)
    cell = board[6][6]
    assert player_1_unit not in cell.units

# one unit's death triggers the death of another unit
def test_cascading_deaths(board):
    player_1_unit = grid.Unit(1)
    grid.add_unit(board, player_1_unit, 6, 6)
    player_1_unit_2 = grid.Unit(1)
    grid.add_unit(board, player_1_unit_2, 6, 4)
    grid.add_unit(board, grid.Unit(2), 5, 5)
    grid.add_unit(board, grid.Unit(2), 5, 5)
    grid.add_unit(board, grid.Unit(2), 7, 3)
    grid.add_unit(board, grid.Unit(2), 7, 3)
    grid.print_board(board)
    grid.resolve_units(board)
    assert player_1_unit in board[6][6].units
    assert player_1_unit_2 in board[6][4].units
    grid.add_unit(board, grid.Unit(2), 6, 7)
    grid.add_unit(board, grid.Unit(2), 6, 7)
    grid.resolve_units(board)
    assert player_1_unit not in board[6][6].units
    assert player_1_unit_2 not in board[6][4].units

def test_player_2_win(board):
    board[6][6].city = 1
    grid.add_unit(board, grid.Unit(2), 6, 7)
    winner = grid.check_for_winner(board)
    assert winner == 2

def test_player_1_win(board):
    board[6][6].city = 2
    grid.add_unit(board, grid.Unit(1), 6, 6)
    winner = grid.check_for_winner(board)
    assert winner == 1

def test_draw(board):
    board[6][6].city = 1
    grid.add_unit(board, grid.Unit(2), 6, 6)
    board[3][3].city = 2
    grid.add_unit(board, grid.Unit(1), 3, 3)
    winner = grid.check_for_winner(board)
    assert winner == 3

def test_game_not_over(board):
    winner = grid.check_for_winner(board)
    assert winner is None

def test_uncontrolled_city_does_not_end_game(board):
    board[6][6].city = 1
    winner = grid.check_for_winner(board)
    assert winner is None
