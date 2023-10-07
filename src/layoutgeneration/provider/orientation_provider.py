import random
from abc import ABC, abstractmethod
from typing import List
import numpy as np

from layoutgeneration.layout.orientation import Orientation


class OrientationProvider(ABC):
    @abstractmethod
    def get_orientation(self) -> Orientation:
        pass


class UniqueOrientationProvider(OrientationProvider):
    def __init__(self, orientation: Orientation):
        self.orientation = orientation

    def get_orientation(self) -> Orientation:
        return self.orientation


class RandomOrientationProvider(OrientationProvider):
    def __init__(self, choices: List[Orientation]):
        self.choices = choices

    def get_orientation(self) -> Orientation:
        return random.choice(self.choices)


class SequentialOrientationProvider(OrientationProvider):
    def __init__(self, choices: List[Orientation]):
        self.choices = choices
        self.counter = 0

    def get_orientation(self) -> Orientation:
        orientation = self.choices[self.counter]
        self.counter = (self.counter + 1) % len(self.choices)
        return orientation


class StochasticOrientationProvider(OrientationProvider):
    def __init__(self, probabilities: List[float], choices: List[Orientation]):
        assert len(probabilities) == len(choices), "probabilities and choices are of different sizes"
        self.probabilities = probabilities
        self.choices = choices

    def get_orientation(self) -> Orientation:
        return np.random.choice(self.choices, p=self.probabilities)
