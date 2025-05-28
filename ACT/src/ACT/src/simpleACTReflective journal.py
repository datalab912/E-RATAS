import fitz  # PyMuPDF
import re
import json
from anytree import NodeMixin
from enum import Enum
import os

# -----------------------------------------------------------
# Example NodeType enum (adapt to your own implementation)
# -----------------------------------------------------------
class NodeType(Enum):
    SECTION = "section"
    TITLE = "title"
    PARAGRAPH = "paragraph"

# -----------------------------------------------------------
# Custom ACTNode class
# -----------------------------------------------------------
class ACTNode(NodeMixin):
    def __init__(self, id, name, nodeType, text=None, page=None, goal=None, 
                 parent=None, children=None, thread_id=None):
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

# -----------------------------------------------------------
# Helper function to get the first three words of a text
# -----------------------------------------------------------
def three_first_words(text: str) -> str:
    """
    Returns the first three words from 'text'. 
    If fewer than three words exist, returns however many words there are.
    """
    words = text.split()
    return " ".join(words[:3])

# -----------------------------------------------------------
# Main function to read PDF, extract weeks, build ACT tree
# -----------------------------------------------------------
def extract_week_sections_act_tree(pdf_path):
    # 1) Read the PDF and extract text in lowercase
    doc = fitz.open(pdf_path)
    pdf_text = ""
    for page in doc:
        pdf_text += page.get_text()
    pdf_text = pdf_text.lower()  # convert to lowercase

    # 2) Identify the first "week #"
    week_pattern = re.compile(r'week\s+(\d+)')
    first_week_match = week_pattern.search(pdf_text)
    if not first_week_match:
        print("No 'week #' pattern found in the PDF.")
        return None

    # First discovered week number
    current_section = int(first_week_match.group(1))

    # Start of target text from the position of this first "week #"
    start_of_target = first_week_match.start()

    # Find the first "work sample" after that position
    work_sample_pos = pdf_text.find("work sample", start_of_target)
    if work_sample_pos != -1:
        target_text = pdf_text[start_of_target:work_sample_pos]
    else:
        target_text = pdf_text[start_of_target:]

    # ----------------------------------------------------------
    # Slice target_text into { week_num: content }
    # ----------------------------------------------------------
    sections = {}
    current_week = current_section
    current_search_pos = 0

    while True:
        # Pattern for "week x"
        pattern_current = re.compile(rf'week\s+{current_week}\b')
        match_current = pattern_current.search(target_text, current_search_pos)
        if not match_current:
            # Cannot find "week x"; stop
            break

        # Look for "week x+1"
        next_week = current_week + 1
        pattern_next = re.compile(rf'week\s+{next_week}\b')
        match_next = pattern_next.search(target_text, match_current.end())

        if match_next:
            # Extract the text from this week to next
            section_text = target_text[match_current.start():match_next.start()].strip()
            sections[current_week] = section_text
            current_search_pos = match_next.start()
            current_week += 1
        else:
            # No next week found; take remainder
            section_text = target_text[match_current.start():].strip()
            sections[current_week] = section_text
            break

    # ----------------------------------------------------------
    # Build the ACT tree
    # ----------------------------------------------------------
    root_node = ACTNode(
        id="1",
        name="Reflective journal Entities",  # root name
        nodeType="section",
        text=target_text,
        page=None,
        goal="Reflective journal Entities",  # root goal
        parent=None
    )

    child_id_counter = 1
    # Sort the week keys in ascending order
    for week_num in sorted(sections.keys()):
        # 1) Title node
        title_text = f"week {week_num}"
        title_name = three_first_words(title_text) or title_text
        title_id = f"1.{child_id_counter}"
        child_id_counter += 1

        ACTNode(
            id=title_id,
            name=title_name,
            nodeType="title",
            text=title_text,
            page=None,
            goal=title_text,   # goal = entire text
            parent=root_node
        )

        # 2) Paragraph node
        paragraph_text = sections[week_num]
        paragraph_name = three_first_words(paragraph_text) or "No content"
        paragraph_id = f"1.{child_id_counter}"
        child_id_counter += 1

        ACTNode(
            id=paragraph_id,
            name=paragraph_name,
            nodeType="paragraph",
            text=paragraph_text,
            page=None,
            goal=paragraph_text,  # goal = entire text
            parent=root_node
        )

    return root_node

# -----------------------------------------------------------
# Convert an ACTNode tree to a nested dictionary
# -----------------------------------------------------------
def act_node_to_dict(node: ACTNode) -> dict:
    """
    Recursively convert an ACTNode (with children) into a dictionary 
    suitable for JSON serialization.
    """
    # Prepare the base dictionary for this node
    node_dict = {
        "id": node.id,
        "name": node.name,
        "nodeType": node.nodeType.value,
        "text": node.text,
        "page": node.page,
        "goal": node.goal,
        "children": []
    }

    # Add children (recursively)
    for child in node.children:
        node_dict["children"].append(act_node_to_dict(child))

    return node_dict

# -----------------------------------------------------------
# Example usage
# -----------------------------------------------------------
# if __name__ == "__main__":
#     # Example PDF path
#     pdf_file_path = "src/ACT/src/input/s1-2022_46116761_Final Internship Report_SupriyaBasnet-pages.pdf"
#     # Where you want to save the resulting JSON
#     output_json_path = "src/ACT/src/output/s1-2022_46116761_Final Internship Report_SupriyaBasnet-pages.json"

#     # 1) Build the ACT tree
#     act_root = extract_week_sections_act_tree(pdf_file_path)
#     if not act_root:
#         print("No ACT tree created (no 'week #' found). Exiting.")
#         exit()

#     # 2) Convert the tree to a dictionary
#     root_dict = act_node_to_dict(act_root)

#     # 3) Write JSON to file
#     #    Use ensure_ascii=False to keep non-ASCII characters as is
#     #    and indent=4 for pretty printing
#     with open(output_json_path, "w", encoding="utf-8") as out_file:
#         json.dump(root_dict, out_file, ensure_ascii=False, indent=4)

#     print(f"ACT tree has been successfully written to {os.path.abspath(output_json_path)}")

# -----------------------------------------------------------
# Process an entire folder of PDFs -> produce JSONs
# -----------------------------------------------------------
def process_pdfs_in_folder(input_folder):
    """
    For each .pdf file in 'input_folder', generate a .json file in the same folder
    with the same base name.
    """
    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_folder, filename)

            # 1) Build the ACT tree
            act_root = extract_week_sections_act_tree(pdf_path)
            if not act_root:
                # If no "week #" found, skip or handle differently
                print(f"Skipping {filename} (no 'week #' pattern found).")
                continue

            # 2) Convert the tree to a dictionary
            root_dict = act_node_to_dict(act_root)

            # 3) Write JSON to file (same name, .json extension)
            base_name = os.path.splitext(filename)[0]
            output_folder="src/ACT/src/output"
            output_json_path = os.path.join(output_folder, base_name + ".json")

            with open(output_json_path, "w", encoding="utf-8") as out_file:
                json.dump(root_dict, out_file, ensure_ascii=False, indent=4)

            print(f"Processed: {filename} -> {base_name}.json")

# -----------------------------------------------------------
# Example usage
# -----------------------------------------------------------
if __name__ == "__main__":
    # Change this to the folder path containing your PDFs
    folder_path = "src/ACT/src/input"
    process_pdfs_in_folder(folder_path)