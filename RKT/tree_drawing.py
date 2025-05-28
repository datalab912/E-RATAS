#planner layout
import matplotlib.pyplot as plt
import networkx as nx

def draw_rkt_tree(node, graph=None, pos=None, labels=None):
    if graph is None:
        graph = nx.DiGraph()
        labels = {}

    # Add the current node to the graph with a label
    labels[node.id] = f"ID: {node.id}"
    graph.add_node(node.id, label=f"ID: {node.id}")

    # Recursively add child nodes and edges to the graph
    for child in node.children:
        graph.add_edge(node.id, child.id)
        draw_rkt_tree(child, graph, labels=labels)

    return graph, labels

def tree_drawing(root_node, output_filename):
    graph, labels = draw_rkt_tree(root_node)

    # Apply a planar layout for better spacing, if possible
    try:
        pos = nx.planar_layout(graph)  # This layout raises an exception if graph is not planar
    except nx.NetworkXException:
        pos = nx.spring_layout(graph)  # Fallback to spring layout if graph is not planar
        print("Fallback to Spring Layout: The graph is not planar.")

    # Draw the graph
    plt.figure(figsize=(12, 8))
    nx.draw(graph, pos, labels=labels, with_labels=True, node_size=100, node_color='skyblue', font_size=10, font_color='darkred')
    plt.title('RKT Tree Visualization')

    # Save the plot to a file
    plt.savefig(output_filename, format='jpeg', dpi=300)  # Save as JPEG with higher DPI
    plt.close()

# Usage example:
# Assuming you have a defined root_node with child nodes
# tree_drawing(root_node, 'output_tree.jpeg')







#sprint layout
"""import matplotlib.pyplot as plt
import networkx as nx

def draw_rkt_tree(node, graph=None, pos=None, labels=None):
    if graph is None:
        graph = nx.DiGraph()
        labels = {}

    # Add the current node to the graph with a label
    labels[node.id] = f"ID: {node.id}"
    graph.add_node(node.id, label=f"ID: {node.id}")

    # Recursively add child nodes and edges to the graph
    for child in node.children:
        graph.add_edge(node.id, child.id)
        draw_rkt_tree(child, graph, labels=labels)

    return graph, labels

def tree_drawing(root_node, output_filename):
    graph, labels = draw_rkt_tree(root_node)

    # Apply a spring layout for better spacing
    pos = nx.spring_layout(graph)  # You can try different layouts like nx.planar_layout(graph)

    # Draw the graph
    plt.figure(figsize=(12, 8))
    nx.draw(graph, pos, labels=labels, with_labels=True, node_size=2000, node_color='skyblue', font_size=10, font_color='darkred')
    plt.title('RKT Tree Visualization')

    # Save the plot to a file
    plt.savefig(output_filename, format='jpeg', dpi=300)  # Save as JPEG with higher DPI
    plt.close()

# Usage example:
# tree_drawing(root_node, 'output_tree.jpeg')"""





# Simple display in google colab
"""from graphviz import Digraph

# Draw the a tree



def draw_rkt_tree(node, graph=None):
    if graph is None:
        graph = Digraph(comment='RKT Tree')

    # Add the current node to the graph
    graph.node(node.id, label=f"ID: {node.id}")

    # Recursively add child nodes and edges to the graph
    for child in node.children:
        graph.edge(node.id, child.id)
        draw_rkt_tree(child, graph)

    return graph

def tree_drawing(graph):
    rkt_graph = draw_rkt_tree(graph)
    display(rkt_graph))"""