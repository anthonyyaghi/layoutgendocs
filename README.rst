================
LayoutGeneration
================


    Generate 2D scene layouts using different procedural algorithms


We built 2D layouts of scenes using a hierarchy of procedural algorithms. The layout is built like a tree starting with a root node containing an empty region, at each consequent layer, we apply different generation strategies to different region types.

We need 2 json files to run the generation:
 1. List of regions that can be used in the generation
 2. A configuration file containing the list of strategies to be used and in which hierarchy

Check the example directory.