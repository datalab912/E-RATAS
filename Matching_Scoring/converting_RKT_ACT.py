import json
from anytree import NodeMixin, RenderTree, findall
from enum import Enum
import pandas as pd

# Node type enumeration
class NodeType(Enum):
    SECTION = "section"
    PARAGRAPH = "paragraph"
    CAPTION = "caption"
    IMAGE = "image"
    TABLE = "table"
    TITLE = "title"
    ROOT = "root"

# ACT Node class
class ACTNode(NodeMixin):
    def __init__(self, id, name, nodeType, text=None, page=None, goal=None, parent=None, children=None, thread_id=None):
        super().__init__()
        self.id = id
        self.name = name
        self.nodeType = NodeType(nodeType)
        self.text = text
        self.page = page
        self.goal = goal
        self.parent = parent
        if children:
            self.children = [ACTNode(**child) for child in children]
        self.thread_id = thread_id

# RKT Node class
class RKTNode(NodeMixin):
    def __init__(self, id, leaf=0, criteria=None, criteria_simplified_version=None, separate_criteria_number=0, title=None, related_answer_section=None, score_source_ID=None, score_source=None, influence_type=None, influence_on_scoring=100, list_sub_condition_score=None, score_breakdown=None, matching_percentage=None, reasons=None, score=None, influence_section_type=None, main_reason=None, children=None):
        super().__init__()
        self.id = id
        self.leaf = leaf
        self.criteria = criteria
        self.criteria_simplified_version = criteria_simplified_version or []
        self.separate_criteria_number = separate_criteria_number
        self.title = title
        self.related_answer_section = related_answer_section or []
        self.score_source_ID = score_source_ID or []
        self.score_source = score_source or []
        self.influence_type = influence_type
        self.influence_on_scoring = influence_on_scoring
        self.list_sub_condition_score = list_sub_condition_score or []
        self.score_breakdown = score_breakdown or []
        self.matching_percentage = matching_percentage or []
        self.reasons = reasons or []
        self.score = score
        self.influence_section_type = influence_section_type
        self.main_reason = main_reason or []
        if children:
            self.children = [RKTNode(**child) for child in children]

# Function to load JSON and build tree
def load_tree(json_file, node_class):
    #with open(json_file, 'r') as file:
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return node_class(**data)

# Example of how to use these functions


# Print the trees for verification


def serialize_rkt_node(node):
    """ Recursively serialize an RKTNode into a dictionary. """
    node_dict = {
        'id': node.id,
        'leaf': node.leaf,
        'criteria': node.criteria,
        'criteria_simplified_version': node.criteria_simplified_version,
        'separate_criteria_number': node.separate_criteria_number,
        'title': node.title,
        'related_answer_section': node.related_answer_section,
        'score_source_ID': node.score_source_ID,
        'score_source': node.score_source,
        'influence_type': node.influence_type,
        'influence_on_scoring': node.influence_on_scoring,
        'list_sub_condition_score': node.list_sub_condition_score,
        'score_breakdown': node.score_breakdown,
        'matching_percentage': node.matching_percentage,
        'reasons': node.reasons,
        'score': node.score,
        'influence_section_type': node.influence_section_type,
        'main_reason' : node.main_reason,
        'children': [serialize_rkt_node(child) for child in node.children] if node.children else []
    }
    return node_dict

def write_rkt_to_json(rkt_root, file_path):
    """ Write the serialized RKT tree to a JSON file. """
    with open(file_path, 'w') as json_file:
        json.dump(serialize_rkt_node(rkt_root), json_file, indent=4)


def collect_rkt_nodes(node, nodes_list=None):
    if nodes_list is None:
        nodes_list = []

        # Collect the current node's attributes
    node_attributes = {
        'ID': node.id,
        'leaf': node.leaf,
        'criteria': node.criteria,
        'criteria_simplified_version': '\n*** '.join(item for item in node.criteria_simplified_version),
        'separate_criteria_number': node.separate_criteria_number,
        'Title': node.title,
        'related_answer_section': '\n --'.join(item for item in node.related_answer_section),
        'score_source_ID': str(node.score_source_ID),
        'score_source': str(node.score_source),
        'Influence Type': node.influence_type,
        'Influence on Scoring': node.influence_on_scoring,
        """'list_sub_condition_score': '\n --'.join(node.list_sub_condition_score),"""
        'list_sub_condition_score': node.list_sub_condition_score,
        'score_breakdown': '\n --'.join(str(item) for item in node.score_breakdown),
        'matching_percentage': '\n --'.join(str(percentage) for percentage in node.matching_percentage),
        'reasons': '\n --'.join(str(reason) for reason in node.reasons),
        'score':node.score,
        'influence_section_type': node.influence_section_type,
        'main_reason' : '\n --'.join(str(item) for item in node.main_reason),
    }
    nodes_list.append(node_attributes)

    # Recursively collect attributes from child nodes
    for child in node.children:
        collect_rkt_nodes(child, nodes_list)
    return nodes_list

def display_table(node):

    node_list=[]      
    # Collect node attributes into a list of dictionaries
    nodes_data = collect_rkt_nodes(node, node_list)

    # Create a DataFrame from the collected node attributes
    nodes_df = pd.DataFrame(nodes_data)
    #?????????
    # # Display the DataFrame as a table
    # nodes_df.to_excel('.//output//new_RKT.xlsx', index=False)