import copy
import json
from typing import List, Union

from layoutgeneration.generation.execute import RegionNode, execute_strats
from layoutgeneration.layout.orientation import Orientation
from layoutgeneration.layout.region import Region, RegionType
from layoutgeneration.provider.orientation_provider import RandomOrientationProvider, SequentialOrientationProvider, \
    StochasticOrientationProvider, UniqueOrientationProvider
from layoutgeneration.provider.region_provider import SequentialRegionProvider, StochasticRegionProvider, \
    RandomRegionProvider
from layoutgeneration.strat.drunkard_walk import DrunkardsWalk
from layoutgeneration.strat.grid_placement import GridPlacement
from layoutgeneration.strat.merge_executor import merge_root
from layoutgeneration.strat.place_al import PlaceALStrat
from layoutgeneration.strat.room_placement import SimpleRoomPlacement
from layoutgeneration.strat.space_partition import BinarySpacePartitionStart


def extract_strategies(strats: List) -> List[Union[List, str]]:
    new_strats = []
    temp = []

    for strat in strats:
        if not strat == 'merge':
            temp.append(strat)
        elif not len(temp) == 0:
            new_strats.append(temp)
            temp = []
            new_strats.append('merge')

    if len(temp) > 0:
        new_strats.append(temp)

    return new_strats


def generate_from_strats(region: Region, strats: List) -> List[RegionNode]:
    trees = []
    region_node = None
    new_strats = extract_strategies(strats)

    for idx in range(len(new_strats)):
        if new_strats[idx] == "merge":
            if len(trees) == 0:
                continue
            region_node = merge_root(trees[-1])
            trees.append(region_node)
        else:
            if region_node is None:
                region_node = RegionNode(region, new_strats[idx][0][region.region_type], 0, name="Node_0")
            else:
                region_node = copy.deepcopy(trees[-1])
            trees.append(execute_strats(region_node, new_strats[idx]))
            region_node = None

    return trees


def generate_from_json(json_file: str) -> List[RegionNode]:
    # Read input json
    with open(json_file, 'r') as json_file:
        input_config = json.load(json_file)

    reg = input_config['region']
    strategies = input_config['strategies']

    region = Region(reg['x'], reg['y'], reg['width'], reg['height'], getattr(Orientation, reg['orientation']),
                    getattr(RegionType, reg['type']))

    strats_list = {'PlaceALStrat': PlaceALStrat,
                   'SimpleRoomPlacement': SimpleRoomPlacement,
                   'BinarySpacePartitionStart': BinarySpacePartitionStart,
                   'DrunkardsWalk': DrunkardsWalk,
                   'GridPlacement': GridPlacement}

    region_providers = {'RandomRegionProvider': RandomRegionProvider,
                        'SequentialRegionProvider': SequentialRegionProvider,
                        'StochasticRegionProvider': StochasticRegionProvider}

    orient_providers = {'RandomOrientationProvider': RandomOrientationProvider,
                        'SequentialOrientationProvider': SequentialOrientationProvider,
                        'StochasticOrientationProvider': StochasticOrientationProvider,
                        'UniqueOrientationProvider': UniqueOrientationProvider}

    # Build the list of strategies from the json file
    strats = []
    for layer in strategies:
        layer_strats = dict()
        for region_type, strategy in layer.items():
            # merge is not a region type, it's a property of the layer
            if region_type == "merge":
                continue
            strat_func = strats_list[strategy["name"]]
            params = strategy['args']

            if "choices" in strategy:
                params.update({"choices": [getattr(RegionType, region_type) for region_type in strategy["choices"]]})

            if "region_prov" in strategy:
                region_prov = region_providers[strategy["region_prov"]["name"]]
                region_prov_args = strategy["region_prov"]["args"]
                params.update({"region_prov": region_prov(**region_prov_args)})

            if "orient_prov" in strategy:
                orient_prov = orient_providers[strategy["orient_prov"]["name"]]
                orient_prov_args = strategy["orient_prov"]["args"]
                if "choices" in orient_prov_args:
                    orient_prov_args.update(
                        {"choices": [getattr(Orientation, region_type) for region_type in orient_prov_args["choices"]]})
                if "orientation" in orient_prov_args:
                    orient_prov_args.update({"orientation": getattr(Orientation, orient_prov_args["orientation"])})
                params.update({"orient_prov": orient_prov(**orient_prov_args)})
            layer_strats[getattr(RegionType, region_type)] = strat_func(**params)
        strats.append(layer_strats)
        if "merge" in layer and layer["merge"]:
            strats.append("merge")

    return generate_from_strats(region, strats)
