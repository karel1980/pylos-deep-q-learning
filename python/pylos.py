from typing import Iterable, List

PHASE_SOURCE_LOCATION = 0
PHASE_TARGET_LOCATION = 1
PHASE_RETRACT1 = 2
PHASE_RETRACT2 = 3


class MoveException(Exception):
    pass


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

    def __repr__(self):
        return str(self)

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


def tuple_to_location(tup):
    if tup is None:
        return None

    layer, row, col = tup
    return Location(layer, row, col)


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
    actions: Actions
    current_player: int
    reserve: List[int]
    phase: int
    allow_retractions: bool
    winner: int

    def __init__(self):
        self.layers: List[List[List[int]]] = [
            self.create_layer(4),
            self.create_layer(3),
            self.create_layer(2),
            self.create_layer(1)]

        self.current_player = 0
        self.reserve: List[int] = [15, 15]
        self.layers: List[List[List[int]]]
        self.phase: int = PHASE_SOURCE_LOCATION
        self.allow_retractions = False
        self.winner = None
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
        location = tuple_to_location(location)

        self.validate_move(location)

        if self.phase == PHASE_SOURCE_LOCATION:
            self.handle_source_move(location)

        elif self.phase == PHASE_TARGET_LOCATION:
            self.handle_target_move(location)

        elif self.phase == PHASE_RETRACT1:
            self.handle_retract1(location)

        elif self.phase == PHASE_RETRACT2:
            self.handle_retract2(location)
            self.winner = self.determine_winner()

    def validate_move(self, location):
        location = tuple_to_location(location)

        if self.game_over():
            raise MoveException('game is over')

        if self.phase == PHASE_SOURCE_LOCATION:
            self.validate_source_move(location)

        elif self.phase == PHASE_TARGET_LOCATION:
            self.validate_target_move(location)

        else:
            self.validate_retract_move(location)

    def validate_source_move(self, location):
        if location is None:
            return

        if self._get(location) is None:
            raise MoveException('source location contains no ball')

        if self._get(location) != self.current_player:
            raise MoveException('you can only move your own balls')

        self.validate_ball_at_location_can_be_moved_up(location)

    def is_valid_move(self, location):
        location = tuple_to_location(location)

        try:
            self.validate_move(location)
            return True
        except MoveException:
            return False

    def validate_ball_at_location_can_be_moved_up(self, location: Location):
        if self.has_ball_directly_above(location):
            raise MoveException('ball is blocked by higher ball', location)

        supported_free_locations = self.get_supported_free_locations()
        higher_targets = list(filter(lambda l: l[0] > location[0], supported_free_locations))

        for target in higher_targets:
            if not location.is_directly_below(target):
                return

        raise MoveException('there are no possible targets for source location', location)

    def get_supported_free_locations(self):
        return filter(lambda l: self.has_occupied_square_below(l), self.get_free_locations())

    def game_over(self):
        return self.winner is not None

    def has_occupied_square_below(self, location: Location):
        layer, row, col = location
        if layer == 0:
            return True
        return self._get(Location(layer - 1, row, col)) is not None and \
               self._get(Location(layer - 1, row, col + 1)) is not None and \
               self._get(Location(layer - 1, row + 1, col)) is not None and \
               self._get(Location(layer - 1, row + 1, col + 1)) is not None

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
        for source in filter(lambda ball: not self.has_ball_directly_above(ball), self.get_current_player_balls()):
            for target in filter(lambda location: self.is_free_location(location), self.get_all_locations()):
                if not source.is_directly_below(target):
                    return None

        # current player has no valid moves left -> lose
        return 1 - self.current_player

    def handle_source_move(self, source: Location):
        self.actions.source = source
        if source is not None:
            self.reserve[self.current_player] -= 1
            self._clear(source)
        self.phase = PHASE_TARGET_LOCATION

        return source

    def handle_target_move(self, target):
        self.actions.target = target
        self._set(target, self.current_player)
        self.reserve[self.current_player] -= 1
        self.phase = PHASE_RETRACT1
        if self.is_part_of_square_belonging_to_same_player(target, self.current_player):
            self.allow_retractions = True

        return target

    def all_locations(self):
        for l in range(len(self.layers)):
            for r in range(len(self.layers[l])):
                for c in range(len(self.layers[l][r])):
                    yield Location(l, r, c)

    def handle_retract1(self, location):
        self._do_retract(location)
        self.phase = PHASE_RETRACT2

    def handle_retract2(self, location):
        self._do_retract(location)
        self.initialise_turn()
        self.current_player = 1 - self.current_player

    def _do_retract(self, location):
        if location is None:
            return

        self._clear(location)
        self.reserve[self.current_player] += 1

        self.actions.retract1 = location
        return

    def validate_retract_move(self, location):
        if location is None:
            return

        if not self.allow_retractions:
            raise MoveException('retractions are not allowed because you did just create a square')

        if self._get(location) != self.current_player:
            raise MoveException('you can only retract your own balls')

        if self.has_ball_directly_above(location):
            raise MoveException('retraction not possible when there are balls on top of location')

    def validate_target_move(self, target):
        if target is None:
            raise MoveException('target must not be None')

        if self._get(target) is not None:
            raise MoveException('target is not empty')

        if not self.is_fully_supported(target):
            raise MoveException('target location is not fully supported')

        if self.actions.source is not None:
            if self.actions.source.is_directly_below(target):
                raise MoveException('target location is above source location')

        return True

    def _get(self, location):
        layer, row, col = location
        return self.layers[layer][row][col]

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

    def is_fully_supported(self, location):
        layer, row, col = location

        if layer == 0:
            return True

        return self.layers[layer - 1][row][col] is not None and self.layers[layer - 1][row + 1][col] is not None and \
               self.layers[layer - 1][row][col + 1] is not None and self.layers[layer - 1][row + 1][col + 1] is not None

    def is_part_of_square_belonging_to_same_player(self, location, player):
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

    def has_ball_directly_above(self, location):
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

    def get_free_locations(self) -> Iterable[Location]:
        return filter(lambda loc: self._get(loc) is None, self.get_all_locations())

    def get_current_player_balls(self) -> Iterable[Location]:
        for location in self.get_all_locations():
            if self._get(location) == self.current_player:
                yield location
