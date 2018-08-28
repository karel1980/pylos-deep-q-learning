import pylos
from pylos import Pylos, Actions, Location


def test_initial_state():
    game = pylos.Pylos()

    assert game.actions == Actions()
    assert game.phase == pylos.PHASE_SOURCE_LOCATION
    assert game.render() == "..../..../..../....#.../.../...#../..#."
    assert game.reserve == [15, 15]
    assert game.current_player == 0


def test_from_location_valid():
    game = Pylos()

    game.move(None)

    assert game.actions == Actions()
    assert game.phase == pylos.PHASE_TARGET_LOCATION
    assert game.render() == "..../..../..../....#.../.../...#../..#."
    assert game.reserve == [15, 15]
    assert game.current_player == 0


# TODO: test alternative reasons for invalid moves

def test_from_location_invalid_fallback_to_None():
    game = pylos.Pylos()

    game.move(Location(0, 0, 0))

    assert game.phase == pylos.PHASE_TARGET_LOCATION
    assert game.actions == Actions(None, None, None, None)
    assert game.render() == "..../..../..../....#.../.../...#../..#."
    assert game.reserve == [15, 15]
    assert game.current_player == 0


def test_target_location_valid():
    game = pylos.Pylos()
    game.move(None)

    game.move(Location(0, 0, 0))

    assert game.phase == pylos.PHASE_RETRACT1
    assert game.actions == Actions(None, Location(0, 0, 0), None, None)
    print(game.render())
    assert game.render() == "0.../..../..../....#.../.../...#../..#."
    assert game.reserve == [14, 15]
    assert game.current_player == 0


def test_target_location_invalid():
    game = pylos.Pylos()
    game.move(None)

    game.move(Location(1, 0, 0))

    assert game.phase == pylos.PHASE_RETRACT1
    assert game.actions == Actions(None, Location(0, 0, 0), None, None)
    assert game.render() == "0.../..../..../....#.../.../...#../..#."
    assert game.reserve == [14, 15]
    assert game.current_player == 0


def test_retract1_none():
    game = pylos.Pylos()
    game.move(None)
    game.move(Location(0, 0, 0))

    game.move(None)

    assert game.phase == pylos.PHASE_RETRACT2
    assert game.actions == Actions(None, Location(0, 0, 0), None, None)
    assert game.render() == "0.../..../..../....#.../.../...#../..#."
    assert game.reserve == [14, 15]
    assert game.current_player == 0


def test_retract1_invalid():
    game = pylos.Pylos()
    game.move(None)
    game.move(Location(0, 0, 0))

    game.move(Location(0, 0, 0))

    assert game.phase == pylos.PHASE_RETRACT2
    assert game.actions == Actions(None, Location(0, 0, 0), None, None)
    assert game.render() == "0.../..../..../....#.../.../...#../..#."
    assert game.reserve == [14, 15]
    assert game.current_player == 0


def test_retract2_valid():
    game = pylos.Pylos()
    game.move(None)
    game.move(Location(0, 0, 0))
    game.move(None)

    game.move(None)

    assert game.phase == pylos.PHASE_SOURCE_LOCATION
    assert game.actions == Actions(None, None, None, None)
    assert game.render() == "0.../..../..../....#.../.../...#../..#."
    assert game.reserve == [14, 15]
    assert game.current_player == 1


def test_retract2_invalid():
    game = pylos.Pylos()
    game.move(None)
    game.move(Location(0, 0, 0))
    game.move(None)

    game.move(Location(0, 0, 0))

    assert game.phase == pylos.PHASE_SOURCE_LOCATION
    assert game.actions == Actions(None, None, None, None)
    assert game.render() == "0.../..../..../....#.../.../...#../..#."
    assert game.reserve == [14, 15]
    assert game.current_player == 1


def test_layer0_valid_move():
    game = Pylos()

    success = game.move_from_reserve((0, 1, 2))

    assert success == True
    assert game.render() == "..../..0./..../....#.../.../...#../..#."
    assert game.current_player == 1
    assert game.reserve == [14, 15]


def test_valid_upmove():
    game = Pylos()

    game.move_from_reserve((0, 0, 0))
    game.move_from_reserve((0, 3, 3))
    game.move_from_reserve((0, 0, 1))
    game.move_from_reserve((0, 1, 0))
    game.move_from_reserve((0, 1, 1))

    print(game.render())
    assert game.render() == "00../10../..../...1#.../.../...#../..#."
    success = game.move_up((0, 3, 3), (1, 0, 0))

    print(game.render(), success)
    assert success == True
    assert game.render() == "00../10../..../....#1../.../...#../..#."


def test_valid_moveup_with_0_retraction():
    game = setup_moveup_scenario()

    success = game.move_up((0, 3, 0), (1, 0, 0), [])

    assert success == True
    assert game.render() == "0101/0101/0101/.101#001/001/..1#../..#."


def test_valid_moveup_with_1_valid_retraction():
    game = setup_moveup_scenario()

    print(game.render())
    success = game.move_up((0, 3, 0), (1, 0, 0), [(1, 0, 0)])
    print(game.render())

    assert success == True
    assert game.render() == "0101/0101/0101/.101#.01/001/..1#../..#."




def test_valid_moveup_with_1_invalid_retraction_blocked_ball():
    game = setup_moveup_scenario()

    success = game.move_up((0, 3, 0), (1, 0, 0), [(0, 0, 0)])

    assert success == False

def test_valid_moveup_with_1_invalid_retraction_opponent_ball():
    game = setup_moveup_scenario()

    print (game.render())
    success = game.move_up((0, 3, 0), (1, 0, 0), [(0, 3, 1)])
    print (game.render())

    assert success == False
    assert game.render() == "0101/0101/0101/.101#001/001/..1#../..#."


def setup_moveup_scenario():
    game = Pylos()

    fill_layer(game, 0)

    game.move_from_reserve((1, 0, 1))
    game.move_from_reserve((1, 0, 2))

    game.move_from_reserve((1, 1, 1))
    game.move_from_reserve((1, 1, 2))

    game.move_from_reserve((1, 1, 0))
    game.move_from_reserve((1, 2, 2))

    assert game.render() == "0101/0101/0101/0101#.01/001/..1#../..#."

    return game


def test_layer0_invalid_move_already_occupied():
    game = Pylos()
    assert game.move_from_reserve((0, 1, 2)) == True
    assert game.move_from_reserve((0, 1, 2)) == False
    assert game.layers[0] == [[1, None, None, None], [None, None, 0, None], [None, None, None, None], [None, None, None, None]]
    assert game.current_player == 0

#
# def test_layer1_valid_move():
#     game = Pylos()
#     game.move_from_reserve((0, 1, 1))
#     game.move_from_reserve((0, 1, 2))
#     game.move_from_reserve((0, 2, 2))
#     game.move_from_reserve((0, 2, 1))
#
#     game.move_from_reserve((1, 1, 1))
#
#     assert game.layers[0] == [[None, None, None, None], [None, 0, 1, None], [None, 1, 0, None],
#                                [None, None, None, None]]
#     assert game.layers[1] == [[None, None, None], [None, 0, None], [None, None, None]]
#
#
# def test_layer1_invalid_move_insufficient_support():
#     game = Pylos()
#     game.move_from_reserve((0, 1, 1))
#     game.move_from_reserve((0, 1, 2))
#     game.move_from_reserve((0, 2, 2))
#
#     success = game.move_from_reserve((1, 1, 1))
#
#     assert success == False
#     assert game.layers[1] == [[None, None, None], [None, None, None], [None, None, None]]
#
#
# def test_valid_single_retraction():
#     game = Pylos()
#     game.move_from_reserve((0, 0, 0))
#     game.move_from_reserve((0, 3, 0))
#
#     game.move_from_reserve((0, 1, 0))
#     game.move_from_reserve((0, 3, 1))
#
#     game.move_from_reserve((0, 0, 1))
#     game.move_from_reserve((0, 3, 2))
#
#     success = game.move_from_reserve((0, 1, 1), [(0, 1, 0)])
#
#     assert success == True
#     assert game.layers[0] == [[0, 0, None, None], [None, 0, None, None], [None, None, None, None], [1, 1, 1, None]]
#
#
# def test_invalid_single_retraction_no_square():
#     game = Pylos()
#     game.move_from_reserve((0, 0, 0))
#     game.move_from_reserve((0, 3, 0))
#
#     game.move_from_reserve((0, 1, 0))
#     game.move_from_reserve((0, 3, 1))
#
#     success = game.move_from_reserve((0, 1, 1), [(0, 1, 0)])
#
#     assert success == False
#     assert game.layers[0] == [[0, None, None, None], [0, None, None, None], [None, None, None, None],
#                                [1, 1, None, None]]
#
#
# def test_invalid_retraction_retract_opponent_ball():
#     game = Pylos()
#     game.move_from_reserve((0, 0, 0))
#     game.move_from_reserve((0, 3, 0))
#
#     game.move_from_reserve((0, 1, 0))
#     game.move_from_reserve((0, 3, 1))
#
#     game.move_from_reserve((0, 0, 1))
#     game.move_from_reserve((0, 3, 2))
#
#     success = game.move_from_reserve((0, 1, 1), [(0, 3, 0)])
#
#     assert success == False
#     assert game.layers[0] == [[0, 0, None, None], [0, None, None, None], [None, None, None, None], [1, 1, 1, None]]
#
#
# def test_winner():
#     game = Pylos()
#
#     assert game.get_winner() == None
#
#     fill_layer(game, 0)
#     fill_layer(game, 1)
#     fill_layer(game, 2)
#     fill_layer(game, 3)
#
#     assert game.get_winner() == 1
#
#
def fill_layer(game, layer_num):
    for row in range(4 - layer_num):
        for col in range(4 - layer_num):
            game.move_from_reserve((layer_num, row, col))
#
#
# def test_is_valid_from_position_true_when_none():
#     game = Pylos()
#
#     assert game.is_valid_from_position(None)
#
#
# def test_is_valid_from_position_true_when_own_ball():
#     game = Pylos()
#
#     game.move_from_reserve((0, 0, 0))
#     game.move_from_reserve((0, 1, 0))
#
#     assert game.is_valid_from_position((0, 0, 0))
#
#
# def test_is_valid_from_position_false_when_blocked():
#     game = Pylos()
#
#     fill_layer(game, 0)
#
#     assert game.is_valid_from_position((0, 0, 0))
#     assert game.is_valid_from_position((0, 1, 0))
#
#
# def test_is_valid_from_position_false_when_opponent_ball():
#     game = Pylos()
#
#     game.move_from_reserve((0, 0, 0))
#
#     assert not game.is_valid_from_position((0, 0, 0))
#
#
# def test_is_valid_to_position_true_when_empty():
#     game = Pylos()
#
#     assert game.is_valid_to_position(None, (0, 0, 0))
#
#
# def test_is_valid_to_position_false_when_occupied():
#     game = Pylos()
#
#     fill_layer(game, 0)
#
#     assert not game.is_valid_to_position((0, 0, 0), (0, 0, 0))
#
#
# def test_render():
#     game = Pylos()
#
#     assert game.render() == "..../..../..../....#.../.../...#../..#."
#
#     game.move_from_reserve((0, 0, 0))
#
#     assert game.render() == "0.../..../..../....#.../.../...#../..#."
#
#
# def test_invalid_move_put_on_top():
#     game = Pylos()
#
#     success = game.move_from_reserve((3, 0, 0))
#
#     assert not success
