import random
import numpy as np
from typing import List
from abc import ABC, abstractmethod

from layoutgeneration.layout.region import RegionType


class RegionProvider(ABC):
    @abstractmethod
    def get_region(self, choices: List[RegionType]) -> RegionType:
        pass


class RandomRegionProvider(RegionProvider):
    def get_region(self, choices: List[RegionType]) -> RegionType:
        return random.choice(choices)


class SequentialRegionProvider(RegionProvider):
    def __init__(self):
        self.counter = 0

    def get_region(self, choices: List[RegionType]) -> RegionType:
        choice = choices[self.counter % len(choices)]
        self.counter += 1
        return choice


class StochasticRegionProvider(RegionProvider):
    def __init__(self, probabilities: List):
        self.probabilities = probabilities

    def get_region(self, choices: List[RegionType]) -> RegionType:
        return np.random.choice(choices, p=self.probabilities)
