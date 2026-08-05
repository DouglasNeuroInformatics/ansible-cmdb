#!/usr/bin/env python

import sys
import os
import codecs
import shutil
from mako.template import Template
from mako.lookup import TemplateLookup


def render(hosts, vars={}, tpl_dirs=[]):
    if not os.path.isdir("cmdb"):
        os.mkdir("cmdb")

    # Copy static assets (JS, CSS, images) into the output directory so they
    # can be served over HTTP alongside the generated HTML pages.
    data_dir = vars.get("data_dir", "")
    static_src = os.path.join(data_dir, "static")
    static_dst = os.path.join("cmdb", "static")
    if os.path.isdir(static_src):
        if os.path.isdir(static_dst):
            shutil.rmtree(static_dst)
        shutil.copytree(static_src, static_dst)

    lookup = TemplateLookup(
        directories=tpl_dirs,
        default_filters=["decode.utf8"],
        input_encoding="utf-8",
        output_encoding="utf-8",
        encoding_errors="replace",
    )

    # Render host overview
    template = lookup.get_template("html_fancy_split_overview.tpl")
    out_file = os.path.join("cmdb", "index.html")
    output = template.render(hosts=hosts, **vars).lstrip().decode("utf8")
    with open(out_file, "w", encoding="utf8") as f:
        f.write(output)

    # Render host details
    template = lookup.get_template("html_fancy_split_detail.tpl")
    for hostname, host in sorted(hosts.items()):
        out_file = os.path.join("cmdb", "{0}.html".format(hostname))
        output = template.render(host=host, **vars).lstrip().decode("utf8")
        with open(out_file, "w", encoding="utf8") as f:
            f.write(output)
