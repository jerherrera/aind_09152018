
from utils import *
import itertools

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diagonal_units = [['A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7', 'H8', 'I9'],
                  ['I1', 'H2', 'G3', 'F4', 'E5', 'D6', 'C7', 'B8', 'A9']]
unitlist = row_units + column_units + square_units + diagonal_units


# Must be called after all units (including diagonals) are added to the unitlist
units = extract_units(unitlist, boxes)
peers = extract_peers(units, boxes)

def naked_twins(values):
    # # Collect all possible twins from the Sudoku.
    # possible_twins = [box for box in values if len(values[box]) == 2]
    # true_twins = []
    # # Extract the real twins from the Sudoku.
    # for box1 in possible_twins:
    #     for box2 in peers[box1]:
    #         if values[box1]==values[box2]:
    #             true_twins.append([box1,box2])
    # # Cycle through the real twins 
    # for twins in range(len(true_twins)):  # and extract the boxes for the first pair of potential twins.
    #     box1, box2 = true_twins[twins][0], true_twins[twins][1]   # Collect the peers of each of the boxes
    #     peers_box1, peers_box2 = set(peers[box1]), set(peers[box2])  # Intersect them to see which peers are in common.
    #     peers_isect = peers_box1 & peers_box2 # Cycle through the intersected peers
    #     for peer_id in peers_isect:  # If the intersected peer is larger than two
    #         if len(values[peer_id])>2:  # For each digit of the twins
    #             for xltr in values[box1]: # Reassign 
    #                 values = assign_value(values, peer_id, values[peer_id].replace(xltr,''))
    # return values

    # for box in values:
    #     if len(values[box]) == 2:
    #         for peer in peers[box]:
    #             if values[box] == values[peer]:
    #                 # Change the values of the twins
    #                 total_peers = set(peers[box]) & set(peers[peer])
    #                 for peer_2_change in total_peers:
    #                     if len(values[peer_2_change]) > 2:
    #                         values = assign_value(values, peer_2_change, values[peer_2_change].replace(values[box][0],''))
    #                         values = assign_value(values, peer_2_change, values[peer_2_change].replace(values[box][1],''))
    # return values

    # for unit in unitlist:
    #     for box in unit:
    #         if len(values[box]) == 2:
    #             twin_count = 0
    #             for possible_twin in unit:
    #                 if values[box] == values[possible_twin] and box != possible_twin:
    #                     twin_count += 1
    #                     real_twin = possible_twin
    #             if twin_count == 1:
    #                 ltr1 = values[box][0]
    #                 ltr2 = values[box][1] 
    #                 values = assign_value(values, box, ltr1)
    #                 values = assign_value(values, real_twin, ltr2)
    # return values

    for unit in unitlist:
        # Find all boxes with two digits remaining as possibilities
        pairs = [box for box in unit if len(values[box]) == 2]
        # Pairwise combinations
        poss_twins = [list(pair) for pair in itertools.combinations(pairs, 2)]
        for pair in poss_twins:
            box1 = pair[0]
            box2 = pair[1]
            # Find the naked twins
            if values[box1] == values[box2]:
                for box in unit:
                    # Eliminate the naked twins as possibilities for peers
                    if box != box1 and box != box2:
                        for digit in values[box1]:
                            values[box] = values[box].replace(digit,'')
    return values

def eliminate(values):
    """Apply the eliminate strategy to a Sudoku puzzle

    The eliminate strategy says that if a box has a value assigned, then none
    of the peers of that box can have the same value.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the assigned values eliminated from peers
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit,'')
    return values


def only_choice(values):
    """Apply the only choice strategy to a Sudoku puzzle

    The only choice strategy says that if only one box in a unit allows a certain
    digit, then that box must be assigned that digit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with all single-valued boxes assigned

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values


def reduce_puzzle(values):
    """Reduce a Sudoku puzzle by repeatedly applying all constraint strategies

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary after continued application of the constraint strategies
        no longer produces any changes, or False if the puzzle is unsolvable 
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """Apply depth first search to solve Sudoku puzzles in order to solve puzzles
    that cannot be solved by repeated reduction alone.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary with all boxes assigned or False

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    and extending it to call the naked twins strategy.
    """
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes): 
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and 
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    """Find the solution to a Sudoku puzzle using search and constraint propagation

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.
        
        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    Returns
    -------
    dict or False
        The dictionary representation of the final sudoku grid or False if no solution exists.
    """
    values = grid2values(grid)
    values = search(values)
    return values


if __name__ == "__main__":
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(grid2values(diag_sudoku_grid))
    result = solve(diag_sudoku_grid)
    display(result)

    try:
        import PySudoku
        PySudoku.play(grid2values(diag_sudoku_grid), result, history)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
