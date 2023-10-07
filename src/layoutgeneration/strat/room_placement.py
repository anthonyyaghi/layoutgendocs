import random
from queue import Queue
from typing import List

from layoutgeneration.strat.base_start import BaseStrat
from layoutgeneration.layout.region import Region, RegionType
from layoutgeneration.provider.orientation_provider import OrientationProvider, UniqueOrientationProvider
from layoutgeneration.provider.region_provider import RegionProvider


class SimpleRoomPlacement(BaseStrat):
    def __init__(self, min_width: int, min_height: int, max_width: int, max_height: int, max_num_rooms: int,
                 choices: List[RegionType], region_prov: RegionProvider, orient_prov: OrientationProvider):
        self.min_width = min_width
        self.min_height = min_height
        self.max_width = max_width
        self.max_height = max_height
        self.max_num_room = max_num_rooms
        self.choices = choices
        self.picker = region_prov
        self.orientation_prov = orient_prov

    def generate(self, region: Region) -> List[Region]:
        regions = []
        room = 0

        q = Queue()
        q.put(region)

        while not q.empty() and room < self.max_num_room:
            reg = q.get()

            count = 0
            x = int(random.uniform(reg.min_bound[0], reg.max_bound[0]))
            y = int(random.uniform(reg.min_bound[1], reg.max_bound[1]))
            while (reg.max_bound[0] <= self.min_width + x or reg.max_bound[1] <= self.min_height + y) and count < 3:
                x = int(random.uniform(reg.min_bound[0], reg.max_bound[0]))
                y = int(random.uniform(reg.min_bound[1], reg.max_bound[1]))
                count += 1

            if count == 3:
                regions.append(reg)
                continue
            else:
                w = int(random.uniform(self.min_width, self.max_width))
                h = int(random.uniform(self.min_height, self.max_height))

                while x + w > reg.max_bound[0]:
                    w = int(random.uniform(self.min_width, self.max_width))
                while y + h > reg.max_bound[1]:
                    h = int(random.uniform(self.min_height, self.max_height))

                region_type = self.picker.get_region(self.choices)

                new_reg = Region(x, y, w, h, self.orientation_prov.get_orientation(), region_type)
                regions.append(new_reg)
                subs = reg.subtract(new_reg, UniqueOrientationProvider(reg.orientation))

                for r in subs:
                    q.put(r)

                room += 1

        while not q.empty():
            regions.append(q.get())

        return regions
