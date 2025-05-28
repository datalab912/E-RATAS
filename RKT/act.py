from enum import Enum
from pathlib import Path
import fitz  # PyMuPDF
from anytree import NodeMixin, RenderTree
from anytree.iterators.levelorderiter import LevelOrderIter
from anytree.iterators.postorderiter import PostOrderIter
from anytree.render import AsciiStyle
from json import JSONEncoder

from redis import Redis
from rq import Queue, get_current_job
from rq.job import Job
from log.log import Log

from .pdf_utls import extract_content_for_header, split_into_paragraphs, is_title
from .assistant import ACTAssistant

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
    def __init__(self, filepath: Path):
        # Check if the file is a pdf file
        if filepath.suffix == ".pdf":
            self.root = self._build_act_tree(filepath)
            # Assign hierarchical IDs
            self.assign_hierarchical_ids()
            # self.generate_goal()
        elif filepath.suffix == ".json":
            self.import_json(filepath)
        else:
            raise ValueError(
                "Invalid file type. Only PDF and JSON files are supported."
            )

    def _build_act_tree(self, filepath: str):
        doc = fitz.open(filepath)

        root = ACTNode(0, filepath.name, NodeType.ROOT)  # Create the root node

        # Keep track of the current section at each level
        section_stack = [root]

        section_id = 1  # Start with section ID 1
        subsection_counters = {}  # A dictionary to track subsection IDs at each level

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
                node.id = section_id
                section_id += 1

                subsection_id = (
                    subsection_counters.get(node.id, 0) + 1
                )  # Get or initialize
                # Update the counter
                subsection_counters[node.id] = subsection_id

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
        from anytree.exporter import JsonExporter

        # JSON Export is now independent of the Node class
        exporter = JsonExporter(
            indent=4, sort_keys=True, default=NodeTypeEncoder().default
        )
        file_path.parent.mkdir(exist_ok=True, parents=True)
        with open(file_path, "w") as outfile:
            exporter.write(self.root, outfile)

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

    def generate_goal_using_job(self, export_path: Path):
        """
        Generates a goal using a job for processing paragraphs.

        Args:
            export_path (Path): The path to export the generated goal.

        Returns:
            None
        """
        redis_conn = Redis()
        queue = Queue(name=self.root.name, connection=redis_conn)
        jobs = []
        for node in self.root.post_order_iter():
            if node.nodeType == NodeType.PARAGRAPH:
                job = Queue.prepare_data(
                    process_paragraph_job,
                    (node.text,),
                    job_id=f"{self.root.name}_{node.id}",
                    description=f"Processing paragraph {self.root.name}_{node.id}",
                    result_ttl=3600,  # Result will be kept for 1 hour
                )
                jobs.append(job)

        q = queue.enqueue_many(jobs)
        logger.info(
            f"Enqueued {len(jobs)} jobs for processing paragraphs for {self.root.name}"
        )
        queue.enqueue(generate_goal_job, export_path, depends_on=q)
        logger.info(f"Enqueued job for generating goal for {self.root.name}")


def generate_goal_job(export_path: Path):
    current_job = get_current_job()
    act_tree = ACTTree(export_path)
    logger.info(f"Generating goal for tree: {act_tree.root.name}")
    for id, node in zip(
        current_job._dependency_ids,
        [
            node
            for node in act_tree.root.post_order_iter()
            if node.nodeType == NodeType.PARAGRAPH
        ],
    ):
        try:
            result = Job.fetch(id, connection=current_job.connection).result
            node.goal = result
            logger.info(f"Result of dependent job with id {id}: {result}")
        except Exception as e:
            logger.error(f"Error fetching result of job with id {id}: {e}")
    for node in act_tree.root.post_order_iter():
        if node.nodeType == NodeType.TITLE:
            node.goal = node.text
        elif node.nodeType == NodeType.SECTION:
            union_goal = ""
            for child in node.children:
                if child.goal:
                    union_goal += f"\n{child.goal}"
            node.goal = union_goal
    act_tree.export_json(export_path)


def process_paragraph_job(node_text):
    act_assistant = ACTAssistant()
    act_assistant.add_message_to_thread("Paragraph:\n" + node_text)
    text_result = act_assistant.run_assistant_single_time(instructions="")
    return text_result
