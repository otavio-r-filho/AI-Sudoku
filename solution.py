assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers

    #First select a unit
    for unit in unitlist:
        unit_twin_values = [] #This vector will store the twin values
        unit_twin_boxes = [] #This vector will store the twin boxes

        vals = [values[box] for box in unit]
        #Searching for twin values with 2 digits
        for value in vals:
            if vals.count(value) == 2 and len(value) == 2 and value not in unit_twin_values:
                unit_twin_values.append(value)
                unit_twin_boxes.append([box for box in unit if values[box] == value])

        #Check if this unit has any twin value
        if len(unit_twin_values) > 0:
            for twins in unit_twin_boxes:
                digits = values[twins[0]]
                for box in unit:
                    #Check if the box is not one of the twins
                    if box not in twins and len(values[box]) > 1:
                        values = assign_value(values, box, values[box].replace(digits[0], '').replace(digits[1], ''))
        #Sanity check ;)
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False

    return values

def diagonal(values):
    first_diagonal_solved = [values[box] for box in frst_diagonal if len(values[box]) == 1]
    second_diagonal_solved = [values[box] for box in scnd_diagonal if len(values[box]) == 1]

    for box in frst_diagonal:
        for value in first_diagonal_solved:
            if len(values[box]) > 1:
                value = assign_value(values, box, values[box].replace(value,''))

    for box in scnd_diagonal:
        for value in second_diagonal_solved:
            if len(values[box]) > 1:
                value = assign_value(values, box, values[box].replace(value,''))

    return values

def cross(A, B):
    #Cross product of elements in A and elements in B.
    return [a+b for a in A for b in B]

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    digits = '123456789'
    chars = []

    for digit in grid:
        if digit in digits:
            chars.append(digit)
        else:
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '') for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    #Getting the list of pre solved values
    solved_values = [box for box in values.keys() if len(values[box]) == 1]

    """
    Instead of using an iterator of the pre-solved values, I could used the iterator
    of the values dictionary and also eliminate values for the box that would be solved 
    in the process. 
    I'm not using this beacuase in the exercises this answer was not valid
    """
    for box in solved_values:
        for peer in peers[box]:
            values = assign_value(values, peer, values[peer].replace(values[box], ''))
    return values

def only_choice(values):
    digits = '123456789'

    for unit in unitlist:
        for digit in digits:
            digit_places = [box for box in unit if digit in values[box]]
            if len(digit_places) == 1:
                values = assign_value(values, digit_places[0], digit)
    return values


def reduce_puzzle(values):
    stalled = False
    while not stalled:
        solve_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = diagonal(values)
        values = eliminate(values)
        values = only_choice(values)
        solve_values_after = len([box for box in values.keys() if len(values[box]) == 1])

        stalled = solve_values_before == solve_values_after

        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    values = naked_twins(values)
    return values

def search(values):

    values = reduce_puzzle(values)

    if values is False:
        return False
    if all(len(values[s]) == 1 for s in boxes):
        return values

    siz,box = min((len(values[box]), box) for box in boxes if len(values[box]) > 1)

    for digit in values[box]:
        game_branch = values.copy()
        game_branch = assign_value(game_branch, box, digit)

        attempt = search(game_branch)

        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    values = search(values)

    return values

rows = 'ABCDEFGHI'
cols = '123456789'

boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
frst_diagonal = [rows[i]+cols[i] for i in range(0, len(rows))]
scnd_diagonal = [rows[len(rows) - 1 - i]+cols[i] for i in range(0, len(rows))]
unitlist = row_units + column_units + square_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
