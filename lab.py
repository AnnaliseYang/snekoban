"""
6.1010 Lab 4:
Snekoban Game
"""

import json
import typing

# NO ADDITIONAL IMPORTS!


direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}


def make_new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    game = level_description
    height = len(game)
    width = len(game[0])

    # dictionary mapping each object to a set of locations (row, col)
    object_positions = {
        "player": set(),
        "computer": set(),
        "target": set(),
        "wall": set(),
    }
    for row in range(height):
        for col in range(width):
            if game[row][col]:
                for obj in game[row][col]:
                    # loop over all positions and find the object
                    object_positions[obj].add((row, col))
                    if obj == "player":
                        player_pos = (row, col)

    new_game = {
        "height": height,
        "width": width,
        "positions": object_positions,
        "player_pos": player_pos
    }
    return new_game


def get_height(game):
    return game["height"]

def get_width(game):
    return game["width"]

def get_player_position(game):
    return game["player_pos"]

def get_objects(game, row, col):
    """returns a set of all the objects in a certain position"""
    out = set()
    if row in range(get_height(game)) and col in range(get_width(game)):
        for obj, locs in game["positions"].items():
            # check of the given location contains the object
            if (row, col) in locs:
                out.add(obj)
    return out

def get_positions(game, obj):
    """
    returns a set of positions (row, col) that contain the given object
    """
    return game["positions"][obj]

def copy_game(game):
    game_copy = {
        "height": get_height(game),
        "width": get_width(game),
        "positions": {key: val.copy() for key, val in game["positions"].items()},
        "player_pos": get_player_position(game)
    }
    return game_copy

def move_object(game, pos, new_pos, obj):
    """
    Takes in the game, a position (row, col)
    and direction ("up", "down", "left", "right")
    Returns a new game with the updated location
    """
    if pos in game["positions"][obj]:
        # remove the current position from the game dictionary
        game["positions"][obj].remove(pos)
        # add the new position
        game["positions"][obj].add(new_pos)

    # update player position
    if obj == "player":
        game["player_pos"] = new_pos


def victory_check(game):
    """
    Given a game representation (of the form returned from make_new_game),
    return a Boolean: True if the given game satisfies the victory condition,
    and False otherwise.
    """
    target_positions = get_positions(game, "target")
    if target_positions == set():
        # if there are no targets, return False
        return False
    else:
        for pos in target_positions:
            # if ANY of the computers are not in a target location, return False
            if "computer" not in get_objects(game, *pos):
                return False
        return True

def step(game, pos, direction):
    """
    Takes in a position (row, col)
    Returns a new position (row, col) after the move
    """
    # define the current position and change in position
    row, col = pos
    dy, dx = direction_vector[direction]

    new_row = row + dy if row + dy in range(get_height(game)) else row
    new_col = col + dx if col + dx in range(get_width(game)) else col

    # new position after one step
    new_pos = (new_row, new_col)
    return new_pos

def valid_step(game, pos, direction):
    """
    Return the new position if the step is valid, otherwise return None
    """
    new_pos = step(game, pos, direction)
    wall_pos = get_positions(game, "wall")
    computer_pos = get_positions(game, "computer")

    # Case 1: if the player hits a wall, return None
    if new_pos in wall_pos:
        return None
    # Case 2: if the player moves to a computer location,
    # check if there is one or two computers in a row
    if new_pos in computer_pos:
        # check the position two steps over from the current position
        new_pos_2 = step(game, new_pos, direction)
        if new_pos_2 not in wall_pos | computer_pos:
            return new_pos # the player pushes one computer
        else:
            return None # the player doesn't move if th
    else:
        return new_pos

def step_game(game, direction):
    """
    Given a game representation (of the form returned from make_new_game),
    return a new game representation (of that same form), representing the
    updated game after running one step of the game.  The user's input is given
    by direction, which is one of the following:
        {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """
    current_pos = get_player_position(game)
    new_pos = valid_step(game, current_pos, direction)

    if new_pos:
        # if the new position is valid, return a new game.
        # otherwise return the original game
        new_game = copy_game(game)
        move_object(new_game, current_pos, new_pos, "player")
        if new_pos in get_positions(game, "computer"):
            new_pos_2 = step(game, new_pos, direction)
            move_object(new_game, new_pos, new_pos_2, "computer")
        return new_game
    return game



def dump_game(game):
    """
    Given a game representation (of the form returned from make_new_game),
    convert it back into a level description that would be a suitable input to
    make_new_game (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    out = [] # output list
    height = get_height(game)
    width = get_width(game)

    def layer(obj):
        """sorts objects by the order they appear on the screen"""
        return 0 if obj == "target" else 1

    # convert the new game representation back into a list of lists
    for row in range(height):
        current_row = [] # make a list objects for each row
        for col in range(width):
            current_cell = [] # make a listof objects for each position
            for obj in sorted(get_objects(game, row, col), key = layer):
                if obj:
                    current_cell.append(obj)
            current_row.append(current_cell)
        out.append(current_row)

    return out


def solve_puzzle(game):
    """
    Given a game representation (of the form returned from make_new_game), find
    a solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """

    def visited_key(game):
        """helper function that returns the key used for the visited set"""
        return get_player_position(game), frozenset(get_positions(game, "computer"))

    start_game = copy_game(game)
    paths = [[start_game]]
    visited = {visited_key(start_game)}

    directions = ["up", "down", "left", "right"]

    while paths:
        path = paths.pop(0)
        current_game = path.pop()

        if victory_check(current_game):
            # return the current path if the player won
            return path
        else:
            # otherwise continue BFS to find the shortest path
            for direction in directions:
                if valid_step(current_game, get_player_position(current_game), direction):
                    new_game = step_game(current_game, direction)
                    if visited_key(new_game) not in visited:
                        new_path = path + [direction, new_game]
                        paths.append(new_path)
                        visited.add(visited_key(new_game))
    return None


if __name__ == "__main__":

    print("-----------------------------------------------------------------------------------------")
    print("Welcome to Snekoban!")
    print("\nTo play the game, run the following command in your terminal, where /path/to/server.py refers to the location of server.py:")
    print("$ python3 /path/to/server.py")

    print("\nAfter doing so, please navigate to http://localhost:6101 in your web browser. Enjoy the game!")
    print("-----------------------------------------------------------------------------------------")
    print("\n***** All levels of the game are designed by David W. Skinner and implemented by Anna Yang. *****")

    # ##### Sample Solution found using solve_puzzle #####

    # with open('puzzles/m1_021.json', 'r') as file:
    #     m1_021 = json.load(file)

    # level_21_sol = solve_puzzle(make_new_game(m1_021))
    # print("Sample solution for Level 21:", level_21_sol)
