import os
from pathlib import Path
from unittest import result
import fitz
from regex import P  # PyMuPDF

from act import ACTTree

sample_filepath = (
    Path(__file__).parent.parent.parent.parent
    / "data/raw/sample_reports/anas1-2023/46154825_Tuan Khoi Tran_assignsubmission_file/46154825_TuanKhoiTran_FinalReport.pdf"
)

sample_filepath = Path(
    "C:\\Users\\MSD\\Desktop\\my_project\\ACT\\src\\ACT\\tests\\data\\45698120.pdf"
)


sample_act = ACTTree(sample_filepath)
sample_act.print_tree()
# sample_act.visualize_tree()

# for node in sample_act.root.root.children[2].children[2].children:
#     print(node.name, node.id, node.text)

#sample_act.export_json(Path("sample_act3.json"))
sample_act.generate_goal_using_job()
sample_act.export_json(Path("C:\\Users\\MSD\\Desktop\\my_project\\ACT\\ouput\\sample_act4.json"))

# print(sample_act.root.children[0].text)

# sample_node3 = ACTNode(0, "This is a sample section", NodeType.SECTION, "This is a sample section")
# sample_node1 = ACTNode(0, "This is a sample paragraph", NodeType.PARAGRAPH, "This is a sample paragraph", parent=sample_node3)
# sample_node2 = ACTNode(0, "This is a sample title", NodeType.TITLE, "This is a sample title", parent=sample_node3)

# sample_node3.print_tree()


def check_pdfs_for_toc(directory_path):
    """
    Recursively checks all PDF files in a directory and subdirectories for a table of contents.

    Args:
        directory_path (str): The path to the directory to start searching.

    Returns:
        list: A list of tuples, each containing the full file path and a boolean indicating whether a TOC was found.
    """
    results = []
    for root, dirs, files in os.walk(directory_path):
        for filename in files:
            if filename.endswith(".pdf"):
                file_path = os.path.join(root, filename)
                try:
                    with fitz.open(file_path) as doc:
                        toc = doc.get_toc()
                        has_toc = bool(toc)  # True if toc is not empty
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
                    has_toc = False  # Assume no TOC if there's an error
                results.append((file_path, has_toc))  # Store full path
    return results


# pdf_directory = "/Users/dannguyen/Yirigaa/major_project/data/raw"  # Replace with your directory path
# toc_results = check_pdfs_for_toc(pdf_directory)

# for filename, has_toc in toc_results:
#     if has_toc:
#         print(f"File: {filename} has a table of contents")
