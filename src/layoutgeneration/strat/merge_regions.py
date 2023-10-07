from typing import List

from layoutgeneration.layout.orientation import Orientation
from layoutgeneration.layout.region import Region, get_types


def find_reg(arr, value_to_merge):
    region = {}

    if len(arr) == 0:
        return None

    i = 0
    j = 0
    for i in range(len(arr)):
        for j in range(len(arr[i])):
            if tuple(arr[i][j]) == value_to_merge:
                region["x"] = i
                region["y"] = j
                break
        else:
            continue
        break

    if len(region) == 0:
        return None

    x = region["x"]
    y = region["y"]
    while x < len(arr):
        if tuple(arr[x][y]) == value_to_merge:
            x += 1
            if x == len(arr):
                x -= 1
                break
        else:
            x -= 1
            break

    while y < len(arr[x]):
        if tuple(arr[x][y]) == value_to_merge:
            y += 1
            if y == len(arr[x]):
                y -= 1
                break
        else:
            y -= 1
            break

    for m in range(i, x + 1):
        for n in range(j, y + 1):
            if tuple(arr[m][n]) == value_to_merge:
                continue
            else:
                y = n - 1

    region["width"] = x
    region["height"] = y
    return region


class MergeRegion:

    def __init__(self):
        self.region_types = get_types()

    def find_all_regions(self, arr, orient: Orientation):
        result = []
        for region_type in self.region_types:
            while True:
                region = find_reg(arr, (*region_type.value, orient.value))

                if region is None:
                    break

                region["orient"] = orient
                region["type"] = region_type
                result.append(region)

                for i in range(region["x"], region["width"] + 1):
                    for j in range(region["y"], region["height"] + 1):
                        arr[i][j] = -1

        return result

    def generate(self, mat, root: Region) -> List[Region]:
        regions = self.find_all_regions(mat, Orientation.UP)
        regions.extend(self.find_all_regions(mat, Orientation.DOWN))
        regions.extend(self.find_all_regions(mat, Orientation.LEFT))
        regions.extend(self.find_all_regions(mat, Orientation.RIGHT))

        # to remove blank arrays: []
        regions = [x for x in regions if x]

        # create new list of regions
        new_regions = []

        for region in regions:
            new_regions.append(Region(region["x"] + root.x, region["y"] + root.y, region["width"] - region["x"] + 1,
                                      region["height"] - region["y"] + 1, region["orient"], region["type"]))
        return new_regions
