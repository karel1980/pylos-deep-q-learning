from pylos import *


def test_initial_state():
    pylos = Pylos()

    assert pylos.reserve == [15, 15]
    assert pylos.current_player == 0
    assert len(pylos.layers) == 4
    assert pylos.layers[0] == [
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None],
        [None, None, None, None]
    ]
    assert pylos.layers[1] == [
        [None, None, None],
        [None, None, None],
        [None, None, None]
    ]
    assert pylos.layers[2] == [
        [None, None],
        [None, None]
    ]
    assert pylos.layers[3] == [
        [None]
    ]


def test_layer0_valid_move():
    pylos = Pylos()

    success = pylos.move_from_reserve((0, 1, 2))

    assert success == True
    assert pylos.render() == "..../..0./..../....#.../.../...#../..#."
    assert pylos.current_player == 1
    assert pylos.reserve == [14, 15]


def test_valid_upmove():
    pylos = Pylos()

    pylos.move_from_reserve((0, 0, 0))
    pylos.move_from_reserve((0, 3, 3))
    pylos.move_from_reserve((0, 0, 1))
    pylos.move_from_reserve((0, 1, 0))
    pylos.move_from_reserve((0, 1, 1))

    success = pylos.move_up((0, 3, 3), (1, 0, 0))

    assert success == True
    assert pylos.render() == "00../10../..../....#1../.../...#../..#."


def test_valid_moveup_with_0_retraction():
    pylos = setup_moveup_scenario()

    success = pylos.move_up((0, 3, 0), (1, 0, 0), [])

    assert success == True
    assert pylos.render() == "0101/0101/0101/.101#001/001/..1#../..#."


def test_valid_moveup_with_1_valid_retraction():
    pylos = setup_moveup_scenario()

    success = pylos.move_up((0, 3, 0), (1, 0, 0), [(1, 0, 0)])

    assert success == True
    assert pylos.render() == "0101/0101/0101/.101#.01/001/..1#../..#."


def test_valid_moveup_with_1_invalid_retraction_blocked_ball():
    pylos = setup_moveup_scenario()

    success = pylos.move_up((0, 3, 0), (1, 0, 0), [(0, 0, 0)])

    assert success == False


def test_valid_moveup_with_1_invalid_retraction_opponent_ball():
    pylos = setup_moveup_scenario()

    success = pylos.move_up((0, 3, 0), (1, 0, 0), [(0, 3, 1)])

    assert success == False
    assert pylos.render() == "0101/0101/0101/0101#.01/001/..1#../..#."


def test_get_moveup_locations():
    pylos = Pylos()

    fill_layer(pylos, 0)

    actual = list(pylos.get_moveup_locations((0, 0, 0)))

    print(actual)

    assert actual == [
        (1, 0, 1), (1, 0, 2),
        (1, 1, 0), (1, 1, 1), (1, 1, 2),
        (1, 2, 0), (1, 2, 1), (1, 2, 2),
    ]


def setup_moveup_scenario():
    pylos = Pylos()

    fill_layer(pylos, 0)

    pylos.move_from_reserve((1, 0, 1))
    pylos.move_from_reserve((1, 0, 2))

    pylos.move_from_reserve((1, 1, 1))
    pylos.move_from_reserve((1, 1, 2))

    pylos.move_from_reserve((1, 1, 0))
    pylos.move_from_reserve((1, 2, 2))

    assert pylos.render() == "0101/0101/0101/0101#.01/001/..1#../..#."

    return pylos


def test_layer0_invalid_move_already_occupied():
    pylos = Pylos()
    assert pylos.move_from_reserve((0, 1, 2)) == True
    assert pylos.move_from_reserve((0, 1, 2)) == False
    assert pylos.layers[0] == [[None, None, None, None], [None, None, 0, None], [None, None, None, None],
                               [None, None, None, None]]
    assert pylos.current_player == 1


def test_layer1_valid_move():
    pylos = Pylos()
    pylos.move_from_reserve((0, 1, 1))
    pylos.move_from_reserve((0, 1, 2))
    pylos.move_from_reserve((0, 2, 2))
    pylos.move_from_reserve((0, 2, 1))

    pylos.move_from_reserve((1, 1, 1))

    assert pylos.layers[0] == [[None, None, None, None], [None, 0, 1, None], [None, 1, 0, None],
                               [None, None, None, None]]
    assert pylos.layers[1] == [[None, None, None], [None, 0, None], [None, None, None]]


def test_layer1_invalid_move_insufficient_support():
    pylos = Pylos()
    pylos.move_from_reserve((0, 1, 1))
    pylos.move_from_reserve((0, 1, 2))
    pylos.move_from_reserve((0, 2, 2))

    success = pylos.move_from_reserve((1, 1, 1))

    assert success == False
    assert pylos.layers[1] == [[None, None, None], [None, None, None], [None, None, None]]


def test_valid_single_retraction():
    pylos = Pylos()
    pylos.move_from_reserve((0, 0, 0))
    pylos.move_from_reserve((0, 3, 0))

    pylos.move_from_reserve((0, 1, 0))
    pylos.move_from_reserve((0, 3, 1))

    pylos.move_from_reserve((0, 0, 1))
    pylos.move_from_reserve((0, 3, 2))

    success = pylos.move_from_reserve((0, 1, 1), [(0, 1, 0)])

    assert success == True
    assert pylos.layers[0] == [[0, 0, None, None], [None, 0, None, None], [None, None, None, None], [1, 1, 1, None]]


def test_invalid_single_retraction_no_square():
    pylos = Pylos()
    pylos.move_from_reserve((0, 0, 0))
    pylos.move_from_reserve((0, 3, 0))

    pylos.move_from_reserve((0, 1, 0))
    pylos.move_from_reserve((0, 3, 1))

    success = pylos.move_from_reserve((0, 1, 1), [(0, 1, 0)])

    assert success == False
    assert pylos.layers[0] == [[0, None, None, None], [0, None, None, None], [None, None, None, None],
                               [1, 1, None, None]]


def test_invalid_retraction_retract_opponent_ball():
    pylos = Pylos()
    pylos.move_from_reserve((0, 0, 0))
    pylos.move_from_reserve((0, 3, 0))

    pylos.move_from_reserve((0, 1, 0))
    pylos.move_from_reserve((0, 3, 1))

    pylos.move_from_reserve((0, 0, 1))
    pylos.move_from_reserve((0, 3, 2))

    success = pylos.move_from_reserve((0, 1, 1), [(0, 3, 0)])

    assert success == False
    assert pylos.layers[0] == [[0, 0, None, None], [0, None, None, None], [None, None, None, None], [1, 1, 1, None]]


def test_winner():
    pylos = Pylos()

    assert pylos.get_winner() == None

    fill_layer(pylos, 0)
    fill_layer(pylos, 1)
    fill_layer(pylos, 2)
    fill_layer(pylos, 3)

    assert pylos.get_winner() == 1


def fill_layer(pylos, layer_num):
    for row in range(4 - layer_num):
        for col in range(4 - layer_num):
            pylos.move_from_reserve((layer_num, row, col))


def test_is_valid_from_position_true_when_none():
    pylos = Pylos()

    assert pylos.is_valid_from_position(None)


def test_is_valid_from_position_true_when_own_ball():
    pylos = Pylos()

    pylos.move_from_reserve((0, 0, 0))
    pylos.move_from_reserve((0, 1, 0))

    assert pylos.is_valid_from_position((0, 0, 0))


def test_is_valid_from_position_false_when_blocked():
    pylos = Pylos()

    fill_layer(pylos, 0)

    assert pylos.is_valid_from_position((0, 0, 0))
    assert pylos.is_valid_from_position((0, 1, 0))


def test_is_valid_from_position_false_when_opponent_ball():
    pylos = Pylos()

    pylos.move_from_reserve((0, 0, 0))

    assert not pylos.is_valid_from_position((0, 0, 0))


def test_is_valid_to_position_true_when_empty():
    pylos = Pylos()

    assert pylos.is_valid_to_position(None, (0, 0, 0))


def test_is_valid_to_position_false_when_occupied():
    pylos = Pylos()

    fill_layer(pylos, 0)

    assert not pylos.is_valid_to_position((0, 0, 0), (0, 0, 0))


def test_render():
    pylos = Pylos()

    assert pylos.render() == "..../..../..../....#.../.../...#../..#."

    pylos.move_from_reserve((0, 0, 0))

    assert pylos.render() == "0.../..../..../....#.../.../...#../..#."
