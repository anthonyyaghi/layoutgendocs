import tempfile

import cv2
import numpy as np

from layoutgeneration.generation.execute import RegionNode
from layoutgeneration.layout.orientation import Orientation
from layoutgeneration.treeplotter.tree import Tree
from layoutgeneration.treeplotter.plotter import create_tree_diagram


def plot_generation_tree(root: RegionNode, output_path):
    """

    :param root: The root node of a generation tree
    :param output_path: The output path of the tree

    Will plot a graph showing the generation process
    """
    generate_tree_images(root)
    gen_tree = Tree(root=root, connector_type="step", orientation="north")
    create_tree_diagram(gen_tree, save_path=output_path, verbose=True)


def generate_tree_images(node: RegionNode):
    """

    :param node: Node in a tree

    Will add an image to the nodes of the tree. The image will be added in 2 forms: 1. numpy array under the "value"
    parameter and an image path under the "image" parameter
    """
    # Base case
    if not node.has_children:
        img = node_image(node)
        img_path = tempfile.NamedTemporaryFile().name + ".jpg"
        cv2.imwrite(img_path, img)
        node.value = img
        node.image = img_path
        return
    # Generate the images for the children
    for child in node.children:
        if child.region.orientation == Orientation.AUTO:
            child.region.orientation = node.region.orientation
        generate_tree_images(child)
    # Generate the node image a combination of the children images
    w = node.region.width
    h = node.region.height
    img = np.zeros((h, w, 3), np.uint8)
    for child in node.children:
        min_x, min_y = child.region.min_bound
        max_x, max_y = child.region.max_bound
        min_x -= node.region.x
        min_y -= node.region.y
        max_x -= node.region.x
        max_y -= node.region.y
        img[min_y:max_y, min_x:max_x] = child.value

    img_path = tempfile.NamedTemporaryFile().name + ".jpg"
    cv2.imwrite(img_path, img)
    node.value = img
    node.image = img_path


def node_image(node: RegionNode) -> np.array:
    """

    :param node: A node in a tree
    :return: An image in the form of a numpy array
    """
    w = node.region.width
    h = node.region.height
    img = np.zeros((h, w, 3), np.uint8)
    img[:, :] = node.region.region_type.value
    # Draw direction arrow
    start_point_x = int(w / 2)
    if node.region.orientation is Orientation.RIGHT:
        start_point_x = 0
    if node.region.orientation is Orientation.LEFT:
        start_point_x = int(w)

    start_point_y = int(h / 2)
    if node.region.orientation is Orientation.UP:
        start_point_y = int(h)
    if node.region.orientation is Orientation.DOWN:
        start_point_y = 0

    end_point_x = int(w / 2)
    if node.region.orientation is Orientation.RIGHT:
        end_point_x = int(w)
    if node.region.orientation is Orientation.LEFT:
        end_point_x = 0

    end_point_y = int(h / 2)
    if node.region.orientation is Orientation.UP:
        end_point_y = 0
    if node.region.orientation is Orientation.DOWN:
        end_point_y = int(h)

    start_point = (start_point_x, start_point_y)
    end_point = (end_point_x, end_point_y)
    color = (255, 255, 255)
    img = cv2.arrowedLine(img, start_point, end_point, color)
    return img
