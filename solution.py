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

        #Then I take all values in the unit with length 2
        vals = [values[box] for box in unit if len(values[box]) == 2]

        #In this loop the values that occur twice and are not included in the unit_twin_values will be appended to the list
        #Boxes that have a value in the unit_twin_values list will be placed in a list, which will be a sublist of unit_twin_boxes.
        #Each sublist of the unit_twin_box will have exactly 2 items
        for value in vals:
            if vals.count(value) == 2 and value not in unit_twin_values:
                unit_twin_values.append(value)
                unit_twin_boxes.append([box for box in unit if values[box] == value])

        #Before start traversing the unit_twin_boxes list, I check if there is any element in this list
        if len(unit_twin_values) > 0:
            for twins in unit_twin_boxes:
                #As these boxes are twins, only one box is need to read the twin value
                digits = values[twins[0]]
                for box in unit:
                    #Check if the box is not one of the twins, because I don't one twin erasing the other
                    if box not in twins and len(values[box]) > 1 and len(digits) == 2:
                        values = assign_value(values, box, values[box].replace(digits[0], '').replace(digits[1], ''))
    return values

def is_valid(values):
    """
    This function test if the values in the first and second diagonals are unique
    It returns true if yes and false otherwise
    """

    digits = '123456789'

    for unit in unitlist:
        for digit in digits:
            digit_occurrences = 0 
            for box in unit:
                if values[box] == digit:
                    digit_occurrences += 1
            if digit_occurrences != 1:
                return False
    return True

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
    """
    Puts the grid chars in a list, replacing . for 123456789
    """
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
    """
    Selects the boxes that have values with length = 1
    subtract this value from its peers
    """
    # for box in boxes:
    #     if len(values[box]) == 1:
    #         for peer in peers[box]:
    #             values = assign_value(values, peer, values[peer].replace(values[box], ''))

    for unit in unitlist:
        solved = [values[box] for box in unit if len(values[box]) == 1]
        for box in unit:
            for digit in solved:
                if len(values[box]) > 1:
                    values = assign_value(values, box, values[box].replace(digit, ''))

    return values

def only_choice(values):
    """
    Select a unit and replace the value of the box with the digit that exists only in this box
    """
    digits = '123456789'

    for unit in unitlist:
        for digit in digits:
            digit_places = [box for box in unit if digit in values[box]]
            if len(digit_places) == 1:
                values = assign_value(values, digit_places[0], digit)
    return values


def reduce_puzzle(values):
    """
    There 3 constraints:
        1 - All values in the diagonals must be unique
        2 - There cannot be more than 1 occurrence of a digit in the same unit
        3 - If only one box in a particular unit can have a digit, this box must be filled with this digit
    If the problem gets stalled, the naked twins technique is used narrow down that numbers of possibilities

    The functions measures the length of the unsolved boxes before and after the reductions, if this length remains the
    same, the naked twins technique will be used. If after the naked twins the sudoku is still stalled, the function return
    the board back 
    """

    stalled = False
    while not stalled:
        unsolved_values_length_before = sum([len(values[box]) for box in boxes if len(values[box]) > 1])
        
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)

        unsolved_values_length_after = sum([len(values[box]) for box in boxes if len(values[box]) > 1])
        stalled = unsolved_values_length_before == unsolved_values_length_after           

        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    """
    First the puzzle is reduced
    If the puzzle is not solved after the reduction, the box with the least amount of choices will be picked
    and one of the values will be chosen. This will be repeated util a diagonal solution is found and the method returns a solution,
    or no solution was found and the method returns false
    """

    values = reduce_puzzle(values)

    if values is False:
        return False
    if all(len(values[s]) == 1 for s in boxes):
        return values

    size,box = min((len(values[box]), box) for box in boxes if len(values[box]) > 1)

    for digit in values[box]:
        game_branch = values.copy()
        game_branch = assign_value(game_branch, box, digit)

        attempt = search(game_branch)

        if attempt:
            if is_valid(attempt):
                return attempt

    return False

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

#As its own name says, these lists and dictionaries store the boxes grouped by its names
boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
first_diagonal = [rows[i]+cols[i] for i in range(0, len(rows))]
second_diagonal = [rows[len(rows) - 1 - i]+cols[i] for i in range(0, len(rows))]
unitlist = [first_diagonal] + [second_diagonal] + row_units + column_units + square_units

if __name__ == '__main__':

    """
    
    #diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    diag_sudoku_grid = '9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................'
    #diag_sudoku_grid = '.5....817412......7...1...................7...49....5.....3....2........6.....9..'

    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')

    """   
    grids = [
        '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3',
        '9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................',
        '.5....817412......7...1...................7...49....5.....3....2........6.....9..',
        '4.......3..9.........1...7.....1.8.....5.9.....1.2.....3...5.........7..7.......8',
        '......3.......12..71..9......36...................56......4..67..95.......8......', 
        '....3...1..6..........9...5.......6..1.7.8.2..8.......3...1..........7..9...2....', 
        '...47..........8.........5.9..2.1...4.......6...3.6..1.7.........4..........89...', 
        '...4.....37.5............89....9......2...7......3....43............2.45.....6...', 
        '..7........5.4...........18...3.6....1.....7....8.2...62...........9.6........4..', 
        '....29.......7......3...8..........735.....161..........6...4......6.......83....', 
        '7.......8.....14...4........7..1.......4.3.......6..2........3...35.....5.......4', 
        '5.......7......2.....3...1...8.4.......7.8.......2.9...8...5.....1......6.......9', 
        '..682...........69..7.......2..........9.4..........8.......5..58...........521..'      
    ]

    for grid in grids:
        assignments.clear()
        solution = solve(grid)

        if solution:
            print('\nDiagonal solution found!:')
            display(solve(grid))
            
            try:
                from visualize import visualize_assignments
                visualize_assignments(assignments)
            except SystemExit:
                pass
            except:
                print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
        else:
            print('\nI couln\'t find a solution the grid:\n', grid, '\n')
    
