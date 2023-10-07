from typing import List
from layoutgeneration.layout.region import Region, RegionType
from layoutgeneration.strat.base_start import BaseStrat
import math

from layoutgeneration.provider.orientation_provider import OrientationProvider
from layoutgeneration.provider.region_provider import RegionProvider


class GridPlacement(BaseStrat):
    def __init__(self, cell_size: tuple, choices: List[RegionType], region_prov: RegionProvider,
                 orient_prov: OrientationProvider, keep_extra_space: bool):
        self.cell_size_x = cell_size[0]
        self.cell_size_y = cell_size[1]
        self.choices = choices
        self.picker = region_prov
        self.orientation_prov = orient_prov
        self.keep_extra_space = keep_extra_space

    def generate(self, region: Region) -> List[Region]:
        regions = []
        w = region.width
        h = region.height
        max_region = region.max_bound
        # fill the squares to the max
        # get max width
        remaining_x = w % self.cell_size_x
        fill_till_x = w - remaining_x
        # get max height
        remaining_y = h % self.cell_size_y
        fill_till_y = h - remaining_y
        if fill_till_x == 0 or fill_till_y == 0:
            return [region]
        for y in range(region.y, region.y + fill_till_y, self.cell_size_y):
            for x in range(region.x, region.x + fill_till_x, self.cell_size_x):
                region_type = self.picker.get_region(self.choices)
                regions.append(
                    Region(x, y, self.cell_size_x, self.cell_size_y, self.orientation_prov.get_orientation(), region_type))
        if self.keep_extra_space:
            if remaining_x != 0:
                regions.append(Region(max_region[0] - remaining_x, region.y, remaining_x, h,
                                      self.orientation_prov.get_orientation(), RegionType.EMPTY))
            if remaining_y != 0:
                regions.append(Region(region.x, max_region[1] - remaining_y, w, remaining_y,
                                      self.orientation_prov.get_orientation(), RegionType.EMPTY))
        else:
            nb_cells_x = fill_till_x / self.cell_size_x
            nb_cells_y = fill_till_y / self.cell_size_y
            # space_value between boxes
            space_x_min = 0 if nb_cells_x <= 1 else math.floor(remaining_x / (nb_cells_x - 1))
            # space_x = math.ceil(remaining_x / (nb_cells_x - 1))

            space_y_min = 0 if nb_cells_y == 1 else math.floor(remaining_y / (nb_cells_y - 1))
            # space_y = math.ceil(remaining_y / (nb_cells_y - 1))
            region_x_max = []
            region_y_max = []
            if remaining_x != 0 and remaining_y != 0:

                for i in range(1, len(regions)):
                    if regions[i].x == region.x:
                        regions[i].y = regions[i - 1].max_bound[1] + space_y_min

                    elif regions[i].y == region.y:
                        regions[i].x = regions[i - 1].max_bound[0] + space_x_min

                    else:
                        regions[i].x = regions[i - 1].max_bound[0] + space_x_min
                        regions[i].y = regions[i - 1].y

                    region_x_max.append(regions[i].x)
                    region_y_max.append(regions[i].y)

                # get max of x and y to get all the regions that are at the edge
                if len(regions) > 1:
                    x_max = max(region_x_max)
                    y_max = max(region_y_max)
                    # add the left space to the edge nodes to fill the region
                    for j in range(0, len(regions)):
                        if regions[j].x == x_max:
                            regions[j].x = region.max_bound[0] - self.cell_size_x

                        if regions[j].y == y_max:
                            regions[j].y = region.max_bound[1] - self.cell_size_y

            elif remaining_x != 0 and remaining_y == 0:
                for i in range(1, len(regions)):
                    if not regions[i].x == region.x:
                        regions[i].x = regions[i - 1].max_bound[0] + space_x_min

            elif remaining_x == 0 and remaining_y != 0:
                for i in range(1, len(regions)):
                    if regions[i].x == region.x:
                        regions[i].y = regions[i - 1].max_bound[1] + space_y_min
                    else:
                        regions[i].y = regions[i - 1].y

        return regions
