from enum import Enum
from pathlib import Path
import fitz  # PyMuPDF
from anytree import NodeMixin, RenderTree
from anytree.exporter import JsonExporter
from anytree.iterators.levelorderiter import LevelOrderIter
from anytree.iterators.postorderiter import PostOrderIter
from anytree.render import AsciiStyle
from json import JSONEncoder
from pathlib import Path

from redis import Redis
from rq import Queue, get_current_job
from rq.job import Job
from text_validity_check import get_sections_from_text, validate_section_order
from log.log import Log

import pika
import json
from pathlib import Path
import numpy as np

import os

from pdf_utls import (
    extract_content_for_header,
    get_section_text,
    split_into_paragraphs,
    is_title,
)
from assistant import ACTAssistant

logger = Log("act", "act.log")


class NodeTypeEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, NodeType):
            return obj.value
        return super().default(obj)


class NodeType(Enum):
    SECTION = "Section"
    PARAGRAPH = "Paragraph"
    CAPTION = "Caption"
    IMAGE = "Image"
    TABLE = "Table"
    TITLE = "Title"
    ROOT = "Root"


class ACTNode(NodeMixin):
    def __init__(
        self,
        id: str,
        name: str,
        nodeType,
        text=None,
        page=None,
        goal=None,
        parent=None,
        children=None,
        thread_id=None,
    ):
        if not isinstance(nodeType, NodeType):  # Ensure type is a NodeType
            raise TypeError("Node type must be a NodeType enum member")
        super(ACTNode, self).__init__()
        self.id = id
        self.name = name
        self.nodeType = nodeType
        self.text = text
        self.goal = goal
        self.parent = parent
        self.page = page
        if children:
            self.children = children
        thread_id = thread_id

    def print_tree(self, indent=0):
        output = ""
        for pre, fill, node in RenderTree(self):
            print("%s%s" % (pre, node.name))
            output += "%s%s\n" % (pre, node.name)
        return output

    def level_order_iter(self):
        return LevelOrderIter(self)

    def build_goal(self):
        if self.nodeType == NodeType.PARAGRAPH or self.nodeType == NodeType.CAPTION:
            self.goal = self.goal.text
        elif self.nodeType == NodeType.SECTION:
            union_goal = ""
            for child in PostOrderIter(self):
                union_goal += child.goal
            self.goal = union_goal

    def post_order_iter(self, **kwargs):
        return PostOrderIter(self, **kwargs)

    def __str__(self):
        return f"Node(name={self.name}, type={self.nodeType}, id={self.id}),\n goal={self.goal},\n text={self.text}, page={self.page}"


class ACTTree:  # New class to encapsulate structure logic
    def __init__(self, filepath: Path = None, text: str = None):
        if filepath:
            # Check if the file is a pdf file
            if filepath.suffix == ".pdf":
                self.root = self._build_act_tree_from_pdf(filepath)
                # Assign hierarchical IDs
                self.assign_hierarchical_ids()
                # self.generate_goal()
                self.number_of_paragraph()  # Number of paragraph nodes, thus number of jobs for generating paragraph's goal
            elif filepath.suffix == ".json":
                self.import_json(filepath)
                self.number_of_paragraph()  # Number of paragraph nodes, thus number of jobs for generating paragraph's goal
            elif filepath.suffix == ".txt":
                self.build_from_text(filepath)
                # Assgin hierarchical IDs
                self.assign_hierarchical_ids()
                self.number_of_paragraph()  # Number of paragraph nodes, thus number of jobs for generating paragraph's goal
            else:
                raise ValueError(
                    "Invalid file type. Only PDF and JSON files are supported."
                )
        elif text:
            self.build_from_text(text=text)
        
        self.queue_name = self.root.name
        #self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', heartbeat=60))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name)
        
        
    def number_of_paragraph(self):
        """Count the number of leaf nodes with nodeType == NodeType.PARAGRAPH."""
        def is_leaf(node: ACTNode) -> bool:
            return not node.children

        def count_leaves(node: ACTNode) -> int:
            if is_leaf(node) and node.nodeType == NodeType.PARAGRAPH:
                return 1
            x = sum(count_leaves(child) for child in node.children)
            return x

        self.pending_a_jobs = count_leaves(self.root)
        print(" ")
        

    def _build_act_tree_from_pdf(self, filepath: Path):
        doc = fitz.open(filepath)

        root = ACTNode(0, filepath.name, NodeType.ROOT)  # Create the root node

        # Keep track of the current section at each level
        section_stack = [root]

        for entry in doc.get_toc():
            level, title, page_number = entry

            # Determine appropriate parent
            while level <= len(section_stack) - 1:
                section_stack.pop()  # Pop until we find the right parent level
            parent = section_stack[-1]

            # Create and append the node
            node = ACTNode(
                level, title, NodeType.SECTION, None, parent=parent, page=page_number
            )
            section_stack.append(node)

        # Prepare headers from toc_data
        headers = [(entry[1], entry[2]) for entry in doc.get_toc()]

        sections = {}
        for header in headers:
            sections[header[0]] = extract_content_for_header(doc, headers, header[0])

        # Content Association
        for node in root.level_order_iter():
            if node.nodeType in (NodeType.SECTION, NodeType.PARAGRAPH):
                node.text = sections.get(node.name, "")

        # Content Association with Paragraphs
        for node in root.level_order_iter():
            if node.nodeType == NodeType.SECTION:
                if not node.children:
                    paragraphs = split_into_paragraphs(node.text)

                    for paragraph_text in paragraphs:
                        if is_title(paragraph_text):
                            ACTNode(
                                0,
                                paragraph_text,
                                NodeType.TITLE,
                                paragraph_text,
                                parent=node,
                            )
                        else:
                            ACTNode(
                                0,
                                paragraph_text[:5],
                                NodeType.PARAGRAPH,
                                paragraph_text,
                                parent=node,
                            )

        return root

    def visualize_tree(self, file_path="act_tree.png"):
        from anytree.exporter import UniqueDotExporter  # Import here for clarity

        UniqueDotExporter(self.root).to_picture(file_path)

    def export_json(self, file_path):

        # # JSON Export is now independent of the Node class
        # exporter = JsonExporter(
        #     indent=4, sort_keys=True, default=NodeTypeEncoder().default
        # )
        # file_path.parent.mkdir(exist_ok=True, parents=True)
        # with open(file_path, "w") as outfile:
        #     exporter.write(self.root, outfile)

        # try:
        #     exporter = JsonExporter(
        #         indent=4, sort_keys=True, default=NodeTypeEncoder().default
        #     )
        #     file_path.parent.mkdir(exist_ok=True, parents=True)
        #     with open(file_path, "w", encoding="utf-8") as outfile:
        #         exporter.write(self.root, outfile)
        #     print(f"File successfully created at: {file_path}")
        # except Exception as e:
        #     print(f"Failed to create file: {e}")

        exporter = JsonExporter(
                indent=4, sort_keys=True, default=NodeTypeEncoder().default
            )
        json_data = exporter.export(self.root)

        import tempfile
        import shutil

        try:
            # Ensure the directory exists
            file_path.parent.mkdir(exist_ok=True, parents=True)

            # Write the JSON string to a temporary file
            with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tmpfile:
                tmpfile.write(json_data)
                temp_name = tmpfile.name
            
            # Move the temporary file to the final destination
            shutil.move(temp_name, file_path)
            print(f"File successfully created at: {file_path}")
        except Exception as e:
            print(f"Failed to create file: {e}")


    def json_serial(self):
        exporter = JsonExporter(
            indent=4, sort_keys=True, default=NodeTypeEncoder().default
        )
        return exporter.export(self.root)

    def import_json(self, file_path):
        from anytree.importer import JsonImporter

        importer = JsonImporter()

        with open(file_path, "r") as infile:
            tree_data = importer.read(infile)

        def create_node(node_data):
            return ACTNode(
                name=node_data.name,
                nodeType=NodeType[
                    node_data.nodeType.upper()
                ],  # Convert string to NodeType
                id=node_data.id,
                page=node_data.page,
                text=node_data.text,
                goal=node_data.goal,
            )

        self.root = create_node(tree_data)  # Create the root node

        # Recursively create children
        def build_tree(parent_node, data):
            for child_data in data.children:
                child_node = create_node(child_data)
                child_node.parent = parent_node
                build_tree(child_node, child_data)  # Recursion

        build_tree(self.root, tree_data)

    def assign_hierarchical_ids(self):
        node_id = 0

        for pre, _, node in RenderTree(self.root, style=AsciiStyle()):
            if node.parent and node.parent.parent is None:
                node_id += 1
            node.id = node_id

            if node.parent is not None:
                subsection_id = 1
                for sibling in node.parent.children:
                    if sibling == node and node.parent.parent is not None:
                        node.id = f"{node.parent.id}.{subsection_id}"
                        break
                    subsection_id += 1

    def print_tree(self):
        self.root.print_tree()

    def generate_goal(self):
        act_assistant = ACTAssistant()
        count = 0
        for node in self.root.post_order_iter():
            if count == 10:
                break
            if node.nodeType == NodeType.PARAGRAPH:
                act_assistant.add_message_to_thread("Paragraph:\n" + node.text)
                node.goal = act_assistant.run_assistant_single_time()
            elif node.nodeType == NodeType.TITLE:
                node.goal = node.text
            elif node.nodeType == NodeType.SECTION:
                union_goal = ""
                for child in node.children:
                    if child.goal:
                        union_goal += child.goal
                node.goal = union_goal
            count += 1

    def build_from_text(self, filepath: Path = None, text: str = None):
        file_text = filepath.read_text()
        sections = get_sections_from_text(file_text)
        if not validate_section_order(sections):
            raise ValueError("Sections are not in valid hierarchical order.")
        self.root = ACTNode(0, filepath.name, NodeType.ROOT)
        current_nodes = [self.root]  # Keep track of nodes at each level

        for i in range(len(sections)):
            section_number, section_header, header_start, header_len = sections[i]
            next_section_start, next_section_len = (
                sections[i + 1][2:] if i < len(sections) - 1 else (None, None)
            )
            levels = [int(x) for x in section_number.split(".")]
            new_level = len(levels)

            # Find the appropriate parent
            while new_level <= len(current_nodes) - 1:
                current_nodes.pop()  # Pop until we find the right level
            parent = current_nodes[-1]

            # Create and add the node
            node = ACTNode(
                new_level,
                section_header,
                NodeType.SECTION,
                parent=parent,
                text=get_section_text(
                    file_text, header_start, header_len, next_section_start
                ),
            )
            current_nodes.append(node)

        return self.root
    
    def generate_goal_using_job(self):
        z=0
        for node in self.root.post_order_iter():
            if node.nodeType == NodeType.PARAGRAPH:
                job_id = f"{self.root.name}_{node.id}"
                z = z+1
                self.publish_job(job_id, 'Par_Goal', node.text)
        print(" ")        
        self.consume_queue()
        #self.export_json(export_path)

    def publish_job(self, job_id, job_type, payload):
        job = {
            'job_id': job_id,
            'job_type': job_type,
            'payload': payload
        }
        self.channel.basic_publish(exchange='',
                                   routing_key=self.queue_name,
                                   body=json.dumps(job))
    
    def consume_queue(self):
        def callback(ch, method, properties, body):
            job = json.loads(body)
            job_id = job['job_id']
            job_type = job['job_type']
            payload = job['payload']

            if job_type == 'Par_Goal':
                self.process_paragraph_job(job_id, payload)
                self.pending_a_jobs -= 1
                if self.pending_a_jobs == 0:
                    # Once all paragraph_goal jobs are done, publish the final internal_goal job
                    final_job_id = self.root.name
                    self.publish_job(final_job_id, 'Internal_Goal', {})

            elif job_type == 'Internal_Goal':
                self.process_internal_job()
                # Stop consuming after processing the final B job
                self.channel.stop_consuming()
                # Delete the queue after processing is complete
                self.channel.queue_delete(queue=self.queue_name)

            ch.basic_ack(delivery_tag=method.delivery_tag)

        self.channel.basic_consume(queue=self.queue_name, on_message_callback=callback)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()
        print(' [*] Processing finished.')

    def process_internal_job(self):
        # Set goals for title and section nodes
        for node in self.root.post_order_iter():
            if node.nodeType == NodeType.TITLE:
                node.goal = node.text
            elif node.nodeType == NodeType.SECTION:
                union_goal = ""
                for child in node.children:
                    if child.goal:
                        union_goal += f"\n{child.goal}"
                node.goal = union_goal

    def process_paragraph_job(self, job_id, node_text):
        #act_assistant = ACTAssistant()
        #act_assistant.add_message_to_thread("Paragraph:\n" + node.text)
        #node.goal = act_assistant.run_assistant_single_time(instructions="")
        prefix = f"{self.root.name}"
    
        # Check if the job_id starts with the root_name followed by an underscore
        if job_id.startswith(prefix):
            # Remove the prefix to get the node ID
            node_id = job_id[len(prefix):]
            node_id = node_id[1:]
        else:
            raise ValueError("The root name does not match the job ID prefix.")
        
        node = self.find_node_by_id(node_id)


        import time
        time.sleep(0.1)
        node.goal = node_text[0:3]
        print(" ")
    
    def find_node_by_id(self, node_id: str) -> ACTNode:
        return self._find_node_recursive(self.root, node_id)

    def _find_node_recursive(self, node: ACTNode, node_id: str) -> ACTNode:
        if node.id == node_id:
            return node
        
        if node.children:
            for child in node.children:
                found_node = self._find_node_recursive(child, node_id)
                if found_node:
                    return found_node
        
        return None