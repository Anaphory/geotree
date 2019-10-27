import numpy

import sys
import argparse

import matplotlib.pyplot as plt
import ete3
import cartopy
import cartopy.crs as ccrs
import colorsys

parser = argparse.ArgumentParser()
parser.add_argument(
    "treestream",
    nargs="?", default=sys.stdin, type=argparse.FileType("r"))
parser.add_argument(
    "output",
    nargs="?", default=None, type=argparse.FileType("wb")
)
args = parser.parse_args()

leaf_colormap = None

ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines(resolution='10m')
# ax.add_feature(cartopy.feature.LAND, zorder=0, edgecolor='black')
# ax.add_feature(cartopy.feature.OCEAN, zorder=0)
min_lat, max_lat, min_lon, max_lon = None, None, None, None

for tree_string in args.treestream:
    t = ete3.Tree(tree_string)
    if leaf_colormap is None:
        leaf_colormap = {n: None for n in t.iter_leaf_names()}
        for k, key in enumerate(leaf_colormap):
            leaf_colormap[key] = numpy.array((k/len(leaf_colormap), 1.0, 1.0))

    for post, node in t.iter_prepostorder():
        if post or node.is_leaf():
            lat, lon = node.location.lstrip("{").rstrip("}").split("|")
            node.lat = float(lat)
            node.lon = float(lon)
            if node.is_leaf():
                node.color = leaf_colormap[node.name]
            else:
                node.color = numpy.mean([child.color
                                         for child in node.children],
                                        axis=0)
                node.color[1] *= 0.5
                for child in node.children:
                    plt.plot([node.lon, child.lon], [node.lat, child.lat],
                             color=colorsys.hsv_to_rgb(*child.color),
                             transform=ccrs.PlateCarree(),
                             linewidth=0.5,
                    )


            if min_lat is None:
                min_lat = lat
                max_lat = lat
                min_lon = lon
                max_lon = lon
            else:
                if min_lat > lat:
                    min_lat = lat
                if min_lon > lon:
                    min_lon = lon
                if max_lat < lat:
                    max_lat = lat
                if max_lon < lon:
                    max_lon = lon

plt.savefig(args.output, bbox_inches='tight', dpi=600)
plt.show()
