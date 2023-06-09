# renku-graph-vis

## Graphical visualization of the graph
Starting from the knowledge graph extracted from the renku project, this is queried to retrieve the needed information, 
perform some inferring and generating an interactive graphical representation.

In particular, two commands are provided:
% TODO deprecated?
* `display` to generate a representation of the graph over an output image (probably will be deprecated)
* `show-graph` to start an interactive visualization of the graph over the browser 

### `display` command
<details>
CLI command to output a graphical representation of the graph over a png image.

In particular, the following information are elaborated:
* inputs/arguments/outputs of the single workflow (eg notebook execution);

#### Parameters

* `--filename` The filename of the output file image, until now, only png images are supported (eg `--filename graph.png`), default is `graph.png`
* `--input-notebook` Input notebook to process, if not specified, will query for all the executions from all notebooks  
* `--revision` The revision of the renku project at which the graph should be extracted, defaults to `HEAD`    
```bash
$ renku aqs display
 ```
![](readme_imgs/example_display_graph_complete.png)

#### Specify executed notebook
```bash
$ renku aqs display --input-notebook final-an.ipynb
 ```

![](readme_imgs/example_display_graph_final-an.png)

</details>