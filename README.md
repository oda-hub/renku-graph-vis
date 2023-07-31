# renku-graph-vis plugin

This Renku plugin offers a visual representation of the project Knowledge Graph. Users can access the visualization through a CLI command, as well as during an interactive Renku session. The plugin allows users to have a live overview of the project's development through the Knowledge Graph.

Additionally, the plugin provides an option for users to enrich the graph with an ontology. By doing so, the plugin can identify specific types of individual components, thus enhancing the understanding of those. This enrichment allows users to gain a better understanding of the interconnections within the Knowledge Graph.

## Graphical visualization of the graph

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
  $ renku graphvis display --input final-an.ipynb`
  ```
  ![](readme_imgs/example_display_graph_final-an_1.png)
<!-- TODO to be properly tested, and not included before release
* `--revision`:  The revision of the Renku project from which the graph should be extracted. The default is `HEAD`.-->   



## `show-graph` command

The CLI command generates an interactive, web-based, graphical representation of the project Knowledge Graph.

```bash
$ renku graphvis show-graph
 ```

![](readme_imgs/example_show-graph.png)

By clicking on any node in the graph, users can interact with it. This action triggers the expansion of the mode: a `SPARQL` query is dynamically constructed, this retrieves all the nodes and edges directly linked to the clicked node. The animation below illustrates this behavior. It can also be seen that, after the expansion of a node, the newly added nodes can be reabsorbed by clicking on the same node once again.

<div align="center">
<img align="center" width="65%" src="readme_imgs/animation_expansion_retraction_2.gif">
</div>
<br clear="left"/>

The interface provides the user with a number of adjustable options, accessible via dedicated menus:

<div align="center">
<img align="center" width="65%" src="readme_imgs/graph_menu.png">
</div>

<!-- TODO to improve hierarchical layout -->
* **Change Graph Layout**: Currently, two layouts are supported.
  * _Random_: Nodes and edges are displayed randomly over the dedicated frame (as shown in the picture above).
  * _Hierarchical_: Nodes and edges are displayed in a hierarchical visualization. 
An example of this layout is displayed in the image below.
  <div align="center">
  <img src="readme_imgs/hierarchical_view_2.png" width="65%" />
  </div>

* **Enable/Disable Selection of Subsets of Nodes**: This feature allows users to filter certain subsets of nodes 
(e.g., astroquery-related nodes). The configuration can be done through a dedicated JSON file, 
as explained [here](https://github.com/oda-hub/renku-aqs-graph-library/#selection-of-subset-of-nodes).

<div align="center">
<img width="30%" src="readme_imgs/enable_disable_set_nodes-graph.png">
</div>

* **Apply Absorptions of Nodes on the Graph**: Users can enable the display of 
specific nodes along with their child nodes absorbed within. Conversely, they can display regular separate nodes. 
For example, in the images below, the Activity node shows its child nodes inside it (left image) 
and as separate nodes (right image). This functionality is configurable through a dedicated JSON file, 
as explained [here](https://github.com/oda-hub/renku-aqs-graph-library/#absorptionexpansion-of-nodes).
<div align="center">
<img align="center" width="37%" src="readme_imgs/reduced_activity.png">
<img align="center" width="38%" src="readme_imgs/expanded_activity.png">
</div>
<br clear="left"/>

* **Enable/Disable Graphical Configurations for the Graph**:  This feature allows users to enable or disable a set 
of graphical configurations for the graph's nodes and edges. Each configuration is loaded from a dedicated JSON file, as explained [here](https://github.com/oda-hub/renku-aqs-graph-library/#graphical). In the image below, two JSON files have been loaded, and the related checkboxes will enable/disable their configurations.

<div align="center">
<img width="30%" src="readme_imgs/enable_disable_configuration-graph.png">
</div>

The functionalities for graph drawing and user interactions are developed in a dedicated JavaScript library 
available at the following [repository](https://github.com/oda-hub/renku-aqs-graph-library/). 
Detailed descriptions of the various configuration files and the library's functionalities are also provided.

### Graph visualization within a renkulab session

The graph can be displayed during an interactive Renkulab session by including `renku_graph_vis` 
within the project's requirements. A dedicated button will then be displayed in the Renkulab launcher when 
a new session is started. This will open a dedicated tab for the visualization of the Graph.

<div align="center">
<img width="75%" src="readme_imgs/renkulab_overview_example_1.png">
</div>

The graph dynamically updates while working in the session. In the example below, the execution of a notebook is started, and when it completes, the graph is automatically reloaded to include the latest execution.

<div align="center">
<img width="75%" src="readme_imgs/renkulab_execution_example_1.gif">
</div>

### Ontology integration into the graph

An ontology can be integrated into the graph. By doing so, it is possible to gain valuable insights into the various types of entities present in the graph. In the image below, it can be observed a graph where the ODA ontology has been imported. Notably, the node labeled `SimbadClass` is an instance of the `AstroqueryModule` class, while the entity named `Mrk 421` is an instance of the `AstrophysicalObject` class. The ontology location can be conveniently provided within a dedicated config JSON file. More details are provided at the following [repository](https://github.com/oda-hub/renku-aqs-graph-library/).

<div align="center">
<img width="75%" src="readme_imgs/details_astroquery_annotations_2.png">
</div>

***
# Plugin requirements and installation

The plugin is currently developed using version `2.6.0` of renku-python. Please ensure that this version is installed 
by running:

```bash
renku --version
```

The versioning of the dependency is guaranteed during the plugin's installation, and in addition, a dedicated check will be performed during the import.

The plugin can be installed via `pip`:

```bash
pip install renku_graph_vis
```

Or can be made available within a Renku session, by adding those in the list of requirements of the Renku project, within your `requirements.txt` file.