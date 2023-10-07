import json
import os.path
from queue import Queue
from typing import List, Callable, Dict

import cv2

from layoutgeneration.generation.execute import RegionNode
from layoutgeneration.layout.region import Region
from layoutgeneration.visualization.plot import generate_tree_images


def save_final_regions(root: RegionNode, output_path, save_img: bool = False):
    generate_tree_images(root)
    final_regions = find_bfs(root, lambda node: node.region.region_type.final)
    final_regions = list(
        map(lambda val: {"x": val["region"].x, "y": val["region"].y, "width": val["region"].width,
                         "height": val["region"].height, "orient": val["region"].orientation.value,
                         "dir_path": val["region"].region_type.dir_path, "path": val["path"],
                         "type": val["region"].region_type.name},
            final_regions))
    with open(output_path, "w") as output_file:
        json.dump(final_regions, output_file)

    if save_img:
        img = root.value
        img_path = f"{'.'.join(output_path.split('.')[:-1])}.png"
        cv2.imwrite(img_path, img)


def find_bfs(root: RegionNode, validate: Callable) -> List[Dict]:
    regions = []
    q = Queue()
    q.put({"node": root, "path": f"/{root.name}"})
    while not q.empty():
        val = q.get()
        node = val["node"]
        path = val["path"]
        if validate(node):
            regions.append({"region": node.region, "path": os.path.join(path, f"{node.region.region_type.name}_{node.name}")})
        for child in node.children:
            q.put({"node": child, "path": os.path.join(path, f"{node.region.region_type.name}_{node.name}")})
    return regions
