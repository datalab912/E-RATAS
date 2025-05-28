from ACT.src.text_validity_check import (
    get_sections_from_text,
    get_sections_from_file,
    validate_section_order,
)
from ACT.tests.mock import SAMPLE_TEXT_FILE_PATH


def test_get_sections_from_text():
    text = "1. Introduction\n\n1.1. Background and Problem Statement\n\n1.2. Research Questions"
    expected_sections = [
        ("1", "Introduction", 0, 15),
        ("1.1", "Background and Problem Statement", 17, 37),
        ("1.2", "Research Questions", 56, 23),
    ]
    assert get_sections_from_text(text) == expected_sections


def test_get_sections_from_file():
    expected_sections = [
        ("1", "Introduction", 0, 15),
        ("1.1", "Background and Problem Statement:", 17, 37),
        ("1.1.1", "Sample Heading", 414, 20),
        ("1.2", "Research Questions:", 436, 23),
        ("1.3", "Project Goals and Scope:", 655, 28),
        ("2", "Literature Review", 925, 20),
        ("2.1", "Data Quality and Anomaly Detection:", 947, 40),
        ("2.2", "Applications of NLP in Data Quality:", 1066, 40),
        ("3", "Methodology", 1195, 14),
        ("3.1", "Data Collection and Preprocessing:", 1211, 38),
        ("3.3", "False Heading", 1328, 17),
        ("3.2", "Feature Engineering:", 1348, 24),
        ("3.3", "Model Selection and Evaluation:", 1475, 35),
        ("4", "Results and Discussion", 1628, 25),
        ("4.1", "Experimental Setup:", 1655, 23),
        ("4.2", "Model Performance:", 1732, 22),
        ("4.3", "Limitations and Future Work:", 1854, 32),
    ]
    assert get_sections_from_file(SAMPLE_TEXT_FILE_PATH) == expected_sections


def test_validate_section_order():
    sections = [
        ("1", "Introduction", 0, 15),
        ("1.1", "Background and Problem Statement:", 17, 37),
        ("1.1.1", "Sample Heading", 414, 20),
        ("1.2", "Research Questions:", 436, 23),
        ("1.3", "Project Goals and Scope:", 655, 28),
        ("2", "Literature Review", 925, 20),
        ("2.1", "Data Quality and Anomaly Detection:", 947, 40),
        ("2.2", "Applications of NLP in Data Quality:", 1066, 40),
        ("3", "Methodology", 1195, 14),
        ("3.1", "Data Collection and Preprocessing:", 1211, 38),
        ("3.2", "Feature Engineering:", 1328, 24),
        ("3.3", "Model Selection and Evaluation:", 1455, 35),
        ("4", "Results and Discussion", 1608, 25),
        ("4.1", "Experimental Setup:", 1635, 23),
        ("4.2", "Model Performance:", 1712, 22),
        ("4.3", "Limitations and Future Work:", 1834, 32),
    ]
    assert validate_section_order(sections) == True


def test_invalid_section_order():
    sections = [
        ("1", "Introduction", 0, 15),
        ("1.1", "Background and Problem Statement:  ", 17, 39),
        ("1.1.1", "Sample Heading", 416, 20),
        ("1.2", "Research Questions: ", 438, 24),
        ("1.3", "Project Goals and Scope:  ", 658, 30),
        ("2", "Literature Review", 930, 20),
        ("2.1", "Data Quality and Anomaly Detection: ", 952, 41),
        ("2.2", "Applications of NLP in Data Quality: ", 1072, 41),
        ("3", "Methodology", 1202, 14),
        ("3.1", "Data Collection and Preprocessing: ", 1218, 39),
        ("3.3", "False Heading", 1336, 17),
        ("3.2", "Feature Engineering: ", 1356, 25),
        ("3.3", "Model Selection and Evaluation: ", 1484, 36),
        ("4", "Results and Discussion", 1638, 25),
        ("4.1", "Experimental Setup: ", 1665, 24),
        ("4.2", "Model Performance: ", 1743, 23),
        ("4.3", "Limitations and Future Work: ", 1866, 33),
    ]
    assert validate_section_order(sections) == False
