from cgi import test
import os
from unittest.mock import patch
from log.log import Log
from pathlib import Path


def test_logging_messages(caplog):
    log = Log("test_project")

    log.info("Test info message")
    log.warning("Test warning message")

    assert "Test info message" in caplog.text
    assert "Test warning message" in caplog.text


def test_log_file_creation():
    test_file = "test_log.log"
    test_path = (
        Path(__file__).parent.parent.parent.parent / "logs" / test_file
    )  # Path to the log file

    log = Log("test_project", test_file)  # Using temporary file
    print(test_path)
    log.info("Test info message")

    assert os.path.exists(test_path)  # Check if log file exists


@patch("logging.Logger.warning")
def test_logging_level(mock_warning):
    log = Log("test_project")
    log.warning("Test warning message")

    mock_warning.assert_called_once_with("Test warning message")
