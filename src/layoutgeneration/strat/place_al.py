import random
from typing import List, Tuple
import os
import json
from layoutgeneration.layout.orientation import Orientation
from layoutgeneration.provider.region_provider import RandomRegionProvider,SequentialRegionProvider
from layoutgeneration.strat.base_start import BaseStrat
from layoutgeneration.layout.region import Region, RegionType
from layoutgeneration.provider.orientation_provider import UniqueOrientationProvider
from layoutgeneration.strat.grid_placement import GridPlacement


class PlaceALStrat(BaseStrat):
    def __init__(self, min_width: int, max_width: int, right: bool, left: bool, empty_path_width: int = 200, max_tries: int = 10):
        """
        :param min_width: minimum width of the assembly line
        :param max_width: maximum width of the assembly line
        """
        self.max_tries = max_tries
        self.min_width = min_width
        self.max_width = max_width
        self.right = right
        self.left = left
        self.empty_path_width = empty_path_width

    def generate(self, region: Region) -> List[Region]:
        al_regions, direction = self.generate_al(region, tries=self.max_tries)
        ret = []
        for reg in al_regions:
            if reg.region_type is RegionType.EMPTY:
                regs = self.add_path(reg, direction, self.max_tries)
                for i in regs:
                    ret.append(i)
            else:
                ret.append(reg)

        return ret

    def generate_al(self, region: Region, tries=10) -> Tuple[List[Region], bool]:

        # First choose if the AL will be vertical or horizontal
        is_vertical = bool(random.getrandbits(1))
        orientations = [Orientation.UP, Orientation.DOWN] if is_vertical else [Orientation.LEFT, Orientation.RIGHT]
        max_dim = region.max_bound[0] if is_vertical else region.max_bound[1]
        # Define the position and size of the AL
        pos = random.randint(0, region.width if is_vertical else region.height)
        al_width = random.randint(self.min_width, self.max_width)
        al_width = min(al_width, max_dim - pos - (region.x if is_vertical else region.y))
        if al_width < self.min_width:
            return [region] if tries <= 0 else self.generate_al(region, tries - 1)
        # Create the AL region
        x_pos = region.x + pos if is_vertical else region.x
        y_pos = region.y if is_vertical else region.y + pos
        width = al_width if is_vertical else region.width
        height = region.height if is_vertical else al_width
        al_region = Region(x_pos, y_pos, width, height, random.choice(orientations), RegionType.ASSEMBLY_LINE)

        # Reserve space for vertical
        if is_vertical and (self.left and self.right):
            new_reg = Region(x_pos - width, y_pos, width + width + width, height, Orientation.RIGHT,
                             RegionType.ASSEMBLY_LINE)
        elif is_vertical and self.left:
            new_reg = Region(x_pos - width, y_pos, width + width, height, Orientation.RIGHT, RegionType.ASSEMBLY_LINE)
        elif is_vertical and self.right:
            new_reg = Region(x_pos, y_pos, width + width, height, Orientation.RIGHT, RegionType.ASSEMBLY_LINE)

        # Reserve space for not vertical
        if not is_vertical and (self.left and self.right):
            new_reg = Region(x_pos, y_pos - height, width, height + height + height, Orientation.RIGHT,
                             RegionType.ASSEMBLY_LINE)
        elif not is_vertical and self.left:
            new_reg = Region(x_pos, y_pos - height, width, height + height, Orientation.RIGHT, RegionType.ASSEMBLY_LINE)
        elif not is_vertical and self.right:
            new_reg = Region(x_pos, y_pos, width, height + height, Orientation.RIGHT, RegionType.ASSEMBLY_LINE)

        # Get the remaining regions
        others: List[Region] = region.subtract(new_reg, UniqueOrientationProvider(region.orientation))
        others.append(al_region)

        # get left and right materials assembly lines
        materials_region = self.add_assembly_materials(al_region, is_vertical, region)

        if len(materials_region) > 0:
            for reg in materials_region:
                others.append(reg)

        return others, is_vertical

    def add_path(self, region: Region, is_vertical, tries=10) -> List[Region]:
        orientations = [Orientation.UP, Orientation.DOWN] if is_vertical else [Orientation.LEFT, Orientation.RIGHT]
        max_dim = region.max_bound[0] if is_vertical else region.max_bound[1]
        # Define the position and size of the Path
        pos = random.randint(0, region.width if is_vertical else region.height)
        path_width = self.empty_path_width
        # Create the AL region
        x_pos = region.x + pos if is_vertical else region.x
        y_pos = region.y if is_vertical else region.y + pos
        width = path_width if is_vertical else region.width
        height = region.height if is_vertical else path_width
        path_region = Region(x_pos, y_pos, width, height, random.choice(orientations), RegionType.EMPTY_PATH)
        if is_vertical and (path_region.max_bound[0] > region.max_bound[0] or path_region.x < region.x):
            return [region] if tries <= 0 else self.add_path(region, is_vertical, tries - 1)
        elif not is_vertical and (path_region.max_bound[1] > region.max_bound[1] or path_region.y < region.y):
            return [region] if tries <= 0 else self.add_path(region, is_vertical, tries - 1)
        # Get the remaining regions
        others: List[Region] = region.subtract(path_region, UniqueOrientationProvider(region.orientation))
        # return the resulting regions
        others.append(path_region)
        return others
    def add_assembly_materials(self, reg: Region, is_vertical: bool, main_region: Region)-> List[Region]:
        ret = []
        # vertical
        if is_vertical:
            if self.right:
                assembly_materials = Region(reg.x + reg.width, reg.y, reg.width, reg.height,
                                            Orientation.LEFT, RegionType.ASSEMBLY_MATERIALS)
                if assembly_materials.max_bound[0] < main_region.max_bound[0]:
                    ret.append(assembly_materials)

            if self.left:
                assembly_materials = Region(reg.x - reg.width, reg.y, reg.width,
                                            reg.height,
                                            Orientation.RIGHT,
                                            RegionType.ASSEMBLY_MATERIALS)
                if assembly_materials.x > main_region.x:
                    ret.append(assembly_materials)
        # not vertical
        else:
            if self.right:
                assembly_materials = Region(reg.x, reg.y + reg.height, reg.width,
                                            reg.height,
                                            Orientation.UP,
                                            RegionType.ASSEMBLY_MATERIALS)
                if assembly_materials.max_bound[1] < main_region.max_bound[1]:
                    ret.append(assembly_materials)
            if self.left:
                assembly_materials = Region(reg.x, reg.y - reg.height, reg.width,
                                            reg.height,
                                            Orientation.DOWN,
                                            RegionType.ASSEMBLY_MATERIALS)
                if assembly_materials.y > main_region.y:
                    ret.append(assembly_materials)
        return ret
