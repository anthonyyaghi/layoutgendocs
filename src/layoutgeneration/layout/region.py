from __future__ import annotations

import json
from typing import List, Tuple
from aenum import Enum, extend_enum

from layoutgeneration.layout.orientation import Orientation
from layoutgeneration.provider.orientation_provider import OrientationProvider


def get_types():
    return [r for r in list(RegionType)]


def load_region_types(json_path: str):
    with open(json_path, "r") as json_file:
        new_region_types = json.load(json_file)
    for region_type in new_region_types:
        try:
            extend_enum(RegionType, region_type["name"], region_type["color"], region_type["final"],
                        region_type["dir_path"])
        except TypeError:
            continue


class RegionType(Enum):
    def __init__(self, value, final, dir_path):
        self._value_ = value
        self._final_ = final
        self._dir_path_ = dir_path

    def __str__(self):
        return self.value

    @property
    def final(self):
        return self._final_

    @property
    def dir_path(self):
        return self._dir_path_


class Region:
    def __init__(self, x: int, y: int, width: int, height: int, orientation: Orientation, region_type: RegionType):
        """

        :param x: x coordinate of the top left corner
        :param y: y coordinate of the top left corner
        :param width: Region width
        :param height: Region height
        :param region_type: Region type
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.orientation = orientation
        self.area = width * height
        self.region_type = region_type

    def subtract(self, region: Region, orientation_prov: OrientationProvider, vertical_first: bool = True) -> List[
        Region]:
        """

        :param region: The region to subtract from this region
        :param orientation_prov: Object that provides an orientation when get_orientation() if called
        :param vertical_first: Choose if to splot vertically or horizontal first
        """
        return self._sub_vertical(region, orientation_prov) if vertical_first else self._sub_horizontal(region,
                                                                                                        orientation_prov)

    def _sub_vertical(self, region: Region, orientation_prov: OrientationProvider) -> List[Region]:
        """

        :param region: The region to subtract from this region

        Vertical first
        -------------------------
        |       |  3   |        |
        |       |------|        |
        |   1   |region|    2   |
        |       |------|        |
        |       |  4   |        |
        -------------------------
        """
        r1 = Region(self.x, self.y, region.x - self.x, self.height, orientation_prov.get_orientation(),
                    self.region_type)
        r2 = Region(region.x + region.width, self.y, self.width - r1.width - region.width, self.height,
                    orientation_prov.get_orientation(), self.region_type)
        r3 = Region(region.x, self.y, region.width, region.y - self.y, orientation_prov.get_orientation(),
                    self.region_type)
        r4 = Region(region.x, region.y + region.height, region.width, self.height - r3.height - region.height,
                    orientation_prov.get_orientation(), self.region_type)

        return list(filter(lambda r: r.area > 0, [r1, r2, r3, r4]))

    def _sub_horizontal(self, region: Region, orientation_prov: OrientationProvider) -> List[Region]:
        """

        :param region: The region to subtract from this region

        Vertical first
        -------------------------
        |          1            |
        |-------|------|--------|
        |   3   |region|    4   |
        |-------|------|--------|
        |          2            |
        -------------------------
        """
        r1 = Region(self.x, self.y, self.width, region.y - self.y, orientation_prov.get_orientation(), self.region_type)
        r2 = Region(self.x, region.y + region.height, self.width, self.height - r1.height - region.height,
                    orientation_prov.get_orientation(), self.region_type)
        r3 = Region(self.x, region.y, region.x - self.x, region.height, orientation_prov.get_orientation(),
                    self.region_type)
        r4 = Region(region.x + region.width, region.y, self.width - r3.width - region.width, region.height,
                    orientation_prov.get_orientation(), self.region_type)

        return list(filter(lambda r: r.area > 0, [r1, r2, r3, r4]))

    @property
    def min_bound(self) -> Tuple[int, int]:
        return self.x, self.y

    @property
    def max_bound(self) -> Tuple[int, int]:
        return self.x + self.width, self.y + self.height
