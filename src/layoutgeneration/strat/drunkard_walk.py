import random
import numpy as np
from typing import List

from layoutgeneration.layout.region import RegionType, Region
from layoutgeneration.provider.orientation_provider import OrientationProvider
from layoutgeneration.strat.base_start import BaseStrat
from layoutgeneration.strat.merge_regions import MergeRegion
from layoutgeneration.provider.region_provider import RegionProvider


def check_location(x, y, maxw, maxh, block_size):
    return bool(maxw - block_size > x >= 0 and maxh - block_size > y >= 0)


class DrunkardsWalk(BaseStrat):
    def __init__(self, max_nb_steps: int, iterations: int, orient_prov: OrientationProvider, choices: List[RegionType], region_prov: RegionProvider,
                 block_size: int = 4):
        self.max_nb_steps = max_nb_steps
        self.iterations = iterations
        self.block_size = block_size
        self.orientation_prov = orient_prov
        self.choices = choices
        self.picker = region_prov

    def generate(self, region: Region) -> List[Region]:

        max_width = region.width
        max_height = region.height

        if self.block_size >= 2*region.width or self.block_size >= 2*region.height:
            return [region]

        arr = np.empty((max_width, max_height, 4), dtype=np.uint8)
        available = np.ones((max_width, max_height), dtype=bool)
        # arr = np.array(arr)

        for iteration in range(self.iterations):

            x = int(random.randint(0, max_width))
            y = int(random.randint(0, max_height))

            for step in range(self.max_nb_steps):
                counter = 0
                region_val = self.picker.get_region(self.choices).value
                orient_val = self.orientation_prov.get_orientation().value
                while counter <= 5:
                    old_x = x
                    old_y = y
                    x += random.randint(-1, 1) * self.block_size
                    y += random.randint(-1, 1) * self.block_size

                    while old_x == x and old_y == y:
                        x += random.randint(-1, 1) * self.block_size
                        y += random.randint(-1, 1) * self.block_size

                    flag = check_location(x, y, max_width, max_height, self.block_size)
                    if flag and available[x, y]:
                        for x_val in range(x, x + self.block_size):
                            for y_val in range(y, y + self.block_size):
                                arr[x_val, y_val, :3] = region_val
                                arr[x_val, y_val, 3] = orient_val
                                available[x_val, y_val] = False
                        counter = 0
                        break
                    else:
                        counter += 1
                        continue

                if counter >= 3:
                    break

        merger = MergeRegion()

        for i in range(len(arr)):
            for j in range(len(arr[0])):
                if available[i, j]:
                    arr[i, j, :3] = region.region_type.value
                    arr[i, j, 3] = region.orientation.value
                    available[i, j] = False

        return merger.generate(mat=arr, root=region)
