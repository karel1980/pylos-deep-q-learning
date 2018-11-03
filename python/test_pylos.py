import pylos
from pylos import Pylos, Actions, Location, MoveException
from nose.tools import assert_equal, raises


def test_initial_state():
    game = pylos.Pylos()

    assert_equal(game.actions, Actions())
    assert_equal(game.phase, pylos.PHASE_SOURCE_LOCATION)
    assert game.render() == "..../..../..../....#.../.../...#../..#."
    assert game.reserve == [15, 15]
    assert game.current_player == 0


def test_move_valid_source_location_new_state():
    game = Pylos()

    game.move(None)

    assert game.actions == Actions()
    assert game.phase == pylos.PHASE_TARGET_LOCATION
    assert game.render() == "..../..../..../....#.../.../...#../..#."
    assert game.reserve == [15, 15]
    assert game.current_player == 0


def test_fill_entire_board_winner_is_player_whose_ball_is_on_the_top():
    game = Pylos()

    fill_layer(game, 0)
    fill_layer(game, 1)
    fill_layer(game, 2)
    fill_layer(game, 3)

    assert game.game_over()
    assert game.winner == 1


def test_is_valid_move_true_when_source_is_reserve():
    game = Pylos()

    assert game.is_valid_move(None)


def test_is_valid_move_false_when_source_is_empty():
    game = Pylos()

    assert not game.is_valid_move((0, 0, 0))


def test_is_valid_move_false_when_source_is_other_player_ball():
    game = Pylos()

    play_turn(game, None, (0, 0, 0), None, None)

    assert not game.is_valid_move((0, 0, 0))


def test_is_valid_move_true_when_source_is_current_player_ball_and_possible_higher_targets():
    game = Pylos()

    play_turn(game, None, (0, 0, 0), None, None)
    play_turn(game, None, (0, 2, 2), None, None)
    play_turn(game, None, (0, 2, 3), None, None)
    play_turn(game, None, (0, 3, 2), None, None)
    play_turn(game, None, (0, 3, 3), None, None)
    play_turn(game, None, (0, 0, 3), None, None)

    assert game.is_valid_move((0, 0, 0))


def test_is_valid_move_false_when_source_is_current_player_ball_and_no_possible_higher_targets():
    game = Pylos()

    play_turn(game, None, (0, 0, 0), None, None)
    play_turn(game, None, (0, 0, 1), None, None)

    assert not game.is_valid_move((0, 0, 0))


def test_valid_turn():
    game = Pylos()

    play_turn(game, None, (0, 0, 0), None, None)

    assert game.actions == Actions()
    assert game.phase == pylos.PHASE_SOURCE_LOCATION
    assert game.render() == "0.../..../..../....#.../.../...#../..#."
    assert game.reserve == [14, 15]
    assert game.current_player == 1
    assert_equal(game.winner, None)


def test_move_game_state_when_valid_move():
    game = pylos.Pylos()
    game.move(None)

    game.move(Location(0, 0, 0))

    assert game.phase == pylos.PHASE_RETRACT1
    assert game.actions == Actions(None, Location(0, 0, 0), None, None)
    assert game.render() == "0.../..../..../....#.../.../...#../..#."
    assert game.reserve == [14, 15]
    assert game.current_player == 0


@raises(MoveException)
def test_move_throws_when_invalid_target_location():
    game = pylos.Pylos()
    game.move(None)

    game.move(Location(1, 0, 0))


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


@raises(MoveException)
def test_retract1_invalid():
    game = pylos.Pylos()
    game.move(None)
    game.move(Location(0, 0, 0))

    game.move(Location(0, 0, 0))


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


@raises(MoveException)
def test_retract2_invalid():
    game = pylos.Pylos()
    game.move(None)
    game.move(Location(0, 0, 0))
    game.move(None)

    game.move(Location(0, 0, 0))


def test_layer0_valid_move():
    game = Pylos()

    play_turn(game, None, (0, 1, 2), None, None)

    assert_equal(game.render(), "..../..0./..../....#.../.../...#../..#.")
    assert_equal(game.current_player, 1)
    assert_equal(game.reserve, [14, 15])


def test_valid_upmove():
    game = Pylos()

    play_turn(game, None, (0, 0, 0))
    assert_equal(game.render(), "0.../..../..../....#.../.../...#../..#.")

    play_turn(game, None, (0, 3, 3))
    assert_equal(game.render(), "0.../..../..../...1#.../.../...#../..#.")

    play_turn(game, None, (0, 0, 1))
    play_turn(game, None, (0, 1, 0))
    play_turn(game, None, (0, 1, 1))

    assert_equal(game.render(), "00../10../..../...1#.../.../...#../..#.")
    play_turn(game, (0, 3, 3), (1, 0, 0))

    assert_equal(game.render(), "00../10../..../....#1../.../...#../..#.")


def test_valid_move_up_with_0_retraction():
    game = setup_moveup_scenario()

    play_turn(game, (0, 3, 0), (1, 0, 0))

    assert game.render() == "0101/0101/0101/.101#001/001/..1#../..#."


def test_valid_moveup_with_1_valid_retraction():
    game = setup_moveup_scenario()

    play_turn(game, (0, 3, 0), (1, 0, 0), (1, 0, 0))

    assert game.render() == "0101/0101/0101/.101#.01/001/..1#../..#."


@raises(MoveException)
def test_valid_moveup_with_1_invalid_retraction_blocked_ball():
    game = setup_moveup_scenario()

    assert_equal(game.render(), "0101/0101/0101/0101#.01/001/..1#../..#.")
    play_turn(game, (0, 3, 0), (1, 0, 0), (0, 0, 0))


@raises(MoveException)
def test_valid_moveup_with_1_invalid_retraction_opponent_ball():
    game = setup_moveup_scenario()

    play_turn(game, (0, 3, 0), (1, 0, 0), (0, 3, 1))


def setup_moveup_scenario():
    game = Pylos()

    fill_layer(game, 0)

    play_turn(game, None, (1, 0, 1))
    play_turn(game, None, (1, 0, 2))

    play_turn(game, None, (1, 1, 1))
    play_turn(game, None, (1, 1, 2))

    play_turn(game, None, (1, 1, 0))
    play_turn(game, None, (1, 2, 2))

    assert game.render() == "0101/0101/0101/0101#.01/001/..1#../..#."

    return game


@raises(MoveException)
def test_layer0_invalid_move_already_occupied():
    game = Pylos()
    play_turn(game, None, (0, 1, 2))
    play_turn(game, None, (0, 1, 2))


def test_layer1_valid_move():
    game = Pylos()
    play_turn(game, None, (0, 1, 1))
    play_turn(game, None, (0, 1, 2))
    play_turn(game, None, (0, 2, 2))
    play_turn(game, None, (0, 2, 1))

    play_turn(game, None, (1, 1, 1))

    assert game.layers[0] == [[None, None, None, None], [None, 0, 1, None], [None, 1, 0, None],
                              [None, None, None, None]]
    assert game.layers[1] == [[None, None, None], [None, 0, None], [None, None, None]]


@raises(MoveException)
def test_layer1_invalid_move_insufficient_support():
    game = Pylos()
    play_turn(game, None, (0, 1, 1))
    play_turn(game, None, (0, 1, 2))
    play_turn(game, None, (0, 2, 2))

    play_turn(game, None, (1, 1, 1))


def test_valid_single_retraction():
    game = Pylos()
    play_turn(game, None, (0, 0, 0))
    play_turn(game, None, (0, 3, 0))

    play_turn(game, None, (0, 1, 0))
    play_turn(game, None, (0, 3, 1))

    play_turn(game, None, (0, 0, 1))
    play_turn(game, None, (0, 3, 2))

    assert_equal(game.layers[0], [[0, 0, None, None], [0, None, None, None], [None, None, None, None], [1, 1, 1, None]])
    play_turn(game, None, (0, 1, 1), (0, 1, 0))
    assert_equal(game.layers[0], [[0, 0, None, None], [None, 0, None, None], [None, None, None, None], [1, 1, 1, None]])


@raises(MoveException)
def test_invalid_single_retraction_no_square():
    game = Pylos()
    play_turn(game, None, (0, 0, 0))
    play_turn(game, None, (0, 3, 0))

    play_turn(game, None, (0, 1, 0))
    play_turn(game, None, (0, 3, 1))

    play_turn(game, None, (0, 1, 1), (0, 1, 0))


@raises(MoveException)
def test_invalid_retraction_retract_opponent_ball():
    game = Pylos()
    play_turn(game, None, (0, 0, 0))
    play_turn(game, None, (0, 3, 0))

    play_turn(game, None, (0, 1, 0))
    play_turn(game, None, (0, 3, 1))

    play_turn(game, None, (0, 0, 1))
    play_turn(game, None, (0, 3, 2))

    play_turn(game, None, (0, 1, 1), (0, 3, 0))


def test_winner_correct_when_board_full():
    game = Pylos()

    assert_equal(game.get_winner(), None)

    fill_layer(game, 0)
    fill_layer(game, 1)
    fill_layer(game, 2)
    fill_layer(game, 3)

    assert_equal(game.get_winner(), 1)


def test_winner_correct_when_current_player_no_balls():
    game = Pylos()

    assert game.get_winner() is None

    play_turn(game, None, (0, 0, 0))
    play_turn(game, None, (0, 3, 0))

    play_turn(game, None, (0, 0, 1))
    play_turn(game, None, (0, 3, 1))

    play_turn(game, None, (0, 1, 0))
    play_turn(game, None, (0, 3, 2))

    play_turn(game, None, (0, 1, 1), (0, 1, 0), (0, 1, 1))
    play_turn(game, None, (0, 3, 3))

    play_turn(game, None, (0, 0, 2))
    play_turn(game, None, (0, 0, 3))

    assert_equal(game.render(), "0001/..../..../1111#.../.../...#../..#.")

    # fill rows 2 and 3
    for row in range(1, 3):
        play_turn(game, None, (0, row, 0))
        play_turn(game, None, (0, row, 1))
        play_turn(game, None, (0, row, 2))
        play_turn(game, None, (0, row, 3))

    assert_equal(game.reserve, [8, 6])

    assert_equal(game.render(), "0001/0101/0101/1111#.../.../...#../..#.")

    # fill next layer
    fill_layer(game, 1)
    fill_layer(game, 2)

    assert_equal(game.reserve, [1, 0])
    assert_equal(game.current_player, 1)
    assert_equal(game.render(), "0001/0101/0101/1111#010/101/010#10/10#.")
    assert_equal(game.determine_winner(), 0)
    assert_equal(game.get_winner(), 0)


def fill_layer(game, layer_num):
    for row in range(4 - layer_num):
        for col in range(4 - layer_num):
            play_turn(game, None, (layer_num, row, col))


def test_is_valid_move_false_when_own_ball_but_no_valid_targets():
    game = Pylos()

    play_turn(game, None, (0, 0, 0))
    play_turn(game, None, (0, 1, 0))

    assert not game.is_valid_move((0, 0, 0))


def test_is_valid_move_false_when_blocked():
    game = Pylos()

    fill_layer(game, 0)
    fill_layer(game, 1)

    assert_equal(game.current_player, 1)
    assert not game.is_valid_move((0, 3, 3))


def test_is_valid_move_true_when_can_move_up():
    game = Pylos()

    fill_layer(game, 0)

    assert_equal(game.render(), "0101/0101/0101/0101#.../.../...#../..#.")
    assert game.is_valid_move((0, 0, 0))


def test_is_valid_move_true_when_source_is_part_of_support():
    game = Pylos()

    fill_layer(game, 0)
    fill_layer(game, 1)

    assert_equal(game.render(), "0101/0101/0101/0101#010/101/010#../..#.")
    assert not game.is_valid_move((0, 1, 0))


def test_is_valid_move_false_when_source_is_opponent_ball():
    game = Pylos()

    fill_layer(game, 0)

    assert not game.is_valid_move((0, 3, 3))


def test_render():
    game = Pylos()

    assert game.render() == "..../..../..../....#.../.../...#../..#."

    play_turn(game, None, (0, 0, 0))

    assert game.render() == "0.../..../..../....#.../.../...#../..#."


@raises(MoveException)
def test_invalid_move_target_without_support():
    game = Pylos()

    play_turn(game, None, (1, 0, 0))


def play_turn(game, source, target, retract1=None, retract2=None):
    game.move(source)
    game.move(target)
    game.move(retract1)
    game.move(retract2)
