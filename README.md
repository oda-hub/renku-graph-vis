# renku-graph-vis plugin

This Renku plugin offers a visual representation of the project Knowledge Graph. Users can access the visualization through a CLI command, as well as during an interactive Renku session. The plugin allows users to have a live overview of the project's development through the Knowledge Graph.

Additionally, the plugin provides an option to enrich the graph with an ontology. By doing so, the plugin can identify specific types of individual components, thus enhancing the understanding of those. This enrichment allows users to gain a better understanding of the interconnections within the Knowledge Graph.

## Visualization of the graph

Starting from the project Knowledge Graph, extracted directly from the renku project, this is queried to retrieve the needed information and generate a graphical representation.

Two main sets of functionalities are provided:

* Two CLI commands
  * `display`: Generates a representation of the graph as an output image.
  * `show-graph`: Starts an interactive visualization of the graph in the web browser.
* Dynamic visualization of the graph during a Renku session.

## `display` command

The CLI command outputs a graphical representation of the graph as a PNG image.

```bash
$ renku graphvis display
 ```
![](readme_imgs/example_display_graph_complete_2.png)

#### Parameters

* `--filename`: The filename of the output image file. Currently, only PNG images are supported. The default is graph.png.

  ```bash
  $ renku graphvis display --filename graph.png
  ```
* `--input`: Specifies the input entity to process (e.g., input notebook for a Papermill execution). If not specified, it will query for all the executions from all input entities.
  ```bash
  $ renku graphvis display --input final-an.ipynb
  ```
  ![](readme_imgs/example_display_graph_final-an_1.png)
<!-- TODO to be properly tested, and not included before release
* `--revision`:  The revision of the Renku project from which the graph should be extracted. The default is `HEAD`.-->

## `show-graph` command

The CLI command generates an interactive, web-based, graphical representation of the project Knowledge Graph.

```bash
$ renku graphvis show-graph
 ```

![show_graph_main](readme_imgs/example_show-graph.png)

By clicking on any node in the graph, users can interact with it. This action triggers the expansion of the node: a `SPARQL` query is dynamically constructed, this retrieves all the nodes and edges directly linked to the clicked node. The animation below illustrates this behavior. It can also be seen that, after the expansion of a node, the newly added nodes can be reabsorbed by clicking on the same node once again.

<div align="center">
<img align="center" width="65%" src="readme_imgs/animation_expansion_retraction_2.gif">
</div>
<br clear="left"/>

The interface provides the user with a number of adjustable options, accessible via a dedicated menu, displayed in the picture below.

<div align="center">
<img align="center" width="65%" src="readme_imgs/graph_menu.png">
</div>
<br clear="left"/>

The following options are available:

<!-- TODO to improve hierarchical layout -->
* **Change Graph Layout**: Currently, two layouts are supported:
  * _Random_: Nodes and edges are displayed randomly over the dedicated frame (as shown in the picture above).
  * _Hierarchical_: Nodes and edges are displayed in a hierarchical visualization. 
An example of this layout is displayed in the image below.
  <div align="center">
  <img src="readme_imgs/hierarchical_view_2.png" width="65%" />
  </div>

<!-- TODO a better naming was suggested, but I don't remember it-->
* **Enable/Disable Selection of Subsets of Nodes**: This feature allows users to filter certain subsets of nodes (e.g., astroquery-related nodes). The configuration can be done through a dedicated JSON file. The animation below gives a demonstration.

<div align="center">
<img width="65%" src="readme_imgs/enable_disable_oda_nodes_selection.gif">
</div>

* **Apply Absorptions of Nodes on the Graph**: Users can enable the display of 
specific nodes along with their child nodes absorbed within, using a set of dedicated checkboxes. For example, in the animation below, it can be seen that the `Activity` node has some of its child nodes (i.e. inputs and outputs) inside it, as well as separate nodes once the relative checkbox is unchecked. This functionality is configurable through a dedicated JSON file.

<div align="center">
<img width="65%" src="readme_imgs/activity_reduction_animation.gif">
</div>


* **Enable/Disable Graphical Configurations for the Graph**:  This feature allows users to enable or disable a set of graphical configurations for the graph's nodes and edges. Each configuration is loaded from a dedicated JSON file, that can be enabled and disabled via a dedicated checkbox. In the animation below, it can be seen that two JSON files have been loaded, more specifically, those are `renku_graph_graphical_config.json` and `oda_graph_graphical_config.json`. In particular, the first one is disabled and then re-enabled, thus removing and then re-applying the properties defined in the json file.

<div align="center">
<img width="65%" src="readme_imgs/enable_disable_graphical_configuration_animation_1.gif">
</div>

The functionalities for graph drawing and user interactions are developed in a dedicated JavaScript library available at the following [repository](https://github.com/oda-hub/renku-aqs-graph-library/). Detailed descriptions of the various configuration files and the library's functionalities are also provided.

### Graph visualization within a renkulab session

The graph can be displayed during an interactive Renkulab session by including the plugin as a project's requirements. A dedicated button will then be displayed in the Renkulab launcher when a new session is started. This will open a dedicated tab for the visualization of the Graph.

<div align="center">
<img width="75%" src="readme_imgs/renkulab_overview_example_1.png">
</div>

The graph dynamically updates while working in the session. In the example below, the execution of a notebook is started, and when it completes, the graph is automatically reloaded to include the latest execution.

<div align="center">
<img width="75%" src="readme_imgs/renkulab_execution_example_3.gif">
</div>

### Ontology integration into the graph

An ontology can be integrated into the graph. By doing so, it is possible to gain valuable insights into the various types of entities present in the graph. In the image below, it can be observed a graph where the ODA ontology has been imported. Notably, the node labeled `SimbadClass` is an instance of the `AstroqueryModule` class, while the entity named `Mrk 421` is an instance of the `AstrophysicalObject` class. The ontology location can be conveniently provided within a dedicated config JSON file. More details are provided at the following [repository](https://github.com/oda-hub/renku-aqs-graph-library/).

<div align="center">
<img width="75%" src="readme_imgs/details_astroquery_annotations_2.png">
</div>

***
# Plugin requirements and installation

The plugin is compatible with a minimum version of `renku-python` of `2.7.0`. Please ensure that the version you have installed is compatible by using the command:

```bash
renku --version
```

The versioning of the dependency is guaranteed during the plugin's installation, and in addition, a dedicated check will be performed during the import.

The plugin can be installed via `pip`:

```bash
pip install renku_graph_vis
```

Or can be made available within a Renku session, by adding those in the list of requirements of the Renku project, within your `requirements.txt` file. Once the new image is available, the plugin will be available within the renku session.
