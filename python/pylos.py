from typing import Iterable, List

PHASE_SOURCE_LOCATION = 0
PHASE_TARGET_LOCATION = 1
PHASE_RETRACT1 = 2
PHASE_RETRACT2 = 3

class Location:
    layer: int
    row: int
    col: int

    def __init__(self, layer, row, col):
        self.layer = layer
        self.row = row
        self.col = col

    def __eq__(self, other):
        if other is None:
            return False
        return (self.layer, self.row, self.col) == (other.layer, other.row, other.col)

    def __iter__(self):
        return (self.layer, self.row, self.col).__iter__()

    def __str__(self):
        return "location(%d, %d, %d)" % (self.layer, self.row, self.col)

    def is_directly_below(self, other):
        return (self.layer + 1 == other.layer) and (self.row in range(other.row - 1, other.row + 2)) and (
                self.col in range(other.col - 1, other.col + 2))

    def __getitem__(self, idx):
        if idx == 0:
            return self.layer
        if idx == 1:
            return self.row
        if idx == 2:
            return self.col

class Actions:
    source: Location
    target: Location
    retract1: Location
    retract2: Location

    def __init__(self, source=None, target=None, retract1=None, retract2=None):
        self.source = source
        self.target = target
        self.retract1 = retract1
        self.retract2 = retract2

    def __eq__(self, other):
        return self.source == other.source and self.target == other.target and self.retract1 == other.retract1 and self.retract1 == other.retract1

    def __str__(self):
        return "actions(%s, %s, %s, %s)" % (self.source, self.target, self.retract1, self.retract2)


class Pylos:

    def __init__(self):
        self.layers: List[Layer] = [self.create_layer(4), self.create_layer(3), self.create_layer(2),
                                    self.create_layer(1)]

        self.current_player: int = 0
        self.reserve: List[int] = [15, 15]
        self.layers: List[List[List[int]]]
        self.phase: int = PHASE_SOURCE_LOCATION
        self.actions: Actions
        self.allow_retractions: bool
        self.winner: int = None
        self.initialise_turn()

    def state(self):
        return self.layers, self.phase, self.actions

    def create_layer(self, size):
        return [[None for _ in range(size)] for _ in range(size)]

    def initialise_turn(self):
        self.phase = PHASE_SOURCE_LOCATION
        self.actions = Actions()
        self.allow_retractions = False

    def move(self, location=None):
        if self.winner is not None:
            return None

        if self.phase == PHASE_SOURCE_LOCATION:
            return self.handle_source_move(location)

        if self.phase == PHASE_TARGET_LOCATION:
            return self.handle_target_move(location)

        if self.phase == PHASE_RETRACT1:
            return self.handle_retract1(location)

        if self.phase == PHASE_RETRACT2:
            result = self.handle_retract2(location)
            self.winner = self.determine_winner()
            return result

    def determine_winner(self):
        # this is determined after the last move of a turn.
        # the current_player is already swapped.

        # then the top ball is set, that is the winner's ball
        if self._get(Location(3, 0, 0)) is not None:
            return self._get(Location(3, 0, 0))

        # as long as current player has balls left he's not dead
        if self.reserve[self.current_player] > 0:
            return None

        # current player has no balls left -> can only try to move ball up
        # check if player can move ball up
        for source in filter(lambda ball: not self.is_supporting_ball(ball), self.get_current_player_balls()):
            for target in filter(lambda location: self.is_free_location(location), self.get_all_locations()):
                if not source.is_directly_below(target):
                    return None

        # current player has no valid moves left -> lose
        return 1 - self.current_player

    def handle_source_move(self, source: Location):
        if not self.is_valid_source(source):
            source = self.generate_valid_source()

        self.actions.source = source
        if source is not None:
            self.reserve[self.current_player] -= 1
            self._clear(source)
        self.phase = PHASE_TARGET_LOCATION

        return source

    def handle_target_move(self, target):
        if not self.is_valid_target(target):
            target = self.generate_valid_target()

        self.actions.target = target
        self._set(target, self.current_player)
        self.reserve[self.current_player] -= 1
        self.phase = PHASE_RETRACT1
        if self.part_of_square(target, self.current_player):
            self.allow_retractions = True

        return target

    def generate_valid_source(self):
        if self.reserve[self.current_player] > 0:
            return None

        return next(filter(lambda location: self.is_valid_source(location), self.all_locations()))

    def generate_valid_target(self):
        return next(filter(lambda location: self.is_valid_target(location), self.all_locations()))

    def all_locations(self):
        for l in range(len(self.layers)):
            for r in range(len(self.layers[l])):
                for c in range(len(self.layers[l][r])):
                    yield Location(l, r, c)

    def handle_retract1(self, location):
        self.phase = PHASE_RETRACT2
        return self._do_retract(location)

    def handle_retract2(self, location):
        location = self._do_retract(location)
        self.initialise_turn()
        self.current_player = 1 - self.current_player
        return location

    def _do_retract(self, location):
        if location is None:
            return None

        if not self.is_valid_retract(location):
            return None

        self._clear(location)
        self.reserve[self.current_player] += 1

        self.actions.retract1 = location
        return location

    def is_valid_retract(self, location):
        if not self.allow_retractions:
            return False

        return self._get(location) == self.current_player and not self.is_supporting_ball(location)

    def is_valid_source(self, from_location):
        if from_location is None and self.reserve[self.current_player] > 0:
            return True

        layer, row, col = from_location

        if self.layers[layer][row][col] != self.current_player:
            return False

        return not self.is_supporting_ball(from_location)

    def is_valid_target(self, target):
        if self.actions.source == target:
            return False

        return self.can_place_ball_at(target)

    def move_from_reserve(self, to_location, retractions=[]):
        r1 = None if len(retractions) < 1 else retractions[0]
        r2 = None if len(retractions) < 2 else retractions[1]
        return self.play_turn(None, to_location, r1, r2)

    def play_turn(self, source, target, retract1, retract2):
        source = None if source is None else Location(source[0], source[1], source[2])
        target = None if target is None else Location(target[0], target[1], target[2])
        retract1 = None if retract1 is None else Location(retract1[0], retract1[1], retract1[2])
        retract2 = None if retract2 is None else Location(retract2[0], retract2[1], retract2[2])
        actual_source = self.move(source)
        actual_target = self.move(target)
        actual_retract1 = self.move(retract1)
        actual_retract2 = self.move(retract2)

        return (source, target, retract1, retract2) == (actual_source, actual_target, actual_retract1, actual_retract2)

    def _get(self, location):
        layer, row, col = location
        return self.layers[layer][row][col]

    def move_up(self, source, target, retractions=[]):
        r1 = None if len(retractions) < 1 else retractions[0]
        r2 = None if len(retractions) < 2 else retractions[1]
        return self.play_turn(source, target, r1, r2)

    def can_place_ball_at(self, to_location):
        if not self.is_free_location(to_location):
            return False

        if not self.support_complete(to_location):
            return False

        return True

    def _set(self, location, value):
        layer, row, col = location
        self.layers[layer][row][col] = value

    def _clear(self, location):
        self._set(location, None)

    def valid_location(self, location):
        layer, row, col = location

        valid_layer = 0 <= layer < len(self.layers)
        if not valid_layer:
            return False

        valid_row = 0 <= row < len(self.layers[layer])
        if not valid_row:
            return False

        return 0 <= col < len(self.layers[layer])

    def is_free_location(self, location):
        return self.valid_location(location) and self._get(location) is None

    def support_complete(self, location):
        layer, row, col = location

        if layer == 0:
            return True

        return self.layers[layer - 1][row][col] is not None and self.layers[layer - 1][row + 1][col] is not None and \
               self.layers[layer - 1][row][col + 1] is not None and self.layers[layer - 1][row + 1][col + 1] is not None

    def part_of_square(self, location, player):
        layer_idx, row, col = location
        layer = self.layers[layer_idx]
        rows = len(layer)
        cols = len(layer[0])

        square = False
        for r in range(min([0, row - 1]), max([row, rows - 2])):
            for c in range(min([0, col - 1]), max([col, cols - 2])):
                pos1 = self._get((layer_idx, r, c))
                pos2 = self._get((layer_idx, r, c + 1))
                pos3 = self._get((layer_idx, r + 1, c))
                pos4 = self._get((layer_idx, r + 1, c + 1))
                if pos1 == pos2 == pos3 == pos4 == player:
                    square = True

        return square

    def is_supporting_ball(self, location):
        layer_idx, row, col = location
        if layer_idx + 1 >= len(self.layers):  # top layer can never support anything
            return False
        next_layer = self.layers[layer_idx + 1]
        rows = len(next_layer)
        cols = len(next_layer[0])

        for r in range(max(0, row - 1), min(row + 1, rows)):
            for c in range(max(0, col - 1), min(col + 1, cols)):
                if next_layer[r][c] is not None:
                    return True
        return False

    def get_winner(self):
        return self.winner

    def render(self) -> str:
        return "#".join(["/".join(["".join(["." if c is None else str(c) for c in row]) for row in layer]) for layer in
                         self.layers])

    def get_all_locations(self) -> Iterable[Location]:
        for l, layer in enumerate(self.layers):
            for r, row in enumerate(layer):
                for c in range(len(row)):
                    yield Location(l, r, c)

    def get_current_player_balls(self) -> Iterable[Location]:
        for location in self.get_all_locations():
            if self._get(location) == self.current_player:
                yield location

