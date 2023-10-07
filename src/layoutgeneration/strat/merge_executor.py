from typing import List
import numpy as np

from layoutgeneration.generation.execute import RegionNode
from layoutgeneration.strat.merge_regions import MergeRegion


def extract_root_array(node: RegionNode, finals: List):
    """
    :param node: Node in a tree
    :param finals: List of the final nodes; not to be merged

    Will return an array version of the root node of type RegionType
    """
    # Base case
    if not node.has_children:
        img = np.zeros((node.region.width, node.region.height, 4), np.uint8)
        img[:, :, :3] = node.region.region_type.value
        img[:, :, 3] = node.region.orientation.value
        node.value = img
        node.image = ""
        return
    # Generate the images for the children
    for child in node.children:
        extract_root_array(child, finals)
    # Generate the node image a combination of the children images
    img = np.zeros((node.region.width, node.region.height, 4), np.uint8)
    for child in node.children:
        min_x, min_y = child.region.min_bound
        max_x, max_y = child.region.max_bound
        min_x -= node.region.x
        min_y -= node.region.y
        max_x -= node.region.x
        max_y -= node.region.y

        if not child.region.region_type.final:
            child_img = child.value
        else:
            child_img = np.zeros(4, dtype=np.uint8)
            finals.append(child)

        img[min_x:max_x, min_y:max_y] = child_img
    node.value = img
    node.image = ""
    return img, finals


def merge_root(region_node: RegionNode) -> RegionNode:
    root = RegionNode(region_node.region, None, 0, name="Node_0")
    finals = []
    root_array, finals = extract_root_array(region_node, finals)

    merger = MergeRegion()
    regions = merger.generate(mat=root_array, root=region_node.region)

    # Add all the children (merged and final) to the root node
    finals_idx = 0
    for idx in range(len(regions)):
        child_node = RegionNode(regions[idx], None, 1, name=f"{root.name}{idx}")
        root.add_child(child_node)
        finals_idx = idx

    for idx in range(len(finals)):
        final_child = finals[idx]
        final_child.name = f"{root.name}{idx + finals_idx}"
        root.add_child(final_child)

    return root
