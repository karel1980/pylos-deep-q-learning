class Pylos:
    def __init__(self):
        self.reserve = [15, 15]
        self.current_player = 0
        self.layers = [self.create_layer(4), self.create_layer(3), self.create_layer(2), self.create_layer(1)]

    def create_layer(self, size):
        return [[None for col in range(size)] for row in range(size)]

    def is_valid_from_position(self, from_position):
        if from_position is None:
            return True

        layer, row, col = from_position

        if self.layers[layer][row][col] != self.current_player:
            return False

        return not self.is_supporting_ball(from_position)

    def is_valid_to_position(self, from_position, to_position):
        if from_position == to_position:
            return False

        if from_position is None:
            return self.can_place_ball_at(to_position)

        if not self.can_take_ball_from(from_position):
            return False

        valid = False

        self._clear(from_position)
        if self.can_place_ball_at(to_position):
            valid = True
        self._set(from_position, self.current_player)

        return valid

    def move_from_reserve(self, to_position, retractions=[]):
        if self.reserve[self.current_player] == 0:
            print("out of balls")
            return False

        if not self.can_place_ball_at(to_position):
            print("cannot place ball at target")
            return False

        for r in retractions:
            if not self.valid_position(r):
                print("retractions invalid")
                return False

        max_retractions = 2 if self.part_of_square(to_position, self.current_player) else 0
        if len(retractions) > max_retractions:
            print("not allowed to retract")
            return False

        print("continuing with retractions", retractions, self.render())
        if not self.retractions_valid(to_position, retractions):
            return False

        print("retractions were valid")
        self.reserve[self.current_player] += len(retractions) - 1
        self._set(to_position, self.current_player)
        for r in retractions:
            self._clear(r)

        self.current_player = 1 - self.current_player

        return True

    def can_take_ball_from(self, position):
        if self._get(position) != self.current_player:
            return False

        print("is_supporting_ball", position, self.is_supporting_ball(position), self.render())
        return not self.is_supporting_ball(position)

    def _get(self, position):
        layer, row, col = position
        return self.layers[layer][row][col]

    def move_up(self, from_position, to_position, retractions=[]):
        if not self.has_current_player_ball_at(from_position):
            print("from position not occupied by current player")
            return False

        if self.is_supporting_ball(from_position):
            print("from position is supporting, cannot be moved")
            return False

        self._clear(from_position)
        self.reserve[self.current_player] += 1

        print("moved to reserve and resuming normally", self.render())
        success = self.move_from_reserve(to_position, retractions)

        if not success:
            print("normal resume failed")
            self._set(from_position, self.current_player)
            self.reserve[self.current_player] -= 1
            return False

        print("resumed normally")

        return True

    def has_current_player_ball_at(self, position):
        return self._get(position) == self.current_player

    def can_place_ball_at(self, to_position):
        if not self.is_free_position(to_position):
            print ("to_position is not free")
            return False

        if not self.support_complete(to_position):
            print ("to_position is not supported")
            return False

        return True

    def _set(self, position, value):
        layer, row, col = position
        self.layers[layer][row][col] = value

    def _clear(self, position):
        self._set(position, None)

    def valid_position(self, position):
        layer, row, col = position

        valid_layer = 0 <= layer < len(self.layers)
        if not valid_layer:
            return False

        valid_row = 0 <= row < len(self.layers[layer])
        if not valid_row:
            return False

        return 0 <= col < len(self.layers[layer])

    def is_free_position(self, position):
        return self.valid_position(position) and self._get(position) is None

    def support_complete(self, position):
        layer, row, col = position

        if layer == 0:
            return True

        return self.layers[layer - 1][row][col] is not None and self.layers[layer - 1][row + 1][col] is not None and \
               self.layers[layer - 1][row][col + 1] is not None and self.layers[layer - 1][row + 1][col + 1] is not None

    def part_of_square(self, position, player):
        self._set(position, player)
        layer_idx, row, col = position
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
        self._clear(position)

        return square

    def retractions_valid(self, to_position, retractions):
        memory = [to_position]

        self._set(to_position, self.current_player)

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

        self._clear(to_position)

        return valid

    def is_supporting_ball(self, position):
        layer_idx, row, col = position
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

    def get_all_positions(self):
        for l, layer in enumerate(self.layers):
            for r, row in enumerate(layer):
                for c in range(len(row)):
                    yield (l, r, c)

    def get_current_player_balls(self):
        for position in self.get_all_positions():
            if self._get(position) == self.current_player:
                yield position

    def can_place_balls(self):
        for position in self.get_all_positions():
            if self.can_place_ball_at(position):
                return True

    def get_moveup_locations(self, from_position):
        if not self.is_valid_from_position(from_position):
            return []

        return list(filter(lambda to_position: self.is_valid_to_position(from_position, to_position),
                      self.get_all_positions()))
