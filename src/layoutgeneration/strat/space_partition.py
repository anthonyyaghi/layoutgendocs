import random
from queue import Queue
from typing import List

from layoutgeneration.strat.base_start import BaseStrat
from layoutgeneration.layout.region import Region, RegionType
from layoutgeneration.provider.orientation_provider import OrientationProvider
from layoutgeneration.provider.region_provider import RegionProvider


class BinarySpacePartitionStart(BaseStrat):
    def __init__(self, nb_cuts: int, min_dimension: int, choices: List[RegionType], region_prov: RegionProvider,
                 orient_prov: OrientationProvider):
        self.min_dimension = min_dimension
        self.nb_cuts = nb_cuts
        self.choices = choices
        self.picker = region_prov
        self.orientation_prov = orient_prov

    def generate(self, region: Region) -> List[Region]:
        regions = []

        q = Queue()
        q.put((region, self.nb_cuts))

        counter = 0

        while not q.empty():
            region, cuts = q.get()

            if region.width < self.min_dimension or region.height < self.min_dimension:
                if not region.area == 0:
                    regions.append(region)
            elif cuts == 0:
                regions.append(region)
            else:
                # choose cut direction
                if random.uniform(0, 1) >= 1 - (self.nb_cuts - counter) / self.nb_cuts:
                    vertical = bool(random.getrandbits(1))
                    cut_pos = random.randint(self.min_dimension, region.width if vertical else region.height)
                    cut_pos += region.x if vertical else region.y
                    # Define first region
                    r1_x = region.x
                    r1_y = region.y
                    r1_w = (cut_pos - region.x) if vertical else region.width
                    r1_h = region.height if vertical else (cut_pos - region.y)
                    # Define second region
                    r2_x = cut_pos if vertical else region.x
                    r2_y = region.y if vertical else cut_pos
                    r2_w = (region.max_bound[0] - cut_pos) if vertical else region.width
                    r2_h = region.height if vertical else (region.max_bound[1] - cut_pos)
                    # Create the regions
                    region_type = self.picker.get_region(self.choices)
                    q.put((Region(r1_x, r1_y, r1_w, r1_h, self.orientation_prov.get_orientation(), region_type),
                           cuts - 1))
                    region_type = self.picker.get_region(self.choices)
                    q.put((Region(r2_x, r2_y, r2_w, r2_h, self.orientation_prov.get_orientation(), region_type),
                           cuts - 1))
                    counter += 1
                else:
                    counter = self.nb_cuts + 1
                    if not region.area == 0:
                        regions.append(region)
        return regions
