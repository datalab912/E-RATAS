from anytree import NodeMixin, PreOrderIter, PostOrderIter, findall_by_attr, NodeMixin, find as find_node
from converting_RKT_ACT import ACTNode, RKTNode, load_tree, write_rkt_to_json, display_table 
import random
# from GPT_assistant.score_01 import SR_01_Assistant
# from GPT_assistant.score_100_whole import SR_100_WHOLE_Assistant
# from GPT_assistant.score_100 import SR_100_Assistant
import re

def reason_story(rkt_path,txt_path):
    
    rkt_tree = load_tree(rkt_path, RKTNode)
    flat_main_reason = flatten_list(rkt_tree.main_reason)

    i = 0
    with open(txt_path, 'w') as file:
        for reason in flat_main_reason:
            i += 1
            x = find_node_by_id(rkt_tree, reason.get('id'))
            file.write(f"{i}: based on simplest criterion number with ID {reason.get('id')} which is: {x.criteria} from score source: {reason.get('score_source')}\n")
            file.write(f"has been gain {reason.get('rewarded_score')} from {reason.get('related_part')} part of the answer\n")
            file.write(f"because of the reason: {reason.get('reason')} \n\n\n")



def flatten_list(nested_list):
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))
        else:
            flat_list.append(item)
    return flat_list

def find_node_by_id(root, target_id):
    for node in PreOrderIter(root):
        if node.id == target_id:
            return node
    return None