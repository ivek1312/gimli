#!/usr/bin/env python
# encoding: utf-8
"""File: sidebar_gallery.py.

Author: Florian Wagner <fwagner@gfz-potsdam.de>
Description: Add all examples/tutorials to sidebar gallery
Created on: 2013-10-13
"""

import os
import random
import re
from glob import glob
from os.path import basename, dirname, join


def make_gallery(src_path, out_path):
    """TODO DOCUMENTME."""
    publish = os.getenv("PUBLISH")
    if publish:
        build_dir = "https://www.pygimli.org"
    else:
        build_dir = ""

    example_dir = join(src_path, "examples")
    tutorial_dir = join(src_path, "tutorials")
    img_dir = join(build_dir, "_images")

    # Get examples/tutorials
    examples = [fn for fn in glob(join(example_dir, "*/*plot*.py"))
                if not "dev" in fn]
    tutorials = [fn for fn in glob(join(tutorial_dir, "*/*plot*.py"))
                 if not "dev" in fn]

    # Get captions
    def readRSTSecTitles(fname, verbose=False):
        """ Return list of section titles found in a given RST file. """
        rst_titles = re.compile(r"^(.+)\n[-=]+\n", flags=re.MULTILINE)
        with open(fname) as f:
            titles = re.findall(rst_titles, f.read())
            if verbose:
                print("File:", fname)
                print("Title:", titles)
        # go through lines only if compiled regex fails (py2/py3 issue)
        if not titles:
            print("WARNING: Problem reading section title in", fname)
            with open(fname) as f:
                title = "unknown"
                for line in f.readlines():
                    if "---" in line or "===" in line:
                        titles.append(title)  # add the line after
                    title = line

        return titles[0].rstrip()

    ex_titles = [readRSTSecTitles(ex) for ex in examples]
    tut_titles = [readRSTSecTitles(tut) for tut in tutorials]
    titles = ex_titles + tut_titles

    # Adjust paths to output directory for html links
    examples = [e.replace(example_dir, join(build_dir, "_examples_auto"))
                for e in examples]

    tutorials = [t.replace(tutorial_dir, join(build_dir, "_tutorials_auto"))
                 for t in tutorials]

    # Create HTML gallery for sidebar with random start item
    gallery = examples + tutorials
    print("\nAdding %d examples/tutorials to sidebar gallery.\n" %
          len(gallery))
    print("\t{:40}{}\n\t".format("Title", "File") + "-" * 80)
    for line in zip(titles, gallery):
        print("\t{:40}{}".format(*line))
    print("\n")

    html_top = """\
    <!-- This file is automatically generated by sidebar_gallery.py -->
    <div id="sidebar_example_gallery" class="carousel slide">
    <div class="carousel-inner">"""

    html_bottom = """\
    </div>
    <a class="carousel-control left" href="#sidebar_example_gallery" data-slide="prev">&lsaquo;</a>
    <a class="carousel-control right" href="#sidebar_example_gallery" data-slide="next">&rsaquo;</a>
    </div>"""

    html_item = """\
    <div class="item">
    <a href="{}">
    <img src="{}">
    <div class="carousel-caption">
    {}
    </div>
    </a>
    </div>"""

    idx = random.randint(0, len(gallery) - 1)
    items = []
    for ix, (item, title) in enumerate(zip(gallery, titles)):
        path = dirname(item)
        name = basename(item)
        url = join(path, name.replace(".py", ".html"))
        img = join(img_dir, "sphx_glr_" + name.replace(".py", "_thumb.png"))
        item = html_item.format(url, img, title)

        if ix == idx:
            item = item.replace("item", "active item")

        items.append(item)

    items.insert(0, html_top)
    items.append(html_bottom)
    html = "\n".join(items)

    if not os.path.exists(join(out_path, "_templates/")):
        os.mkdir(join(out_path, "_templates/"))

    with open(join(out_path, "_templates/gallery.html"), "w") as file:
        file.write(html)


if __name__ == '__main__':
    make_gallery('.', '.')
