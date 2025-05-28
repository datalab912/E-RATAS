import json
import pandas as pd
#from GPT_assistant.topic_modelling import TM_Assistant
import re
from openai import AzureOpenAI
import time

client = AzureOpenAI(
    azure_endpoint="https://prd-auae-core-oai-apim-01.azure-api.net/prd-auae-core-openai-api-02/",
    api_key="a1d43fe4425c41cdb5913f551bcd5b5d",
    api_version="2024-05-01-preview"
)

class RKTNode:
    def __init__(self, id, leaf=0, criteria=None, criteria_simplified_version=None, separate_criteria_number=0, title=None, related_answer_section=None, score_source_ID=None, score_source=None, influence_type=None, influence_on_scoring=100, list_sub_condition_score=None, score_breakdown=None, matching_percentage=None, reasons=None, score=None, influence_section_type=None):
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
        self.children = []

    def display(self, level=0):
        print('  ' * level + f'ID: {self.id}, Title: {self.title}')
        for child in self.children:
            child.display(level + 1)

    def to_dict(self):
        return {
            'id': self.id,
            'leaf': self.leaf,
            'criteria': self.criteria,
            'criteria_simplified_version': self.criteria_simplified_version,
            'separate_criteria_number': self.separate_criteria_number,
            'title': self.title,
            'related_answer_section': self.related_answer_section,
            'score_source_ID': self.score_source_ID,
            'score_source': self.score_source,
            'influence_type': self.influence_type,
            'influence_on_scoring': self.influence_on_scoring,
            'list_sub_condition_score': self.list_sub_condition_score,
            'score_breakdown': self.score_breakdown,
            'matching_percentage': self.matching_percentage,
            'reasons': self.reasons,
            'score': self.score,
            'influence_section_type': self.influence_section_type,
            'children': [child.to_dict() for child in self.children]
        }
    
    @staticmethod
    def from_dict(data):
        node = RKTNode(
            id=data['id'],
            leaf=data['leaf'],
            criteria=data['criteria'],
            criteria_simplified_version=data['criteria_simplified_version'],
            separate_criteria_number=data['separate_criteria_number'],
            title=data['title'],
            related_answer_section=data['related_answer_section'],
            score_source_ID=data['score_source_ID'],
            score_source=data['score_source'],
            influence_type=data['influence_type'],
            influence_on_scoring=data['influence_on_scoring'],
            list_sub_condition_score=data['list_sub_condition_score'],
            score_breakdown=data['score_breakdown'],
            matching_percentage=data['matching_percentage'],
            reasons=data['reasons'],
            score=data['score'],
            influence_section_type=data['influence_section_type']
        )
        for child_data in data['children']:
            node.children.append(RKTNode.from_dict(child_data))
        return node
    

def load_tree_from_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
        return RKTNode.from_dict(data)


def save_RKT_to_json(tree_root, filename):
    with open(filename, 'w') as file:
        json.dump(tree_root.to_dict(), file, indent=4)


def Constructing_Rubric_based_Tree(rubric_id, rubric_table, list_of_concepts, complexity_threshold):
    # Create the RKT tree with root node R
    R = RKTNode(id=rubric_id, leaf=1, title="all criteria", influence_on_scoring=100)
    R.separate_criteria_number = len(rubric_table)

    # Aggregate information from the rubric table into the root node
    for row in rubric_table:
        R.criteria_simplified_version.append(row['Basic-Criteria'])
        R.related_answer_section.append(row['Answer-Section'])
        R.score_source.append(row['Score-Source'])  # Assuming 'Score-Source' is correct
        R.list_sub_condition_score.append(row['Conditions'])  # Assuming 'Conditions' contains sub-condition scores
        R.score_source_ID.append(row['ID'])

    # Expand the tree by adding child nodes to leaf nodes
    nodes_to_expand = [R]  # Start with the root node
    while nodes_to_expand:
        node = nodes_to_expand.pop(0)  # Get the first node to expand
        if node.leaf == 1 and node.separate_criteria_number !=1:
            Node_Expansion_Function(R, node)  # Expand the node
            nodes_to_expand.extend(node.children)  # Add new child nodes to the list of nodes to expand

    title_generation(R)

    return R

def Node_Expansion_Function(R, N):
  N.leaf = 0  # Mark N as no longer a leaf node

  for x in range(N.separate_criteria_number):
    # Create a new child node M of N
    M = RKTNode(id=f"{N.id}.{x+1}", leaf=1)
    N.children.append(M)

    M.criteria = N.criteria_simplified_version[x]
    M.influence_section_type = "partial"

    flag = 0
    """*****************WHOLE********************"""
    if N.influence_section_type == "whole_section":
        M.influence_section_type = "whole_section"
    elif P:=is_whole_format(M.criteria):
        M.influence_section_type = "whole_section"
        M.criteria = P
    
    """*****************ESSENTIAL****************"""
    if N.influence_type == "essential":
        M.influence_type = "essential"
    if P:=is_essential_format(M.criteria):
        M.influence_type = "essential"
        M.criteria = P
    P,O = has_essential_part(M.criteria)
    O = f"{{{O}{{ESSENTIAL}}}}"
    if O:
        M.criteria_simplified_version = [None]
        M.criteria_simplified_version[0]= O
        M.criteria_simplified_version.extend(AzureLLM_One_Level_categorization(P))
        flag=1
        
    """********************OR*******************"""
    if P:=is_OR_format(M.criteria):
        M.influence_type = "or"
        M.criteria_simplified_version = P
        flag=2

    if flag == 0:
        M.criteria_simplified_version  = AzureLLM_One_Level_categorization(M.criteria)
    
        

    # Placeholder for LLM-based categorization and title generation
    
    M.separate_criteria_number = len(M.criteria_simplified_version)
    #M.title = LLM_Criteria_Title(N.title, M.criteria)

    # Placeholder for updating related answer sections based on subsections
    """This requires a function to check for subsections in criteria and update accordingly"""

    
    
    if N.id.count('.') == 1:
      # Check if N is a child of R (not directly)
      M.influence_on_scoring = R.score_source[x]
      M.related_answer_section = R.related_answer_section[x]
      M.score_source=R.score_source[x]
      M.score_source_ID=R.score_source_ID[x]
      M.list_sub_condition_score = R.list_sub_condition_score[x]
    else:
      if flag == 1:
          M.influence_on_scoring = N.influence_on_scoring / ((N.separate_criteria_number)-1)
      M.influence_on_scoring = N.influence_on_scoring / (N.separate_criteria_number)
      M.related_answer_section = N.related_answer_section
      M.score_source = N.score_source
      M.score_source_ID = N.score_source_ID
      # Placeholder for LLM-based subcriteria division
      """M.list_sub_condition_score = LLM_Subcriteria_division(M.criteria_simplified_version, N.list_sub_condition_score[x])"""
      M.list_sub_condition_score = LLM_Subcriteria_division(M.criteria_simplified_version, N.list_sub_condition_score)


def collect_rkt_nodes(node, nodes_list=None):
    if nodes_list is None:
        nodes_list = []

        # Collect the current node's attributes
    node_attributes = {
        'ID': node.id,
        'leaf': node.leaf,
        'criteria': node.criteria,
        'criteria_simplified_version': '\n*** '.join(node.criteria_simplified_version),
        'separate_criteria_number': node.separate_criteria_number,
        'Title': node.title,
        'related_answer_section': '\n --'.join(node.related_answer_section),
        """'score_source_ID': node.score_source_ID,"""
        'score_source_ID': '\n --'.join(str(item) for item in node.score_source_ID),
        'score_source': '\n --'.join(node.score_source),
        """'score_source': node.score_source,"""
        'Influence Type': node.influence_type,
        'Influence on Scoring': node.influence_on_scoring,
        'list_sub_condition_score': '\n --'.join(node.list_sub_condition_score),
        """'list_sub_condition_score': node.list_sub_condition_score,"""
        'score_breakdown': '\n --'.join(node.score_breakdown),
        'matching_percentage': '\n --'.join(node.matching_percentage),
        'reasons': '\n --'.join(node.reasons),
        'score':node.score,
        'influence_section_type': node.influence_section_type
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

    # Display the DataFrame as a table
    nodes_df.to_excel('.\output\RKT.xlsx', index=False)

def is_whole_format(text):

    pattern = r'\{(.*?)\{WHOLE\}\}'
    # Search for the pattern in the text
    match = re.fullmatch(pattern, text)
    if match:
        return match.group(1)
    else:
        return None

def is_essential_format(text):
    pattern = r'\{(.*?)\{ESSENTIAL\}\}'
    # Search for the pattern in the text
    match = re.fullmatch(pattern, text)
    if match:
        return match.group(1)
    else:
        return None

def has_essential_part(input_text):
    # Regular expression to match the pattern { ... {ESSENTIAL}}
    pattern = r'\{(.*?)\{ESSENTIAL\}\}'
    
    # Find all matches in the text
    essential_parts = re.findall(pattern, input_text)
    
    # Check if there are no matches
    if not essential_parts:
        return None, None
    
    # Remove all matches from the original text
    non_essential_text = re.sub(pattern, '', input_text)
    
    # Join the essential parts to form the second output
    essential_text = ''.join(essential_parts)
    
    # Return both outputs
    return non_essential_text, essential_text


def is_OR_format(input_text):
    if not (input_text.startswith("{") and input_text.endswith("}")):
        return None
    
    # Step 2: Remove the starting "{{" and ending "}}"
    inner_text = input_text[1:-1]

    if "OR" not in inner_text:
        return None
    
    # Step 3: Split the text by "OR"
    parts = inner_text.split("OR")
    
    # Step 4: Initialize the list to hold the extracted texts
    extracted_texts = []
    
    for part in parts:
        # Check that each part starts with "{" and ends with "}"
        if not (part.startswith("{") and part.endswith("}")):
            return None
        # Step 5: Remove the starting "{" and ending "}" and add to the list
        extracted_texts.append(part[1:-1])
    
    return extracted_texts

# def LLM_One_Level_categorization(criteria):
    
#     assistant = TM_Assistant()
#     assistant.add_message_to_thread("The new provided rubric criterion is:\n" + criteria + "\n follow the instructions of this thread and examples (provided at the first messages of this thread) to generate the sub-criteria for the new provided criterion")
    
#     output = assistant.run_assistant_single_time()

#     import re

#     # Use regular expression to find all occurrences of subcriteria
#     subcriteria = re.findall(r'\*\*\*([^\*]+)', output)
#     # Clean and trim whitespace from each subcriteria
#     subcriteria = [criterion.strip() for criterion in subcriteria]
#     return subcriteria

#     """assistant.run_assistant_single_text(instructions="use these examples and follow the instructions and rules to generate the sub-criteria")"""


        
def title_generation(node):
    if node.leaf:
        node.title = AzureLLM_Criteria_Title(node.criteria)  # Assuming FFF is a predefined function
        z=1
    else:
        child_titles = set()
        for child in node.children:
            title_generation(child)
            child_titles.update(child.title.split())
        node.title = ' '.join(child_titles)

# def LLM_Criteria_Title(criteria):
#     from GPT_assistant.criteria_titling import CT_Assistant
#     assistant = CT_Assistant()
#     assistant.add_message_to_thread("very good, do again for the next provided rubric criterion:\n" + criteria + "like the previous message, follow the instructions and examples to generate the related feature-based title")
    
#     output = assistant.run_assistant_single_time()

#     return output  # Simplified placeholder return

"""???????"""
def LLM_Subcriteria_division(criteria_simplified_version, list_sub_condition_score):
    Test_List = ["subcondition 1", "subcondition 2"]
    return list_sub_condition_score  # Simplified placeholder return





def AzureLLM_One_Level_categorization(criteria):
    
    from openai import AzureOpenAI

    assistantID="asst_ExIhfWIhQf4kIkETY2rsrWWS"
    threadID = "thread_cFuFloDxQsoPUMbcbUwStVZZ"

    output = OpenAIResponse(criteria, "Topic", assistantID, threadID)


    import re

    # Use regular expression to find all occurrences of subcriteria
    subcriteria = re.findall(r'\*\*\*([^\*]+)', output)
    # Clean and trim whitespace from each subcriteria
    subcriteria = [criterion.strip() for criterion in subcriteria]
    return subcriteria

    """assistant.run_assistant_single_text(instructions="use these examples and follow the instructions and rules to generate the sub-criteria")"""

       


def AzureLLM_Criteria_Title(criteria):

    from openai import AzureOpenAI

    assistantID="asst_swrTGGXEI8yKOiV7YhvUein2"
    threadID = "thread_JxCHdwI1QI7BlaYM57Hkr4mP"
    
    output = OpenAIResponse(criteria, "Title", assistantID, threadID)
    
    return output





def OpenAIResponse(criteria, Type, assistant_id, thread_id):
    """
    Generate a response from Azure OpenAI Assistant API.
    """
    

    if Type == "Title":
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=f"very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions and examples to generate the related feature-based title for the new criterion. The new provided rubric criterion is: {criteria}"
            #, If previuse messages of this thread is related to the User New Query consider them to response response for the User New Query."
        )
    else:
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=f"very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: {criteria}"
        )
    
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    while run.status in ['queued', 'in_progress', 'cancelling']:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )

    if run.status == 'completed':
        messages = client.beta.threads.messages.list(thread_id=thread_id)

        # Iterate through messages to get the latest assistant response
        response_text = None
        for message in messages:
            print(message)
            if message.role == "assistant":
                response_text = message.content
                break

        if response_text:
            output = extract_text(response_text)
            return output
        else:
            raise Exception("No assistant response found.")



def extract_text(object):
    """
    Extracts the actual title text from the given title response.

    Args:
        object (list): The title response from OpenAI which contains nested objects.

    Returns:
        str: The extracted title text.
    """
    if isinstance(object, list) and len(object) > 0:
        # Access the first TextContentBlock, then navigate to the value
        text_block = object[0]
        if hasattr(text_block, 'text') and hasattr(text_block.text, 'value'):
            return text_block.text.value
    raise ValueError("Unable to extract title text from the response.")
