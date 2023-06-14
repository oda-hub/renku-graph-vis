# -*- coding: utf-8 -*-
#
# Copyright 2020 - Viktor Gal
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).
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
import re
import subprocess
import webbrowser
import click

from IPython.display import Image, HTML
from prettytable import PrettyTable

import renkugraphvis.graph_utils as graph_utils


def _run_id(activity_id):
    return str(activity_id).split("/")[-1]


def _create_leaderboard(data, metric, format=None):
    leaderboard = PrettyTable()
    leaderboard.field_names = ["Run ID", "Module", "Query", metric]
    leaderboard.align["Module"] = "l"
    leaderboard.align["Query"] = "l"
    leaderboard.align[metric] = "r"
    for commit, v in data.items():
        if metric in v:
            v["query"].sort()
            leaderboard.add_row([commit, v["module"], v["query"], v[metric]])
    leaderboard.sortby = metric
    leaderboard.reversesort = True
    return leaderboard


@click.group()
def graphvis():
    pass


def show_graph_image(revision="HEAD", paths=os.getcwd(), filename="graph.png", no_oda_info=True, input_notebook=None):
    filename = graph_utils.build_graph_image(revision, paths, filename, no_oda_info, input_notebook)
    return Image(filename=filename)


@graphvis.command()
@click.option(
    "--revision",
    default="HEAD",
    help="The git revision to generate the log for, default: HEAD",
)
@click.option("--filename", default="graph.png", help="The filename of the output file image")
@click.option("--input-notebook", default=None, help="Input notebook to process")
@click.argument("paths", type=click.Path(exists=False), nargs=-1)
def display(revision, paths, filename, input_notebook):
    path = paths
    if paths is not None and isinstance(paths, click.Path):
        path = str(path)
    output_filename = graph_utils.build_graph_image(revision, path, filename, input_notebook)
    return output_filename


@graphvis.command()
def start_session():
    gitlab_url = subprocess.check_output(["git", "remote", "get-url", "origin"]).decode().strip()

    new_session_urls = []

    for pattern in [
        'https://renkulab.io/gitlab/(.*)\.git',
        'git@renkulab.io:(.*)\.git'
    ]:
        if (r := re.match(pattern, gitlab_url)) is not None:
            new_session_urls.append(f"https://renkulab.io/projects/{r.group(1)}/sessions/new?autostart=1&branch=master")

    if (n := len(new_session_urls)) > 1:
        click.echo(f"using first of many session URLs: {new_session_urls}")
    elif n == 0:
        raise RuntimeError("unable to find any session URLs")

    click.echo(f"will open new session: {new_session_urls[0]}")

    webbrowser.open(new_session_urls[0])


@graphvis.command()
def show_graph():
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
