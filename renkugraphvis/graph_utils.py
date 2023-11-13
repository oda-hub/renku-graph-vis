import os
import io
import typing
import pydotplus
import rdflib
import json
import glob
import urllib.request
import pathlib

from rdflib.tools.rdf2dot import LABEL_PROPERTIES
from rdflib.tools import rdf2dot
from lxml import etree
from dateutil import parser
from pyvis.network import Network

from renku.domain_model.project_context import project_context
from renku.command.graph import export_graph_command
from renku.core.errors import RenkuException

import renkugraphvis.javascript_graph_utils as javascript_graph_utils
import renkugraphvis.io_utils as io_utils

from renkugraphvis.config import ENTITY_METADATA_GRAPHVIS_DIR

# TODO improve this
__this_dir__ = os.path.join(os.path.abspath(os.path.dirname(__file__)))
__conf_dir__ = os.path.join(os.path.dirname(__file__), 'configs_dir')


def _graphvis_graph():
    G = rdflib.Graph()
    metadata_path = pathlib.Path(project_context.metadata_path, ENTITY_METADATA_GRAPHVIS_DIR)
    if metadata_path.exists():
        annotation_list = []
        entity_folder_list = glob.glob(f"{metadata_path}/*")
        for entity_folder in entity_folder_list:
            print("Scanning entity folder: ", entity_folder)
            revision_entity_folder_list = glob.glob(f"{entity_folder}/*")
            for revision_entity_folder in revision_entity_folder_list:
                print("Scanning entity folder checksum: ", revision_entity_folder)
                annotation_object_list = glob.glob(f"{revision_entity_folder}/*.jsonld")
                for annotation_object_file in annotation_object_list:
                    with open(annotation_object_file) as annotation_object_file_fn:
                        annotation_object = json.load(annotation_object_file_fn)
                    annotation_list.append(annotation_object)
                    G.parse(data=json.dumps(annotation_object), format="json-ld")

    return G


def _renku_graph(revision=None, paths=None):
    # FIXME: use (revision) filter

    cmd_result = export_graph_command().working_directory(paths).build().execute()

    if cmd_result.status == cmd_result.FAILURE:
        raise RenkuException("fail to export the renku graph")
    graph = cmd_result.output.as_rdflib_graph()

    return graph


def write_graph_files(graph_html_content, ttl_content):
    html_fn = 'graph.html'
    ttl_fn = 'full_graph.ttl'

    with open(ttl_fn, 'w') as gfn:
        gfn.write(ttl_content)

    io_utils.gitignore_file(ttl_fn)

    javascript_graph_utils.write_modified_html_content(graph_html_content, html_fn)
    io_utils.gitignore_file(html_fn)

    return html_fn, ttl_fn


def extract_graph(revision, paths, graph_nodes_subset_config=None):
    if paths is None:
        paths = project_context.path

    # renku graph, from .renku folder
    renku_graph = _renku_graph(revision, paths)

    # graphvis graph, from graphvis folder
    graphvis_graph = _graphvis_graph()

    # ontologies graph, from nodes subset config file
    ontologies_graph = _nodes_subset_ontologies_graph(graph_nodes_subset_config=graph_nodes_subset_config)

    # not the recommended approach but works in our case https://rdflib.readthedocs.io/en/stable/merging.html
    overall_graph = graphvis_graph + renku_graph + ontologies_graph

    overall_graph.bind("aqs", "http://www.w3.org/ns/aqs#")
    overall_graph.bind("oa", "http://www.w3.org/ns/oa#")
    overall_graph.bind("xsd", "http://www.w3.org/2001/XAQSchema#")
    overall_graph.bind("oda", "http://odahub.io/ontology#")
    overall_graph.bind("odas", "https://odahub.io/ontology#")
    overall_graph.bind("local-renku", f"file://{paths}/")

    return overall_graph


def _nodes_subset_ontologies_graph(graph_nodes_subset_config=None):
    G = rdflib.Graph()
    if graph_nodes_subset_config is not None:
        for graph_nodes_subset_config_obj_key in graph_nodes_subset_config:
            graph_nodes_subset_config_obj = graph_nodes_subset_config[graph_nodes_subset_config_obj_key]
            if 'ontology_url' in graph_nodes_subset_config_obj:
                data = urllib.request.urlopen(graph_nodes_subset_config_obj['ontology_url'])
                G.parse(data)
            elif 'ontology_path' in graph_nodes_subset_config_obj:
                if os.path.exists(graph_nodes_subset_config_obj['ontology_path']):
                    with open(graph_nodes_subset_config_obj['ontology_path']) as oo_fn:
                        G.parse(oo_fn)
                else:
                    print(f"\033[31m{graph_nodes_subset_config_obj['ontology_path']} not found\033[0m")

    return G


def get_graph_nodes_subset_config_obj(graph_nodes_subset_config_patter_fn='*_graph_nodes_subset_config.json'):
    graph_nodes_subset_config_obj = None
    nodes_subset_config_list_files = glob.glob(os.path.join(__conf_dir__, graph_nodes_subset_config_patter_fn))

    for config_file_fn in nodes_subset_config_list_files:
        with open(config_file_fn) as graph_nodes_subset_config_fn_f:
            if graph_nodes_subset_config_obj is None:
                graph_nodes_subset_config_obj = {}
            graph_nodes_subset_config_obj.update(json.load(graph_nodes_subset_config_fn_f))

    return graph_nodes_subset_config_obj


def get_graph_reduction_config_obj(graph_reduction_config_patter_fn='*_graph_reduction_config.json'):
    reduction_config_list_files = glob.glob(os.path.join(__conf_dir__, graph_reduction_config_patter_fn))

    graph_reduction_config_obj = None
    for config_file_fn in reduction_config_list_files:
        with open(config_file_fn) as graph_reduction_config_fn_f:
            if graph_reduction_config_obj is None:
                graph_reduction_config_obj = {}
            graph_reduction_config_obj.update(json.load(graph_reduction_config_fn_f))

    return graph_reduction_config_obj


def get_graph_graphical_config_obj(graph_graphical_config_patter_fn='*_graph_graphical_config.json'):
    graphical_config_list_files = glob.glob(os.path.join(__conf_dir__, graph_graphical_config_patter_fn))
    nodes_graph_config_obj = {}
    edges_graph_config_obj = {}
    graph_config_names_list = []

    for config_file_fn in graphical_config_list_files:
        config_file_path = pathlib.Path(config_file_fn)
        config_file_name = config_file_path.name
        with open(config_file_fn) as graph_config_fn_f:
            graph_config_loaded = json.load(graph_config_fn_f)
            nodes_graph_config_obj_loaded = graph_config_loaded.get('Nodes', {})
            edges_graph_config_obj_loaded = graph_config_loaded.get('Edges', {})

        if nodes_graph_config_obj_loaded is not None:
            for config_type in nodes_graph_config_obj_loaded:
                nodes_graph_config_obj_loaded[config_type]['config_file'] = config_file_name
            nodes_graph_config_obj.update(nodes_graph_config_obj_loaded)
        if edges_graph_config_obj_loaded is not None:
            for config_type in edges_graph_config_obj_loaded:
                edges_graph_config_obj_loaded[config_type]['config_file'] = config_file_name
            edges_graph_config_obj.update(edges_graph_config_obj_loaded)

        graph_config_names_list.append(config_file_fn)

    return nodes_graph_config_obj, edges_graph_config_obj, graph_config_names_list


def build_graph_html(revision, paths,
                     include_title=True,
                     template_location="local",
                     include_ttl_content_within_html=True):

    # for compatibility with Javascript
    nodes_graph_config_obj, edges_graph_config_obj, graph_config_names_list = get_graph_graphical_config_obj()
    nodes_graph_config_obj_str = json.dumps(nodes_graph_config_obj).replace("\\\"", '\\\\"')
    edges_graph_config_obj_str = json.dumps(edges_graph_config_obj).replace("\\\"", '\\\\"')

    graph_reduction_config_obj = get_graph_reduction_config_obj()
    graph_reductions_obj_str = json.dumps(graph_reduction_config_obj)

    graph_nodes_subset_config_obj = get_graph_nodes_subset_config_obj()
    # for compatibility with Javascript
    # FIXME there must be a better way
    graph_nodes_subset_config_obj_str = json.dumps(graph_nodes_subset_config_obj)\
        .replace("\\\"", '\\\\"') \
        .replace("\\\\s", '\\\\\\\\\\\\s') \
        .replace("\\n", '\\\\n') \
        .replace("\\t", '\\\\t')

    overall_graph = extract_graph(revision, paths, graph_nodes_subset_config=graph_nodes_subset_config_obj)
    graph_str = overall_graph.serialize(format="n3")

    full_graph_ttl_str = graph_str.replace("\\\"", '\\\\"')

    net = Network(
        height='750px', width='100%',
        cdn_resources=template_location
    )
    net.generate_html()

    javascript_graph_utils.set_html_head(net)

    javascript_graph_utils.add_js_click_functionality(net,
                                                      graph_ttl_stream=full_graph_ttl_str,
                                                      nodes_graph_config_obj_str=nodes_graph_config_obj_str,
                                                      edges_graph_config_obj_str=edges_graph_config_obj_str,
                                                      graph_reductions_obj_str=graph_reductions_obj_str,
                                                      graph_nodes_subset_config_obj_str=graph_nodes_subset_config_obj_str,
                                                      include_ttl_content_within_html=include_ttl_content_within_html)

    javascript_graph_utils.set_html_content(net,
                                            graph_config_names_list=graph_config_names_list,
                                            nodes_graph_config_obj_dict=nodes_graph_config_obj,
                                            edges_graph_config_obj_dict=edges_graph_config_obj,
                                            graph_reduction_config_obj_dict=graph_reduction_config_obj,
                                            graph_nodes_subset_config_obj_dict=graph_nodes_subset_config_obj,
                                            include_title=include_title)

    # return net, html_fn
    return net.html, graph_str


def build_graph_image(revision, paths, filename, input_entity):

    graph_node_config_obj_default = {
        "shape": "box",
        "color": "#FFFFFF",
        "style": "filled",
        "border": 2,
        "cellborder": 0,
        "value": 20,
        "cellpadding": 5
    }

    if paths is None:
        paths = project_context.path

    default_graph_graphical_config_patter_fn = '*_graph_graphical_config.json'
    graph_nodes_subset_config_patter_fn = '*_graph_nodes_subset_config.json'

    graphical_config_list_files = glob.glob(os.path.join(__conf_dir__, default_graph_graphical_config_patter_fn))
    nodes_subset_config_list_files = glob.glob(os.path.join(__conf_dir__, graph_nodes_subset_config_patter_fn))

    nodes_graph_config_obj = {}
    edges_graph_config_obj = {}

    for config_file_fn in graphical_config_list_files:
        config_file_path = pathlib.Path(config_file_fn)
        config_file_name = config_file_path.name
        with open(config_file_fn) as graph_config_fn_f:
            graph_config_loaded = json.load(graph_config_fn_f)
            nodes_graph_config_obj_loaded = graph_config_loaded.get('Nodes', {})
            edges_graph_config_obj_loaded = graph_config_loaded.get('Edges', {})

        if nodes_graph_config_obj_loaded is not None:
            for config_type in nodes_graph_config_obj_loaded:
                nodes_graph_config_obj_loaded[config_type]['config_file'] = config_file_name
            nodes_graph_config_obj.update(nodes_graph_config_obj_loaded)
        if edges_graph_config_obj_loaded is not None:
            for config_type in edges_graph_config_obj_loaded:
                edges_graph_config_obj_loaded[config_type]['config_file'] = config_file_name
            edges_graph_config_obj.update(edges_graph_config_obj_loaded)

    nodes_graph_config_obj['Default'] = graph_node_config_obj_default

    graph_nodes_subset_config_obj = None
    for config_file_fn in nodes_subset_config_list_files:
        with open(config_file_fn) as graph_nodes_subset_config_fn_f:
            if graph_nodes_subset_config_obj is None:
                graph_nodes_subset_config_obj = {}
            graph_nodes_subset_config_obj.update(json.load(graph_nodes_subset_config_fn_f))

    graph = extract_graph(revision, paths, graph_nodes_subset_config=graph_nodes_subset_config_obj)
    renku_path = paths

    query_where = build_query_where(input_entity=input_entity, graph_nodes_subset_config=graph_nodes_subset_config_obj)
    query_construct = build_query_construct(graph_nodes_subset_config=graph_nodes_subset_config_obj)

    query = f"""{query_construct}
               {query_where}
               """

    r = graph.query(query)

    G = rdflib.Graph()
    G.parse(data=r.serialize(format="n3").decode(), format="n3")
    G.bind("oda", "http://odahub.io/ontology#")
    G.bind("odas", "https://odahub.io/ontology#")  # the same
    G.bind("local-renku", f"file://{renku_path}/")

    type_label_values_dict = {}
    analyze_types(G, type_label_values_dict)

    stream = io.StringIO()
    rdf2dot.rdf2dot(G, stream)
    pydot_graph = pydotplus.graph_from_dot_data(stream.getvalue())

    for node in pydot_graph.get_nodes():
        customize_node(node,
                       nodes_graph_config_obj,
                       type_label_values_dict=type_label_values_dict
                       )

    # list of edges and simple color change
    for edge in pydot_graph.get_edge_list():
        customize_edge(edge)

    # final output write over the png image
    pydot_graph.write_png(filename)

    return filename


def customize_edge(edge: typing.Union[pydotplus.Edge]):
    if 'label' in edge.obj_dict['attributes']:
        edge_html = etree.fromstring(edge.obj_dict['attributes']['label'][1:-1])
        edge_html.text = edge_html.text.split(":")[1]
        edge.set_label('< ' + etree.tostring(edge_html, encoding='unicode') + ' >')


def get_edge_label(edge: typing.Union[pydotplus.Edge]) -> str:
    edge_label = None
    if 'label' in edge.obj_dict['attributes']:
        edge_html = etree.fromstring(edge.obj_dict['attributes']['label'][1:-1])
        edge_label_list = edge_html.text.split(":")
        if len(edge_label_list) == 1:
            edge_label = edge_html.text.split(":")[0]
        else:
            edge_label = edge_html.text.split(":")[1]
    return edge_label


def get_id_node(node: typing.Union[pydotplus.Node]) -> str:
    id_node = None
    if 'label' in node.obj_dict['attributes']:
        table_html = etree.fromstring(node.get_label()[1:-1])
        tr_list = table_html.findall('tr')

        td_list_first_row = tr_list[0].findall('td')
        if td_list_first_row is not None:
            b_element_title = td_list_first_row[0].findall('B')
            if b_element_title is not None:
                id_node = b_element_title[0].text

    return id_node


def get_node_graphical_info(node: typing.Union[pydotplus.Node],
                   type_node) -> [str, str]:
    node_label = ""
    node_title = ""
    if 'label' in node.obj_dict['attributes']:
        # parse the whole node table into a lxml object
        table_html = etree.fromstring(node.get_label()[1:-1])
        tr_list = table_html.findall('tr')
        for tr in tr_list:
            list_td = tr.findall('td')
            if len(list_td) == 2:
                list_left_column_element = list_td[0].text.split(':')
                # setting label
                if type_node == 'Action':
                    if 'command' in list_left_column_element:
                        node_label = '<b>' + list_td[1].text[1:-1] + '</b>'
                elif type_node == 'CommandInput':
                    node_label = '<b><i>' + list_td[1].text[1:-1] + '</i></b>'
                else:
                    node_label = ('<b>' + type_node + '</b>\n' + list_td[1].text[1:-1])
                # setting title
                if 'startedAtTime' in list_left_column_element:
                    parsed_startedAt_time = parser.parse(list_td[1].text.replace('^^xsd:dateTime', '')[1:-1])
                    # create an additional row to attach at the bottom, so that time is always at the bottom
                    node_title += parsed_startedAt_time.strftime('%Y-%m-%d %H:%M:%S') + '\n'

    if node_label == "":
        node_label = '<b>' + type_node + '</b>'
    if node_title == "":
        node_title = type_node
    return node_label, node_title


def customize_node(node: typing.Union[pydotplus.Node],
                   graph_configuration,
                   type_label_values_dict=None
                   ):
    id_node = None

    if 'label' in node.obj_dict['attributes']:
        # parse the whole node table into a lxml object
        table_html = etree.fromstring(node.get_label()[1:-1])
        tr_list = table_html.findall('tr')

        # modify the first row, hence the title of the node, and then all the rest
        td_list_first_row = tr_list[0].findall('td')
        if td_list_first_row is not None:
            td_list_first_row[0].attrib.pop('bgcolor')
            b_element_title = td_list_first_row[0].findall('B')
            b_element_title[0].attrib['align'] = 'center'
            node_configuration = graph_configuration['Default']
            if b_element_title is not None:
                id_node = b_element_title[0].text
            if id_node is not None:
                for key in graph_configuration:
                    if id_node in type_label_values_dict and type_label_values_dict[id_node] in key.split(","):
                        node_configuration = graph_configuration[key]
                        break
                # apply styles (shapes, colors etc etc)
                # color and shape change
                node.set_style(node_configuration.get('style', graph_configuration['Default']['style']))
                node.set_shape(node_configuration.get('shape', graph_configuration['Default']['shape']))
                node.set_color(node_configuration.get('color', graph_configuration['Default']['color']))

                table_html.attrib['cellborder'] = str(node_configuration.get('cellborder',
                                                                             graph_configuration['Default']['cellborder']))
                # otherwise the output contains imperfections with the border, as specified in the doc
                if node.get_color().upper() != "#FFFFFF":
                    table_html.attrib['border'] = str(0)
                else:
                    table_html.attrib['border'] = str(graph_configuration['Default']['border'])
                table_html.attrib['cellpadding'] = str(node_configuration.get('cellpadding',
                                                                         graph_configuration['Default']['cellpadding']))

                # remove not needed long id information
                table_html.remove(tr_list[1])
                # remove not-needed information in the output tree nodes
                for tr in tr_list:
                    list_td = tr.findall('td')
                    if len(list_td) == 2:
                        list_left_column_element = list_td[0].text.split(':')
                        if 'align' in list_td[1].keys():
                            list_td[1].attrib['align'] = 'center'
                            list_td[1].attrib['colspan'] = '1'
                        if 'startedAtTime' in list_left_column_element:
                            parsed_startedAt_time = parser.parse(list_td[1].text.replace('^^xsd:dateTime', '')[1:-1])
                            # create an additional row to attach at the bottom, so that time is always at the bottom
                            time_td = etree.Element('td')
                            time_td.attrib['align'] = 'center'
                            time_td.attrib['colspan'] = '2'
                            time_td.text = parsed_startedAt_time.strftime('%Y-%m-%d %H:%M:%S')
                            tr.remove(list_td[1])
                            tr.append(time_td)

                        # remove trailing and leading double quotes
                        list_td[1].text = list_td[1].text[1:-1]

            # serialize back the table html
            node.obj_dict['attributes']['label'] = '< ' + etree.tostring(table_html, encoding='unicode') + ' >'


def build_query_where(input_entity: str = None, graph_nodes_subset_config = None):
    query_where = """
    WHERE {
    
        ?entityInput a <http://www.w3.org/ns/prov#Entity> ;
            <http://www.w3.org/ns/prov#atLocation> ?entityInputLocation ;
            <https://swissdatasciencecenter.github.io/renku-ontology#checksum> ?entityInputChecksum .
                    
        ?entityOutput a <http://www.w3.org/ns/prov#Entity> ; 
            <http://www.w3.org/ns/prov#qualifiedGeneration>/<http://www.w3.org/ns/prov#activity> ?activity ;
            <http://www.w3.org/ns/prov#atLocation> ?entityOutputLocation ;
            <https://swissdatasciencecenter.github.io/renku-ontology#checksum> ?entityOutputChecksum .
    
        ?activity a ?activityType ;
            <http://www.w3.org/ns/prov#startedAtTime> ?activityTime ;
            <http://www.w3.org/ns/prov#qualifiedAssociation>/<http://www.w3.org/ns/prov#hadPlan>/<https://swissdatasciencecenter.github.io/renku-ontology#command> ?activityCommand ;
            <http://www.w3.org/ns/prov#qualifiedUsage>/<http://www.w3.org/ns/prov#entity> ?entityInput .
     
    """

    if input_entity is not None:
        query_where += f"""
                        
            FILTER ( ?entityInputLocation = '{input_entity}' ) .
                    
        """

    query_where += """
    OPTIONAL 
    {
    """

    if graph_nodes_subset_config is not None:
        for graph_nodes_subset_config_obj_key in graph_nodes_subset_config:
            graph_nodes_subset_config_obj = graph_nodes_subset_config[graph_nodes_subset_config_obj_key]
            if 'query_where' in graph_nodes_subset_config_obj:
                query_where += graph_nodes_subset_config_obj['query_where']

    query_where += """
        }
    }
    """

    return query_where


def build_query_construct(graph_nodes_subset_config=None):
    # add time activity information
    query_construct_main = """
        ?entityOutput a <https://swissdatasciencecenter.github.io/renku-ontology#CommandOutput> ;
            <http://www.w3.org/ns/prov#atLocation> ?entityOutputLocation ;
            <https://swissdatasciencecenter.github.io/renku-ontology#checksum> ?entityOutputChecksum .
            
        ?entityInput a <http://www.w3.org/ns/prov#EntityInput> ;
            <http://www.w3.org/ns/prov#atLocation> ?entityInputLocation ;
            <https://swissdatasciencecenter.github.io/renku-ontology#checksum> ?entityInputChecksum .
        
        ?activity a ?activityType ;
            <http://www.w3.org/ns/prov#startedAtTime> ?activityTime ;
            <https://swissdatasciencecenter.github.io/renku-ontology#hasInputs> ?entityInput ;
            <https://swissdatasciencecenter.github.io/renku-ontology#command> ?activityCommand ;
            <https://swissdatasciencecenter.github.io/renku-ontology#hasOutputs> ?entityOutput ;
            <https://swissdatasciencecenter.github.io/renku-ontology#argument> ?entityArgument .

    """

    query_construct_from_config = ""

    if graph_nodes_subset_config is not None:
        for graph_nodes_subset_config_obj_key in graph_nodes_subset_config:
            graph_nodes_subset_config_obj = graph_nodes_subset_config[graph_nodes_subset_config_obj_key]
            if 'query_construct' in graph_nodes_subset_config_obj:
                query_construct_from_config += graph_nodes_subset_config_obj['query_construct']

    query_construct = f"""CONSTRUCT {{
        {query_construct_main}
        {query_construct_from_config}
    }}"""

    return query_construct


def analyze_types(g, type_label_values_dict):
    # analyze types
    types_list = g[:rdflib.RDF.type]
    for s, o in types_list:
        o_qname = g.compute_qname(o)
        s_label = label(s, g)
        if isinstance(s_label, rdflib.Literal):
            s_label = s_label.value
        type_label_values_dict[s_label] = o_qname[2]
        g.remove((s, rdflib.RDF.type, o))
        g.add((s, rdflib.RDF.type, rdflib.Literal(o_qname[2])))


def label(x, g):
    for labelProp in LABEL_PROPERTIES:
        l = g.value(x, labelProp)
        if l:
            return l
    try:
        return g.namespace_manager.compute_qname(x)[2]
    except:
        return x