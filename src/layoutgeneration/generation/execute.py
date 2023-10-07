from queue import Queue
from typing import List, Dict

from layoutgeneration.layout.region import Region, RegionType
from layoutgeneration.strat.base_start import BaseStrat
from layoutgeneration.treeplotter.tree import Node


class RegionNode(Node):
    def __init__(self, region: Region, strategy: BaseStrat, depth, **kwargs):
        super().__init__(**kwargs)
        self.region = region
        self.strategy = strategy
        self.depth = depth


def execute_strats(root: RegionNode, starts: List[Dict[RegionType, BaseStrat]]) -> RegionNode:
    """

    :param root: The initial region to applying generation strategies on.
    :param starts: The size of this list determines the depth of the final tree. Each entry in the list is a dictionary
    specifying the strategy to be used on at each tree level and for each type of regions
    """

    q = Queue()

    if root.has_children:
        for child in root.children:
            try:
                child.strategy = starts[0][child.region.region_type]
                q.put(child)
            except:
                child.strategy = None
                q.put(child)
        if starts[0] is not None:
            starts.insert(0, None)
    else:
        q.put(root)

    while not q.empty():
        node: RegionNode = q.get()
        # generate the children of this node if we didn't reach the last depth in the tree
        if node.depth >= len(starts) or node.strategy is None:
            continue
        regions: List[Region] = node.strategy.generate(node.region)
        for idx, region in enumerate(regions):
            strategy = None
            for i in range(node.depth + 1, len(starts)):
                if region.region_type in starts[i]:
                    strategy = starts[i][region.region_type]
                    break
            child_node = RegionNode(region, strategy, node.depth + 1, name=f"{node.name}{idx}")
            node.add_child(child_node)
            q.put(child_node)

    return root