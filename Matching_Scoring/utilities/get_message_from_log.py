from pathlib import Path
import re

from ACT.src.act import ACTTree, NodeType

# message_pattern = r"Message sent:\s*\[TextContentBlock\(text=Text\(annotations=\[\], value='(.+)'\), type='text'\]"
# response_pattern = r"Assistant Response:\s*(-.*)$"

message_pattern = r"Message sent:\s*\[TextContentBlock\(text=Text\(annotations=\[\], value=[\"\']Paragraph:\\n(.+)[\"\']\), type='text'\)]"
response_pattern = r"Assistant Response:\s*(.+)$"


def extract_messages(log_file_path):
    messages = {}
    message, response = None, None
    with open(log_file_path, "r") as file:
        for line in file:
            response_match = re.search(response_pattern, line, flags=re.DOTALL)
            message_match = re.search(message_pattern, line, flags=re.DOTALL)

            if message_match:
                message = message_match.group(1).replace("\\n", "\n")
            if response_match:
                response = response_match.group(1)
            if message and response:
                print(message[:20], response[:20])
                # break
                messages[message[:20]] = response
                message, response = None, None  # Reset

    return messages


# sample_log_line = """2024-04-24 13:55:28,782 - ACT_Assistant - INFO - Message sent: [TextContentBlock(text=Text(annotations=[], value="Paragraph:\n13 \nFrom this point it will goes into representation point where we have three options to work \non clustering → similarity detection and classification. It depends on to what extends we \nwill go depends on the mentor. We can run more analysis by using these libraries and make \nit vaster by running emotion recognition, object detection, classification based on what \nclasses and also it should be representational and create and API for representation of this \nproject where we can see the full potential of this application.  \nOutcome of the project:  \nPoint of the undertaking is to effectively perceive understudy in a web-based test and can \nfollow understudy's class participation. These days due to Coronavirus pandemic connection \namong understudy and educator is nearly non-existent and extremely less intelligent. So, \nwhen understudy wanted to skirt the class and attempt to hoodwink the instructor to get a \nfree participation for the class, this framework wouldn't allow them to get it done. It will \nperceive understudy face with it put away data set coordinate with understudy separate id \nand fill the participation and store it in a succeed sheet with having every one of the \nindividual subtleties of the understudy."), type='text')], thread_id: thread_8F63PkH4UVSmG1U6RbbKq9X2"""
# print(re.search(message_pattern, sample_log_line, flags=re.DOTALL).group(1))

# Example Usage
log_file = "logs/app.log"
extracted_messages = extract_messages(log_file)

# for message_dict in extracted_messages:
#     print("Message Sent:", message_dict["message"])
#     print("Assistant Response:", message_dict["response"])
#     print("------")

act_tree = ACTTree(Path("data/processed/act/45698120.json"))
for node in act_tree.root.post_order_iter():
    if node.nodeType == NodeType.PARAGRAPH:
        node.goal = extracted_messages.get(node.text[:20])
        if not node.goal:
            print(f"Goal not found for paragraph: {node.text[:100]}, {node.id}")
    if node.nodeType == NodeType.TITLE:
        node.goal = node.text
    elif node.nodeType == NodeType.SECTION:
        union_goal = ""
        for child in node.children:
            if child.goal:
                union_goal += child.goal + "\n"
        node.goal = union_goal
act_tree.export_json(Path("data/processed/act/45698120_with_goals.json"))
# print(extracted_messages)
