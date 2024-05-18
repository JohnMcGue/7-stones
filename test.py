import unittest
import grid
        

class TestUnitDeath(unittest.TestCase):
    def setUp(self):
        self.board = grid.create_standard_board()
    
    def tearDown(self):
        self.board = None
    
    def test_unit_dies_when_cell_is_controlled_by_opponent(self):
        player_1_unit = grid.Unit(1)
        grid.add_unit(self.board, player_1_unit, 6,6)
        player_2_unit = grid.Unit(2)
        player_2_unit_2 = grid.Unit(2)
        grid.add_unit(self.board, player_2_unit, 6,6)
        grid.add_unit(self.board, player_2_unit_2, 6,6)
        grid.resolve_units(self.board)
        grid.print_board(self.board)
        cell = self.board[6][6]
        self.assertTrue(grid.check_player_controls_cell(self.board, cell, 2))
        self.assertTrue(player_1_unit not in cell.units)

    def test_get_contiguous_controlled_cells_returns_appropriate_cells_for_one_unit(self):
        player_1_unit = grid.Unit(1)
        grid.add_unit(self.board, player_1_unit, 6,6)
        contiguous_cells = grid.get_contiguous_controlled_or_contested_cells(self.board, self.board[6][6], 1)
        expected_contiguous_cells = set(grid.get_adjacent_cells(self.board, self.board[6][6]))
        expected_contiguous_cells.add(self.board[6][6])
        self.assertEqual(contiguous_cells, expected_contiguous_cells)
        expected_adjacent_cells = set()
        expected_adjacent_cells.add(self.board[6][4])
        expected_adjacent_cells.add(self.board[6][8])
        expected_adjacent_cells.add(self.board[4][6])
        expected_adjacent_cells.add(self.board[8][6])
        expected_adjacent_cells.add(self.board[5][5])
        expected_adjacent_cells.add(self.board[7][7])
        expected_adjacent_cells.add(self.board[5][7])
        expected_adjacent_cells.add(self.board[7][5])
        self.assertEqual(grid.get_cells_adjacent_to_set(self.board, contiguous_cells), expected_adjacent_cells)

    def test_get_contiguous_controlled_cells_returns_appropriate_cells_for_two_units(self):
        player_1_unit = grid.Unit(1)
        grid.add_unit(self.board, player_1_unit, 6,6)
        player_1_unit_2 = grid.Unit(1)
        grid.add_unit(self.board, player_1_unit_2, 6,7)
        contiguous_cells = grid.get_contiguous_controlled_or_contested_cells(self.board, self.board[6][6], 1)
        expected_contiguous_cells = set(grid.get_adjacent_cells(self.board, self.board[6][6]))
        expected_contiguous_cells.update(set(grid.get_adjacent_cells(self.board, self.board[6][7])))
        self.assertEqual(contiguous_cells, expected_contiguous_cells)
        expected_adjacent_cells = set()
        expected_adjacent_cells.add(self.board[6][4])
        expected_adjacent_cells.add(self.board[5][5])
        expected_adjacent_cells.add(self.board[4][6])
        expected_adjacent_cells.add(self.board[4][7])
        expected_adjacent_cells.add(self.board[5][8])
        expected_adjacent_cells.add(self.board[7][8])
        expected_adjacent_cells.add(self.board[8][7])
        expected_adjacent_cells.add(self.board[8][6])
        expected_adjacent_cells.add(self.board[7][5])
        self.assertEqual(grid.get_cells_adjacent_to_set(self.board, contiguous_cells), expected_adjacent_cells)

    def test_get_contiguous_controlled_cells_for_no_unit(self):
        contiguous_cells = grid.get_contiguous_controlled_or_contested_cells(self.board, self.board[6][6], 1)
        self.assertEqual(contiguous_cells, set())
        expected_adjacent_cells = set()
        expected_adjacent_cells.add(self.board[6][5])
        expected_adjacent_cells.add(self.board[6][7])
        expected_adjacent_cells.add(self.board[5][6])
        expected_adjacent_cells.add(self.board[7][6])
        self.assertEqual(grid.get_cells_adjacent_to_set(self.board, contiguous_cells), expected_adjacent_cells)

    def test_get_contiguous_controlled_cells_returns_appropriate_cells_for_neutral_square(self):
        player_1_unit = grid.Unit(1)
        grid.add_unit(self.board, player_1_unit, 6,6)
        player_2_unit = grid.Unit(2)
        grid.add_unit(self.board, player_2_unit, 5,6)
        player_2_unit_2 = grid.Unit(2)
        grid.add_unit(self.board, player_2_unit_2, 7,4)
        player_2_unit_3 = grid.Unit(2)
        grid.add_unit(self.board, player_2_unit_3, 8,7)
        player_2_unit_4 = grid.Unit(2)
        grid.add_unit(self.board, player_2_unit_4, 5,8)
        contiguous_cells = grid.get_contiguous_controlled_or_contested_cells(self.board, self.board[6][6], 1)
        expected_contiguous_cells = set(grid.get_adjacent_cells(self.board, self.board[6][6]))
        expected_contiguous_cells.update(set(grid.get_adjacent_cells(self.board, self.board[6][7])))
        self.assertEqual(contiguous_cells, expected_contiguous_cells)
        expected_adjacent_cells = set()
        expected_adjacent_cells.add(self.board[6][4])
        expected_adjacent_cells.add(self.board[5][5])
        expected_adjacent_cells.add(self.board[4][6])
        expected_adjacent_cells.add(self.board[4][7])
        expected_adjacent_cells.add(self.board[5][8])
        expected_adjacent_cells.add(self.board[7][8])
        expected_adjacent_cells.add(self.board[8][7])
        expected_adjacent_cells.add(self.board[8][6])
        expected_adjacent_cells.add(self.board[7][5])
        self.assertEqual(grid.get_cells_adjacent_to_set(contiguous_cells), expected_adjacent_cells)
    
    def test_unit_dies_when_surrounding_cells_are_controlled_by_opponent(self):
        player_1_unit = grid.Unit(1)
        grid.add_unit(self.board, player_1_unit, 6,6)
        player_2_unit = grid.Unit(2)
        grid.add_unit(self.board, player_2_unit, 7,7)
        player_2_unit_2 = grid.Unit(2)
        grid.add_unit(self.board, player_2_unit_2, 7,7)
        player_2_unit_3 = grid.Unit(2)
        grid.add_unit(self.board, player_2_unit_3, 5,5)
        player_2_unit_4 = grid.Unit(2)
        grid.add_unit(self.board, player_2_unit_4, 5,5)
        cell = self.board[6][6]
        self.assertTrue(grid.check_player_controls_cell(self.board, cell, 1))
        adjacent_cells = grid.get_adjacent_cells(self.board, cell)
        for adjacent_cell in adjacent_cells:
            self.assertTrue(grid.check_player_controls_cell(self.board, adjacent_cell, 2))
        grid.resolve_units(self.board)
        self.assertTrue(player_1_unit not in cell.units)
    
    # two player 1 units on a square with 1 player 2 unit on it, 
    # implies that the player 2 unit dies b/c player 1 controls that square
    # also 2 player 2 units on each caddy corner square to that one, so the adjacent squares around the main square
    # have 2+1=3 player 2 control and 2 player 1 control, meaning they are controlled by player 2
    # and the player 1 units on the main square should die
    # but player 2 only has control of adjacent squares because of the player 2 unit on the main square
    # catch-22 situation. should all 3 central square units die?
    # should there be an ordering to unit death? ie resolve immediate square, then work outwards?
    def test_simultaneous_deaths(self):
        player_1_unit = grid.Unit(1)
        grid.add_unit(self.board, player_1_unit, 6,6)
        player_1_unit_2 = grid.Unit(1)
        grid.add_unit(self.board, player_1_unit_2, 6,6)
        player_2_unit_0 = grid.Unit(2)
        grid.add_unit(self.board, player_2_unit_0, 6,6)
        player_2_unit = grid.Unit(2)
        grid.add_unit(self.board, player_2_unit, 7,7)
        player_2_unit_2 = grid.Unit(2)
        grid.add_unit(self.board, player_2_unit_2, 7,7)
        player_2_unit_3 = grid.Unit(2)
        grid.add_unit(self.board, player_2_unit_3, 5,5)
        player_2_unit_4 = grid.Unit(2)
        grid.add_unit(self.board, player_2_unit_4, 5,5)
        grid.resolve_units(self.board)
        cell = self.board[6][6]
        self.assertTrue(player_1_unit not in cell.units)
        self.assertTrue(player_1_unit_2 not in cell.units)
        self.assertTrue(player_2_unit_0 not in cell.units)
    
    def test_unit_dies_when_surrounded_even_if_unit_square_is_neutral(self):
        player_1_unit = grid.Unit(1)
        grid.add_unit(self.board, player_1_unit, 6,6)
        player_2_unit = grid.Unit(2)
        grid.add_unit(self.board, player_2_unit, 5,6)
        player_2_unit_2 = grid.Unit(2)
        grid.add_unit(self.board, player_2_unit_2, 7,4)
        player_2_unit_3 = grid.Unit(2)
        grid.add_unit(self.board, player_2_unit_3, 8,7)
        player_2_unit_4 = grid.Unit(2)
        grid.add_unit(self.board, player_2_unit_4, 5,8)
        grid.resolve_units(self.board)
        cell = self.board[6][6]
        self.assertTrue(player_1_unit not in cell.units)
    
    def test_cascading_deaths(self):
        player_1_unit = grid.Unit(1)
        grid.add_unit(self.board, player_1_unit, 6,6)
        player_1_unit_2 = grid.Unit(1)
        grid.add_unit(self.board, player_1_unit_2, 6,6)
        player_2_unit = grid.Unit(2)
        grid.add_unit(self.board, player_2_unit, 7,7)
        player_2_unit_2 = grid.Unit(2)
        grid.add_unit(self.board, player_2_unit_2, 7,7)
        player_2_unit_3 = grid.Unit(2)
        grid.add_unit(self.board, player_2_unit_3, 5,5)
        player_2_unit_4 = grid.Unit(2)
        grid.add_unit(self.board, player_2_unit_4, 5,5)
        grid.resolve_units(self.board)
        self.assertTrue(player_1_unit not in self.board[6][6].units)
        self.assertTrue(player_2_unit not in self.board[7][7].units)
        self.assertTrue(player_2_unit_2 not in self.board[7][7].units)
        self.assertTrue(player_2_unit_3 not in self.board[5][5].units)
        self.assertTrue(player_2_unit_4 not in self.board[5][5].units)

if __name__ == '__main__':
    unittest.main()