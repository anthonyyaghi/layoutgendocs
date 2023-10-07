from abc import ABC, abstractmethod
from typing import List

from layoutgeneration.layout.region import Region


class BaseStrat(ABC):
    @abstractmethod
    def generate(self, region: Region) -> List[Region]:
        """

        :param region: Region in which to generate other regions

        returns a set of regions contain in the input region.
        """
        pass
