import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
import json

from ACT.src.act import NodeType, ACTTree, ACTAssistant
from ACT.tests.mock import SAMPLE_FILEPATH, JSON_FILE_PATH


# Recommended - A fixture for a basic tree structure


@pytest.fixture
def basic_act_tree():
    act_tree = ACTTree(SAMPLE_FILEPATH)
    # Add more complex mocking for act_tree._build_act_tree here if needed
    return act_tree


def test_build_act_tree(basic_act_tree):  # Example using a fixture
    root = basic_act_tree.root
    assert root.name == SAMPLE_FILEPATH.name
    assert root.nodeType == NodeType.ROOT
    assert len(root.children) > 0  # Assuming a non-empty document


def test_build_act_tree_subsections(basic_act_tree):

    root = basic_act_tree.root

    # Assertions for nested structure
    assert len(root.children) == 13  # 13 top-level sections
    section_1 = root.children[0]
    assert section_1.name == "ACKNOWLEDGEMENT"
    assert len(section_1.children) == 2  # 2 subsections
    # ... more assertions on the tree structure


def test_generate_goal(basic_act_tree):

    # Create mock ACTAssistant class and configure methods
    mock_assistant = MagicMock(spec=ACTAssistant)
    mocked_paragraph_goal = "Mocked paragraph goal"
    mock_assistant.run_assistant_single_time.return_value = mocked_paragraph_goal

    with patch("ACT.src.act.ACTAssistant", return_value=mock_assistant):
        act_tree = basic_act_tree
        act_tree.generate_goal()

        # Assertions
        paragraph_nodes = [
            n
            for n in act_tree.root.post_order_iter()
            if n.nodeType == NodeType.PARAGRAPH
        ][:4]

        # Limit to the first 10 paragraph nodes, based on your code's 'count' logic
        for node in paragraph_nodes:
            assert node.goal == mocked_paragraph_goal


def test_assign_hierarchical_ids(basic_act_tree):
    act_tree = basic_act_tree

    # Call the assign_hierarchical_ids method
    act_tree.assign_hierarchical_ids()

    # Assert that the hierarchical IDs are correctly assigned
    assert act_tree.root.id == 0
    assert act_tree.root.children[0].id == 1
    assert act_tree.root.children[0].children[0].id == "1.1"
    assert act_tree.root.children[1].id == 2


def test_export_json(basic_act_tree):
    act_tree = basic_act_tree

    # Export the tree to JSON
    act_tree.export_json(JSON_FILE_PATH)

    # Check if the file was created
    assert Path(JSON_FILE_PATH).exists()

    # Optionally, load the JSON file and validate its contents
    json_data = json.load(open(JSON_FILE_PATH))
    assert json_data["name"] == SAMPLE_FILEPATH.name
    assert json_data["children"][0]["name"] == "ACKNOWLEDGEMENT"
