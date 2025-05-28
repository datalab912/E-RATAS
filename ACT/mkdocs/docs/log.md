# Log Module

This module provides a simplified interface for logging messages in the Python application. It utilizes the standard Python `logging` module under the hood.

## Class: `Log`

The `Log` class is responsible for creating and configuring a logger object.  It offers convenient methods for logging at different levels of severity.

### Constructor (`__init__(self, project_name: str, log_file: str = "app.log")`)

Creates a `Log` instance.

*   **`project_name` (str):** The name of your project or module. Used to categorize log entries.
*   **`log_file` (str, optional):** The name of the log file. Defaults to "app.log" and is created in the "logs" directory.

### Methods

*   **`debug(self, message: str)`:**  Logs a debug-level message.
*   **`info(self, message: str)`:** Logs an info-level message.
*   **`warning(self, message: str)`:**  Logs a warning-level message.
*   **`error(self, message: str)`:** Logs an error-level message.
*   **`critical(self, message: str)`:**  Logs a critical-level message.

## Log Levels

The logging levels correspond to the severity of the message:

*   **DEBUG:** Detailed information, typically for debugging purposes.
*   **INFO:**  General informational messages.
*   **WARNING:**  Potential issues or situations that require attention.
*   **ERROR:**  Errors that affect the functionality of the application.
*   **CRITICAL:**  Severe errors that may cause the application to crash.

## Example Usage

```python
from log import Log

logger = Log("my_module")  # Create a logger for a module
logger.info("Starting data processing...")
logger.warning("Potential issue detected, investigating...")

try:
    # Your code that might raise an exception
except Exception as e:
    logger.error(f"An error occurred: {e}")
```
