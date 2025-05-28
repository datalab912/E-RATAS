from anytree import NodeMixin, PreOrderIter, PostOrderIter, findall_by_attr, NodeMixin, find as find_node
from converting_RKT_ACT import ACTNode, RKTNode, load_tree, write_rkt_to_json, display_table 
import random
#????????????
# from GPT_assistant.score_01 import SR_01_Assistant
# from GPT_assistant.score_100_whole import SR_100_WHOLE_Assistant
# from GPT_assistant.score_100 import SR_100_Assistant
import re
from openai import AzureOpenAI
import time
#from sentence_transformers import SentenceTransformer, util

client = AzureOpenAI(
    azure_endpoint="https://prd-auae-core-oai-apim-01.azure-api.net/prd-auae-core-openai-api-02/",
    api_key="a1d43fe4425c41cdb5913f551bcd5b5d",
    api_version="2024-05-01-preview"
)

# Enums and Node Classes are already defined by you
def scoring(rkt_json_path,act_json_path,matching_threshold, output_json_path):
    act_tree = load_tree(act_json_path, ACTNode)
    rkt_tree = load_tree(rkt_json_path, RKTNode)

    """for pre, _, node in RenderTree(act_tree):
    print(f"{pre}{node.name}")

    for pre, _, node in RenderTree(rkt_tree):
    print(f"{pre}{node.title}")"""

    scoring_reasoning(rkt_tree,act_tree,matching_threshold, output_json_path)

def scoring_reasoning(rkt_root, act_root, matching_limit, output_json_path):
    # Initialize all scores and reasons for each node in RKT
    initialize_rkt_tree(rkt_root, act_root)

    # Process each node in RKT recursively
    """"process_nodes(rkt_root, act_root, matching_limit)"""
    process_nodes_2(rkt_root, act_root, matching_limit)
    # Assuming `rkt_root` is your root node of the RKT tree
    write_rkt_to_json(rkt_root, output_json_path)
    display_table(rkt_root)


def initialize_rkt_tree(rkt_root, act_root):
    # Initialize scores, matching percentages, and reasons recursively
    for rkt_node in PreOrderIter(rkt_root):
        rkt_node.score_breakdown = {child.id: 0 for child in PreOrderIter(act_root)}
        rkt_node.matching_percentage = {child.id: 0 for child in PreOrderIter(act_root)}
        rkt_node.reasons = {child.id: [] for child in PreOrderIter(act_root)}

def process_nodes(rkt_node, act_root, matching_limit):
    RKT_ROOT= rkt_node
    if rkt_node.children:  # Non-leaf RKT nodes
        for child in rkt_node.children:
            process_nodes(child, act_root, matching_limit)
        update_internal_rkt_node(rkt_node, act_root, RKT_ROOT)
    else:  # Leaf RKT nodes
        process_leaf_rkt_node(rkt_node, act_root, matching_limit)


def process_nodes_2(rkt_root, act_root, matching_limit):
    s=0
    for N in PostOrderIter(rkt_root):
        print("N.id")
        if N.id == ".1.1.2.1":
            print(" ")
        if N.children:
            if s==0:
                #write_rkt_to_json(rkt_root, './/output//sample_RKT_with_scores.json')
                s=s+1
            update_internal_rkt_node(N, act_root, rkt_root)
            #write_rkt_to_json(rkt_root, './/output//sample_RKT_with_scores.json')
        else:  # Leaf RKT nodes
            process_leaf_rkt_node(N, act_root, matching_limit)


def process_leaf_rkt_node(rkt_node, act_root, matching_limit):
    N = rkt_node
    for M in PostOrderIter(act_root):
        if M.is_leaf:
            if N.influence_type is None:
                N.influence_type = "and"
            if N.influence_section_type == "whole_section":
                # Find the ACT node whose text matches the related_answer_section
                """?????"""
                matching_nodes = findall_by_attr(act_root, name='text', value=N.related_answer_section)
                if matching_nodes:
                    P = matching_nodes[0]
                    """?????"""
                    #section_text = find_section_text_function(P)  # Custom function to extract text
                    N.matching_percentage[P.id] = 100
                    N.score_breakdown[P.id], N.reasons[P.id] = Azurellm_scoring_function(N, P)  # Scoring based on section text
                    # Apply the same score and reason to all descendants of P
                    for descendant in P.descendants:
                        N.matching_percentage[descendant.id] = 100
                        N.score_breakdown[descendant.id] = N.score_breakdown[P.id]
                        N.reasons[descendant.id] = N.reasons[P.id]
            else:
                # Handle matching and scoring for leaf nodes not covered by 'whole_section'
                L, R = get_sibling_nodes(M)
                N.matching_percentage[M.id] = llm_rubric_paragraph_matching_function(
                    N, M.text, L.text if L else "", R.text if R else "", M.parent.goal if M.parent else "")
                if N.matching_percentage[M.id] > matching_limit:
                    N.score_breakdown[M.id], N.reasons[M.id] = Azurellm_scoring_function(N, M)
        else:
            # For non-leaf nodes in ACT, aggregate scores from children
            #child_scores = [child.score_breakdown[M.id] for child in M.children]
            max_score_child = max(M.children, key=lambda child: N.score_breakdown[child.id])
            N.matching_percentage[M.id] = max(N.matching_percentage[child.id] for child in M.children)
            N.score_breakdown[M.id] = N.score_breakdown[max_score_child.id]
            N.reasons[M.id] = N.reasons[max_score_child.id]

    # Update score source percentage for RKT node based on the scores of all leaf nodes in ACT
    leaf_nodes = [node for node in PostOrderIter(act_root) if node.is_leaf]
    #N.score = max((N.score_breakdown[leaf.id] for leaf in leaf_nodes), default=0)
    
    max_leaf = max(leaf_nodes, key=lambda leaf: N.score_breakdown.get(leaf.id, 0))

    # Extract the maximum score breakdown value from that leaf
    N.score = N.score_breakdown.get(max_leaf.id, 0)

    N.main_reason = N.reasons[max_leaf.id]

def update_internal_rkt_node(rkt_node, act_root, rkt_root):

    N=rkt_node
    es_child = None
    es=0

    # Iterate over each child and check the condition
    for child in N.children:
        if child.influence_type == "essential" and child.score == 0:
        #"""?????and child.is_leaf, """
            es_child = child
            es=1
            break
    
    if es:
        for M in PostOrderIter(act_root):
            N.score_breakdown[M.id] = 0
            N.matching_percentage[M.id] = sum(child.matching_percentage[M.id] for child in N.children) / len(N.children)
            N.reasons[M.id] = es_child.reasons[M.id]
        N.main_reason = es_child.main_reason
        N.score = 0
    
    elif N.influence_type == "or":
        max_score_child = max(N.children, key=lambda c: c.score, default=None)
        if max_score_child:
            for M in PostOrderIter(act_root):
                N.score_breakdown[M.id] = max_score_child.score_breakdown[M.id]
                N.matching_percentage[M.id] = sum(child.matching_percentage[M.id] for child in N.children) / len(N.children)
                N.reasons[M.id] = max_score_child.reasons[M.id]
                
            N.score = max_score_child.score
            N.main_reason = max_score_child.main_reason

    #elif N.influence_type in ["AND", "whole document" AND OTHERS]:
    else:
        for M in PostOrderIter(act_root):
            tem_score = 0
            for child in N.children:
                if child.is_leaf == 1:
                    tem_score = tem_score + child.influence_on_scoring * float(child.score_breakdown[M.id])
                else:
                    tem_score = tem_score + float(child.score_breakdown[M.id])
            N.score_breakdown[M.id] = tem_score
            #N.score_breakdown[M.id] = sum(child.influence_on_scoring * child.score_breakdown[M.id] for child in N.children)
            N.matching_percentage[M.id] = sum(child.matching_percentage[M.id] for child in N.children) / len(N.children)
            for child in N.children:
                if child.reasons[M.id]:
                    N.reasons[M.id].append(child.reasons[M.id])
        tem_score = 0
        for child in N.children:
            if child.is_leaf == 1:
                tem_score = tem_score + child.influence_on_scoring * child.score
            else:
                tem_score = tem_score + child.score
        N.score=tem_score
        #N.score = sum(child.influence_on_scoring * child.score for child in N.children)
        for child in N.children:
            N.main_reason.append(child.main_reason)
        #?????
        #write_rkt_to_json(rkt_root, './/output//sample_RKT_with_scores.json') 

    ees = 0
    for child in N.children:
        if child.influence_type == "essential":
        #"""?????and child.is_leaf, """
            es_child = child
            ees=1
            break
    #??????? just for the reflectiveJournal_light with differnet week as a seprate answer
    #??????? need more think more
    if ees:
        for M in PostOrderIter(act_root):
            if es_child.score_breakdown[M.id] == 0:
                N.score_breakdown[M.id] = 0
                N.reasons[M.id] = es_child.reasons[M.id]
                N.matching_percentage[M.id] = sum(child.matching_percentage[M.id] for child in N.children) / len(N.children)


# Placeholder functions for scoring and matching
# def llm_scoring_function(rkt_node, act_node):
#     # Implement scoring logic
#     if rkt_node.influence_section_type == "whole_section":
#         score, base_reason = llm_scoring_function_wholetext(rkt_node, act_node)
#     else:
#         text = act_node.text
#         assistant = SR_01_Assistant()
#         criterion = rkt_node.criteria
#         assistant.add_message_to_thread("The new provided text:\n" + text + "The newe provided criterion is:\n" + criterion  + "\n follow the instructions of this thread and examples (provided at the first messages of this thread) to generate the score and reasons of the text based on the criterion")
    
#         output = assistant.run_assistant_single_time()
#         score, base_reason = extract_score_reason_01(output)
#         if score ==None:
#             score = 0
#         score = float(score) 
    
#     reason = {
#         'id': rkt_node.id,
#         'score_source_id': rkt_node.score_source_ID,  # Example score source identifier
#         'score_source': rkt_node.score_source,  # Example score source percentage
#         'influence_of_scoring': rkt_node.influence_on_scoring,  # Example influence descriptor
#         'rewarded_score': score,  # The actual score calculated
#         'related_part': act_node.id,  # Text from the ACT node used for scoring
#         'reason': base_reason  # Placeholder reason
#     }
#     #llm_scoring_function(main_text, N.criteria, N.list_sub_condition_score,N.score_source_ID, N.influence_type)
#     return (score, reason) 


# def llm_scoring_function_wholetext(rkt_node, act_node):
#     #depth-first search
#     stack = [act_node]  # Start with the root node on the stack
#     i=0
#     while stack:  # While there are nodes to process...
#         node = stack.pop()  # Remove the top node from the stack
        
#         text = node.text
#         assistant = SR_100_WHOLE_Assistant()
#         assistant.add_message_to_thread("The next part of text is:\n" + text)
#         i=i+1
    
#         stack.extend(reversed(node.children)) 
#     criterion = rkt_node.criteria()

#     assistant.add_message_to_thread(content = f"""
#             Great work! Please repeat the process for the newly provided rubric criterion and text.


#             As with the previous messages, follow this thread’s instructions and examples to generate a score 
#             and explain the reasons behind that score.

#             The new rubric criterion is: {criterion}

#             This text includes the last {str(i)} user messages.
#             """)
                                    

#     output = assistant.run_assistant_single_time()
#     score, base_reason = extract_score_reason_100(output)

#     score = float(score)
#     # Example reason structure
#     reason = {
#         'id': rkt_node.id,
#         'score_source_id': rkt_node.score_source_ID,  # Example score source identifier
#         'score_source': rkt_node.score_source,  # Example score source percentage
#         'influence_of_scoring': rkt_node.influence_on_scoring,  # Example influence descriptor
#         'rewarded_score': score,  # The actual score calculated
#         'related_part': act_node.id,  # Text from the ACT node used for scoring
#         'reason': base_reason  # Placeholder reason
#     }
#     #llm_scoring_function(main_text, N.criteria, N.list_sub_condition_score,N.score_source_ID, N.influence_type)
#     return (score, reason)


def llm_rubric_paragraph_matching_function(rkt_node, main_text, l_text, r_text, p_goal):
    # Implement matching logic
    criteria = rkt_node.criteria
    criteria_title = rkt_node.criteria

    title_main_sim = sbert_similarity(criteria_title, main_text)
    criteria_main_sim = sbert_similarity(criteria, main_text)
    title_left_sim = sbert_similarity(criteria_title, l_text)
    title_right_sim = sbert_similarity(criteria_title, r_text)
    title_pgoal_sim = sbert_similarity(criteria_title, p_goal)
    
    matching_percentage = sum([0.5*title_main_sim, 0.2*criteria_main_sim, 0.1*title_left_sim, 0.1*title_right_sim, 0.1*title_pgoal_sim])
    
    #return random.choice([0.1, 0.15, 0.35])
    return 0.35

def sbert_similarity(title, text):
    # Function to check the similarity of the title with the paragraphs
    #def library_sample_check_function_new_sentence_model(library_sample_check_list, title):
    """model = SentenceTransformer('all-mpnet-base-v2')
    title_encoded = model.encode(title)
    paragraph_encoded = model.encode(text)
    similarity_score = round(util.pytorch_cos_sim(title_encoded, paragraph_encoded).item() * 100)"""
    return 0


def get_sibling_nodes(node):
    
    if node.parent is None:
        return None, None  # The node is a root node and has no siblings
    
    siblings = node.parent.children  # Get all children of the parent (i.e., all siblings including the node itself)
    index = siblings.index(node)  # Find the index of the node within its siblings
    
    # Determine the left sibling based on the index
    left_sibling = siblings[index - 1] if index > 0 else None
    
    # Determine the right sibling based on the index
    right_sibling = siblings[index + 1] if index < len(siblings) - 1 else None

    return left_sibling, right_sibling






#########################################################

def Azurellm_scoring_function(rkt_node, act_node):
    # Implement scoring logic
    from openai import AzureOpenAI

    #???????
    if act_node.nodeType.value == "title":
        score = 0
        base_reason = None
        reason = {
        'id': rkt_node.id,
        'score_source_id': rkt_node.score_source_ID,  # Example score source identifier
        'score_source': rkt_node.score_source,  # Example score source percentage
        'influence_of_scoring': rkt_node.influence_on_scoring,  # Example influence descriptor
        'rewarded_score': score,  # The actual score calculated
        'related_part': act_node.id,  # Text from the ACT node used for scoring
        'reason': base_reason  # Placeholder reason
        }
        return (score, reason)

    if rkt_node.influence_section_type == "whole_section":
        score, base_reason = Azurellm_scoring_function_wholetext(rkt_node, act_node)
    else:
        text = act_node.text
        criterion = rkt_node.criteria
        if NumberOfCall <100:
            SR_01assistantID="asst_vEejes0OOgoQ5CnNVsxhencf"
            SR_01threadID = "thread_HBRlksG6Ydc2kjxW8Lfjkm62"
        elif NumberOfCall <200:
            SR_01assistantID="asst_oUTu4myePXRABMAxauyngUi4"
            SR_01threadID = "thread_28Gu3IGLDRmsUT7Kq5JarMW2"
        elif NumberOfCall <300:
            SR_01assistantID="asst_9ct8JEETjTs6hTOUP4iXipn4"
            SR_01threadID = "thread_j2zfQnFqvnc4MIjRoXzvUbc5"
        else:
        #else NumberOfCall <400:
            SR_01assistantID="asst_1R8p2qle7W1yEwMmr6FdIm7q"
            SR_01threadID = "thread_Mb6oJTCMo4UiiRdEXpFkAp1j"
        # elif NumberOfCall <500:
        #     SR_01assistantID="asst_o9ZPgj1AIIw5z9kdSyNiUf6B"
        #     SR_01threadID = "thread_cCaKberNy1LkAR7wiAOTxL7O"
        # elif NumberOfCall <600:
        #     SR_01assistantID="asst_UqLi68g7R6oTmaFZA5JN1Kck"
        #     SR_01threadID = "thread_bMYz5YXP6iVd8ePssZ6qOfps"
        # elif NumberOfCall <700:
        #     SR_01assistantID="asst_v6PykWfNl0f6IInavKlJ74YK"
        #     SR_01threadID = "thread_Jnh9aAerGmv2ZimzCBhD1P9E"
        # elif NumberOfCall <800:
        #     SR_01assistantID="asst_eS8Q7jwRevlnZjbnhUbej0mO"
        #     SR_01threadID = "thread_6CrK3eV8rkyRlVAuZodSe5QU"
        # else:
        #     SR_01assistantID="asst_AjlDku7ItP4Bond9M7qXh7H2"
        #     SR_01threadID = "thread_VIxV74Do9wn2zrYEceuFSypn"
        
        SR_100assistantID="asst_d2q8R154WEmK3r7wqgQHBguW"
        SR_100threadID = "thread_GXWYaOo3w3y72LfUGaCLk2jt"

        base_reason = ""
    
        output = OpenAIResponse(text, criterion, "SR_01", SR_01assistantID, SR_01threadID)
        if output == None:
            print("none")

        score, base_reason = extract_score_reason_01(output)

        # output = OpenAIResponse(text, criterion, "SR_100", SR_100assistantID, SR_100threadID)

        # score, base_reason = extract_score_reason_100(output)
        if score ==None:
            score = 0
        score = float(score) 
    
    reason = {
        'id': rkt_node.id,
        'score_source_id': rkt_node.score_source_ID,  # Example score source identifier
        'score_source': rkt_node.score_source,  # Example score source percentage
        'influence_of_scoring': rkt_node.influence_on_scoring,  # Example influence descriptor
        'rewarded_score': score,  # The actual score calculated
        'related_part': act_node.id,  # Text from the ACT node used for scoring
        'reason': base_reason  # Placeholder reason
    }
    #llm_scoring_function(main_text, N.criteria, N.list_sub_condition_score,N.score_source_ID, N.influence_type)
    return (score, reason)




def Azurellm_scoring_function_wholetext(rkt_node, act_node):
    #depth-first search
    stack = [act_node]  # Start with the root node on the stack
    i=0
    
    SR_01assistantID="asst_5D6TFJPYWYlaaPJvtBhvxChR"
    SR_01threadID = "thread_JnyKi3iYcHkZm0zZ1MPL4NJB"

    SR_100assistantID="asst_d2q8R154WEmK3r7wqgQHBguW"
    SR_100threadID = "thread_GXWYaOo3w3y72LfUGaCLk2jt"

    combined_text = ""

    while stack:  # While there are nodes to process...
        node = stack.pop()  # Remove the top node from the stack

        # Collect the text from the node into one large string
        combined_text +=  node.text + "\n\n"
        i += 1

        # Push children to the stack
        stack.extend(reversed(node.children))

      

    criterion = rkt_node.criteria()

                                    

    output = OpenAIResponse(combined_text, criterion, "SR_01", SR_01assistantID, SR_01threadID)
    score, base_reason = extract_score_reason_01(output)

    # output = OpenAIResponse(text, criterion, "SR_100", SR_100assistantID, SR_100threadID)
    # score, base_reason = extract_score_reason_100(output)

    score = float(score)
    # Example reason structure
    reason = {
        'id': rkt_node.id,
        'score_source_id': rkt_node.score_source_ID,  # Example score source identifier
        'score_source': rkt_node.score_source,  # Example score source percentage
        'influence_of_scoring': rkt_node.influence_on_scoring,  # Example influence descriptor
        'rewarded_score': score,  # The actual score calculated
        'related_part': act_node.id,  # Text from the ACT node used for scoring
        'reason': base_reason  # Placeholder reason
    }
    #llm_scoring_function(main_text, N.criteria, N.list_sub_condition_score,N.score_source_ID, N.influence_type)
    return (score, reason)

NumberOfCall = 0

def OpenAIResponse(text, criteria, Type, assistant_id, thread_id):
    global NumberOfCall
    """
    Generate a response from Azure OpenAI Assistant API.
    """
    

    if Type == "SR_01":        
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content = f"Great work! Please repeat the process for the newly provided rubric criterion and text. As with the previous messages, follow this thread’s instructions and examples to generate a score, which is 0 or 1, and generate the reasons behind that score. The new rubric criterion is: {criteria}\n The new provided text is: {text}"
        )
    #Type == "SR_100"
    else:
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content= f"Great work! Please repeat the process for the newly provided rubric criterion and text. As with the previous messages, follow this thread’s instructions and examples to generate a score, which is number between 0 to 1, and generate the reasons behind that score. The new rubric criterion is: {criteria}\n The new provided text is: {text}"
        )
    
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    s=0
    while run.status in ['queued', 'in_progress', 'cancelling', 'failed']:
        if run.status == 'failed':
            run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
            time.sleep(1)
            continue

        time.sleep(1)
        s=s+1
        # if s > 10:
        #     print(s)

        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )

    if run.status != 'completed':
        print(None)

    if run.status == 'completed':
        NumberOfCall = NumberOfCall +1
        print(NumberOfCall)
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
            if output == None:
                print("none")
            return output
        else:
            print(None)
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


############################################################

def extract_score_reason_01(output):

    
    # Initialize variables to hold the score and the reason
    score = None
    reason = None

    # Split the output into lines
    # lines = output.split('\n')    
    # # Iterate through each line to find the score and reason
    # for line in lines:
    #     if line.startswith('SCORE:'):
    #         # Extract the score, removing the prefix and any leading/trailing whitespace
    #         score = line.replace('SCORE:', '').strip()
    #     #elif line.startswith('REASON:'):
    #     elif re.match(r'^\s+REASON:', line):
    #         # Extract the reason, removing the prefix and any leading/trailing whitespace
    #         reason = line.replace('REASON:', '').strip()


    import re

    # # Input string
    input_string = clean_input_text(output)
    # # Regular expression to extract SCORE and REASON
    # match = re.search(r"SCORE:\s*(\d+)\s*\n[\s\t\n]*REASON:\s*(.+)", input_string)

    pattern = re.compile(
        r"SCORE.*?:\s*(0(?:\.\d{1,2})?|1).*?REASON.*?:\s*(.+)",
        flags=re.IGNORECASE | re.DOTALL
    )

    
    match = pattern.search(input_string)

    if match:
        score = match.group(1).strip()
        reason = match.group(2).strip()
        print("Score:", score)
        print("Reason:", reason)
    else:
        print("Could not extract SCORE or REASON.")
    
    if score == None:
        print("Could not extract SCORE or REASON.")
    if reason ==None:
        print("Could not extract SCORE or REASON.")

    return score, reason

def clean_input_text(input_text: str) -> str:
    """
    Removes special characters (*, ', ") from the input text.
    """
    # Replace special characters with an empty string
    return re.sub(r"[*'\"]", "", input_text)


def extract_score_reason_100(output):
    # Split the output into lines
    lines = output.split('\n')
    
    # Initialize variables to hold the score and the reason
    score = None
    reason = None
    Nreason = None
    Preason = None
    
    # Iterate through each line to find the score and reason
    for line in lines:
        if line.startswith('SCORE:'):
            # Extract the score, removing the prefix and any leading/trailing whitespace
            score = line.replace('SCORE:', '').strip()
        elif line.startswith('NEGATIVE REASON:'):
            # Extract the reason, removing the prefix and any leading/trailing whitespace
            Nreason = line.replace('NEGATIVE REASON', '').strip()
        elif line.startswith('POSITIVE REASON:'):
            # Extract the reason, removing the prefix and any leading/trailing whitespace
            reason = line.replace('POSITIVE REASON', '').strip()
    
    return score, reason

def extract_score_reason_100_List_version(text):
    score_pattern = r"SCORE: (\d+)%"
    positive_pattern = r"POSITIVE REASONS:\s*(.*)\s*NEGATIVE REASONS:"
    negative_pattern = r"NEGATIVE REASONS:\s*(.*)"

    score = re.search(score_pattern, text)
    positives = re.search(positive_pattern, text, re.DOTALL)
    negatives = re.search(negative_pattern, text, re.DOTALL)

    score = int(score.group(1)) if score else None
    positives = positives.group(1).strip().split('\n') if positives else []
    negatives = negatives.group(1).strip().split('\n') if negatives else []

    # Clean up the lists by removing '*' and trimming whitespace
    positives = [item.strip('* ').strip() for item in positives if item.strip()]
    negatives = [item.strip('* ').strip() for item in negatives if item.strip()]

    return {
        "score": score,
        "positive_reasons": positives,
        "negative_reasons": negatives
    }
################################################################################################
NumberOfCall2 = 0

def Azure_direct_scoring(text):
    global NumberOfCall2
    """
    Generate a response from Azure OpenAI Assistant API.
    """
    if NumberOfCall2 <40:
        assistant_id="asst_EgdPGMWvguvwmo0UJG3jJLsd"
        thread_id = "thread_doIpmnha0vjWe5vDNsczn5TP"
    elif NumberOfCall2 <80:
        assistant_id="asst_02PsWDMcAzLfdCgQwzoAEpLt"
        thread_id = "thread_D4jYs6gCm36JRpKGFUPS1LIt"
    elif NumberOfCall2 <120:
        assistant_id="asst_re4Ci2fPGSujZvDpPSRufde0"
        thread_id = "thread_YbpgK7SNRzbsuxUwJbOo51lu"
    elif NumberOfCall2 <160:
        assistant_id="asst_6onGrPKz3Rg6U6b0Y9UEodve"
        thread_id = "thread_gl3EMlQFaphqD8ZSa6p0qLVV"
    elif NumberOfCall2 <200:
        assistant_id="asst_bsccSa9eeaOTDUdtGxmkt4dU"
        thread_id = "thread_DBrE9ooj504cNnMCsoN1XkM4"
    elif NumberOfCall2 <240:
        assistant_id="asst_adpOfXFzUkSAMIVhxNsDOYOe"
        thread_id = "thread_CpNbFnDtpC6rJzkYRNvyS1UL"
    elif NumberOfCall2 <280:
        assistant_id="asst_zSzXIUO3AKu4YLEXVO90XsAY"
        thread_id = "thread_OY7GeG8l6t3WpgJ8YnFFqv0S"
    elif NumberOfCall2 <320:
        assistant_id="asst_ew5ff0mdSfXr5LvN0nu6PLsj"
        thread_id = "thread_INJ2Q4s17hJcxi5pzOFZuK9I"
    elif NumberOfCall2 <360:
        assistant_id="asst_myD96ZXGoXEIRqdplbsecEYu"
        thread_id = "thread_aoCNlFtoIOcEmVBCS6TTgevE"
    elif NumberOfCall2 <400:
        assistant_id="asst_LjR8ymgmzVKjAGoeTW7Q4nmC"
        thread_id = "thread_lELUSMoroQl8MeT5zlD876mI"
    else:
        assistant_id="asst_WjnP8VHJUasuCsAOZPwNZOEw"
        thread_id = "thread_ZqTpmiCnTNZ58Oe7rijxlDXy"

    

    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content = f"Great work! Please repeat the process for the newly text. As with the previous messages, follow this thread’s instructions to generate a score. The new provided text is: {text}"
    )
    
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    s=0
    while run.status in ['queued', 'in_progress', 'cancelling', 'failed']:
        if run.status == 'failed':
            run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
            time.sleep(1)
            continue

        time.sleep(1)
        s=s+1
        # if s > 10:
        #     print(s)

        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )

    if run.status != 'completed':
        print(None)

    if run.status == 'completed':
        NumberOfCall2 = NumberOfCall2 +1
        print(NumberOfCall2)
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
            output = clean_input_text(output)
            if output == None:
                print("none")
                
            if float(output):
                return float(output)
            else:
                if output == '0.0' or output =='0.00' or output == '0.000':
                    return 0
                output = get_last_float(output)
                if output == '0.0':
                    return 0
                output = get_last_float(output)
                if output == '0.0':
                    return 0
                if float(output):
                    return float(output)
                else:
                    return 0
        else:
            print(None)
            raise Exception("No assistant response found.")
    return 0

import re

def get_last_float(text):
    """
    Extracts and returns the last float number mentioned in the input text.
    If no valid float is found, returns None.
    """
    # Regular expression to match float numbers (handles decimals and negatives)
    float_pattern = r"-?\d+\.\d+|-?\d+"

    # Find all matches in the text
    matches = re.findall(float_pattern, text)

    if matches:
        # Convert the last match to float and return
        return float(matches[-1])
    
    return None  # Return None if no float is found