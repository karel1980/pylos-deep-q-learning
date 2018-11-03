import random
from collections import deque

import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Activation
from keras.optimizers import Adam


class Agent():
    def __init__(self):
        self.gamma = 0.95
        self.memory = deque([], 200)

        self.model = self.create_model()

    def choose_action(self, state):
        # TODO: restrict to valid moves!!
        return np.argmax(self.model.predict(np.array([state])))

    def create_model(self):
        model = Sequential([Dense(200, input_shape=(96,))])
        model.add(Activation('relu'))

        # Hidden layers
        model.add(Dense(200))
        model.add(Activation('relu'))
        model.add(Dense(200))
        model.add(Activation('relu'))

        model.add(Dense(31, activation='softmax'))

        optimizer = Adam()
        model.compile(optimizer, loss='mse')
        return model

    def remember(self, experiences):
        states = np.array([e[0] for e in experiences])
        actions = np.array([e[1] for e in experiences])
        next_states = np.array([e[2] for e in experiences])
        rewards = np.array([e[3] for e in experiences])
        not_done = np.array([0 if e[4] else 1 for e in experiences])

        q = self.model.predict(states)
        best_next_q = self.model.predict(next_states).max(1)

        old_q = q * np.eye(31)[actions]
        new_q = (rewards * self.gamma + not_done * best_next_q).reshape(q.shape[0], -1) * np.eye(31)[actions]

        # Q(s,a) = r + gamma * max_a(Q(s',a))
        target_q = q - old_q + new_q

        self.model.fit(states, target_q, verbose=False)
