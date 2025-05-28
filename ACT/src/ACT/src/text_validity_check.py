from pathlib import Path
import re

header_pattern = r"^(\d+(?:\.\d+)*)[\.\s]*([^.\n\r]+)\.?"


def get_sections_from_text(text: str):
    """Extracts the sections from the text, along with their positions and lengths."""
    sections = []
    current_position = 0  # Track position within the whole text
    for _, line in enumerate(text.split("\n")):
        match = re.search(header_pattern, line)
        if match:
            number_part = match.group(1)
            text_part = match.group(2)
            position = current_position + match.start()  # Adjust for whole text
            length = match.end() - match.start()
            sections.append((number_part, text_part, position, length))

        current_position += len(line) + 1  # Update position (including newline)

    return sections


def get_sections_from_file(file_path: Path):
    """Extracts the sections from the text file."""
    with open(file_path, "r") as file:
        text = file.read()
        return get_sections_from_text(text)


def validate_section_order(sections):

    """
    Checks if a list of sections is in valid hierarchical order. Sections are
    represented as tuples of (section_number, section_title)

    Args:
        section_list: A list of tuples where each tuple represents a section header.

    Returns:
        True if the section list is valid, False otherwise.
    """

    current_level = 0  # Start at the top level
    previous_section_number = ""

    for section_number, _, _, _ in sections:
        number_parts = section_number.split(".")
        current_section_level = len(
            number_parts
        )  # Determine level based on '.' separators

        # Check if the level is deeper than allowed
        if current_section_level > current_level + 1:
            return False

        # If at a new level, reset comparison
        if current_section_level < current_level:
            previous_section_number = ""

        # If at the same level, compare numbers lexicographically
        if current_section_level == current_level:
            if section_number <= previous_section_number:
                return False

        current_level = current_section_level
        previous_section_number = section_number

    return True  # If no errors found, the list is valid


# # Example usage
# sample_text_file_path = (
#     Path(__file__).parent.parent / "tests" / "data" / "sample_act_input.txt"
# )


# sample_sections = get_sections_from_file(sample_text_file_path)
# print(
#     "samle sections:", sample_sections
# )  # Output samle sections: [('1', 'Introduction'), ('1.1', 'Background and Problem Statement:  '), ('1.1.1', 'Sample Heading'), ('1.2', 'Research Questions: '), ('1.3', 'Project Goals and Scope:  '), ('2', 'Literature Review'), ('2.1', 'Data Quality and Anomaly Detection: '), ('2.2', 'Applications of NLP in Data Quality: '), ('3', 'Methodology'), ('3.1', 'Data Collection and Preprocessing: '), ('3.3', 'False Heading'), ('3.2', 'Feature Engineering: '), ('3.3', 'Model Selection and Evaluation: '), ('4', 'Results and Discussion'), ('4.1', 'Experimental Setup: '), ('4.2', 'Model Performance: '), ('4.3', 'Limitations and Future Work: ')]

# if validate_section_order(sample_sections):
#     print("The section order is valid.")
# else:
#     print("Invalid section order.")  # Output: The section order is valid.
