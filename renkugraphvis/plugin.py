# -*- coding: utf-8 -*-
#
# Copyright 2020 - Gabriele Barni [UniGe], Volodymyr Savchenko [EPFL]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import webbrowser
import click

from IPython.display import Image, HTML

import renkugraphvis.graph_utils as graph_utils


@click.group()
def graphvis():
    """Set of commands to generate interactive graph visualization."""
    pass


def show_graph_image(revision="HEAD", paths=os.getcwd(), filename="graph.png", input_notebook=None):
    filename = graph_utils.build_graph_image(revision, paths, filename, input_notebook)
    return Image(filename=filename)


@graphvis.command()
@click.option(
    "--revision",
    default="HEAD",
    help="The git revision to generate the log for, default: HEAD",
)
@click.option("--filename", default="graph.png", help="The filename of the output file image")
@click.option("--input", 'input_entity', default=None, help="Input notebook to process")
@click.argument("paths", type=click.Path(exists=False), nargs=-1)
def display(revision, paths, filename, input_entity):
    """Generates an output of the entire graph over an image file picture."""
    path = paths
    if paths is not None and isinstance(paths, click.Path):
        path = str(path)
    output_filename = graph_utils.build_graph_image(revision, path, filename, input_entity)
    return output_filename


@graphvis.command()
def show_graph():
    """Generates a web-based interactive version of the entire graph."""
    graph_html_content, ttl_content = graph_utils.build_graph_html(None, None)
    html_fn, ttl_fn = graph_utils.write_graph_files(graph_html_content, ttl_content)

    webbrowser.open(html_fn)


def build_graph(paths=os.getcwd(), template_location="local"):
    graph_html_content, ttl_content = graph_utils.build_graph_html(None, paths, template_location=template_location)
    graph_utils.write_graph_files(graph_html_content, ttl_content)


def display_interactive_graph(revision="HEAD", paths=os.getcwd(), include_title=False):
    graph_html_content, ttl_content = graph_utils.build_graph_html(None, paths, include_title=include_title)
    html_fn, ttl_fn = graph_utils.write_graph_files(graph_html_content, ttl_content)

    return HTML(f"""
        <iframe width="100%" height="1150px", src="{html_fn}" frameBorder="0" scrolling="no">
        </iframe>"""
                )
