from itertools import chain

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
        return self.layer, self.row, self.col == other.layer, other.row, other.col

    def __iter__(self):
        return [self.layer, self.row, self.col].__iter__()

    def __str__(self):
        return "location(%d, %d, %d)" % (self.layer, self.row, self.col)


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
    phase: int
    actions: Actions
    allow_retractions: bool

    def __init__(self):
        self.reserve = [15, 15]
        self.current_player = 0
        self.layers: List[Layer] = [self.create_layer(4), self.create_layer(3), self.create_layer(2),
                                    self.create_layer(1)]
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
        if self.phase == PHASE_SOURCE_LOCATION:
            return self.handle_source_move(location)

        if self.phase == PHASE_TARGET_LOCATION:
            return self.handle_target_move(location)

        if self.phase == PHASE_RETRACT1:
            return self.handle_retract1(location)

        if self.phase == PHASE_RETRACT2:
            return self.handle_retract2(location)

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
        print("retracting", location)
        if location is not None:
            if not self.is_valid_retract(location):
                print("retraction", location, " is not valid")
                location = None

        if location is not None:
            self._clear(location)
            self.reserve[self.current_player] += 1

        self.actions.retract1 = location
        return location

    def is_valid_retract(self, location):
        return self._get(location) == self.current_player and self.allow_retractions and not self.is_supporting_ball(location)

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

        if self.actions.source is None:
            return self.can_place_ball_at(target)

        return self.can_place_ball_at(target)

    def move_from_reserve(self, to_location, retractions=[]):
        r1 = None if len(retractions) < 1 else retractions[0]
        r2 = None if len(retractions) < 2 else retractions[1]
        return self.play_turn(None, to_location, None, None)

    def play_turn(self, source, target, retract1, retract2):
        print("playing turn", source, target, retract1, retract2)
        actual_source = self.move(source)
        actual_target = self.move(target)
        actual_retract1 = self.move(retract1)
        actual_retract2 = self.move(retract2)

        print("done playing turn", source, target, retract1, retract2)
        print("done playing turn", actual_source, actual_target, actual_retract1, actual_retract2)
        return (source, target, retract1, retract2) == (actual_source, actual_target, actual_retract1, actual_retract2)

    def can_take_ball_from(self, location):
        if self._get(location) != self.current_player:
            return False

        return not self.is_supporting_ball(location)

    def _get(self, location):
        layer, row, col = location
        return self.layers[layer][row][col]

    def move_up(self, from_location, to_location, retractions=[]):
        r1 = None if len(retractions) < 1 else retractions[0]
        r2 = None if len(retractions) < 2 else retractions[1]
        return self.play_turn(from_location, to_location, r1, r2)

    def has_current_player_ball_at(self, location):
        return self._get(location) == self.current_player

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

    def retractions_valid(self, to_location, retractions):
        memory = [to_location]

        self._set(to_location, self.current_player)

        # check validity
        valid = True
        for r in retractions:
            if self.can_take_ball_from(r):
                self._clear(r)
                memory.append(r)
            else:
                valid = False

        # revert changes
        for r in memory:
            self._set(r, self.current_player)

        self._clear(to_location)

        return valid

    def is_supporting_ball(self, location):
        layer_idx, row, col = location
        if layer_idx + 1 >= len(self.layers):  # top layer can never support anything
            return False
        next_layer = self.layers[layer_idx + 1]
        rows = len(next_layer)
        cols = len(next_layer[0])

        for r in range(max(0, row - 1), min(row + 1, rows)):
            for c in range(max(0, col - 1), min(col + 1, cols)):
                if next_layer[r][c] is None:
                    return False
        return True

    def get_winner(self):
        # you lose if you can't move any balls (no reserve and no balls can be moved up
        if self.reserve[self.current_player] > 0:
            return None

        if self.current_player_has_free_balls() and self.can_place_balls():
            return None

        return 1 - self.current_player

    def render(self) -> str:
        return "#".join(["/".join(["".join(["." if c == None else str(c) for c in row]) for row in layer]) for layer in
                         self.layers])

    def current_player_has_free_balls(self):
        for ball in self.get_current_player_balls():
            if not self.is_supporting_ball(ball):
                return True

        return False

    def get_all_locations(self):
        for l, layer in enumerate(self.layers):
            for r, row in enumerate(layer):
                for c in range(len(row)):
                    yield (l, r, c)

    def get_current_player_balls(self):
        for location in self.get_all_locations():
            if self._get(location) == self.current_player:
                yield location

    def can_place_balls(self):
        for location in self.get_all_locations():
            if self.can_place_ball_at(location):
                return True

    def get_moveup_locations(self, from_location):
        if not self.is_valid_source(from_location):
            return []

        return list(filter(lambda to_location: self.is_valid_target(from_location, to_location),
                           self.get_all_locations()))
