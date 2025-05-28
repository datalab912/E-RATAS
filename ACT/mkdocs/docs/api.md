**API Module Documentation**

## API Module (`app.py`)

The API module provides a Flask-based web interface for interacting with the ACT functionality. It serves as a bridge between the user (or another software system) and the core ACT processing logic.

### Endpoints

- **`/build-act` (GET, POST):**
  - **GET:** Renders an HTML form for uploading a file.
  - **POST:**
    1. Receives a PDF or text file as input.
    2. Builds an ACT tree from the file's content.
    3. Saves the ACT tree as a JSON file in a designated directory.
    4. Enqueues a sample job for further processing (this is currently commented out in the code).
    5. Returns the JSON representation of the ACT tree to the user.
- **`/job` (GET, POST):**
  - **GET:** Renders an HTML form for inputting a string.
  - **POST:**
    1. Receives an input string.
    2. Enqueues a sample job for processing the string.
    3. Returns a confirmation message that the job has been enqueued.
- **`/text-validity-check` (GET, POST):**
  - **GET:** Renders an HTML form for uploading a file.
  - **POST:**
    1. Receives a PDF or text file as input.
    2. Extracts sections from the file's content.
    3. Validates the hierarchical order of the sections.
    4. Returns a message indicating whether the text is valid or not.

### Interactions (act_api.py <-> software.py)

* The `act_api.py` module provides a user interface for uploading a file and initiating the ACT building process.
* When the user uploads a PDF file through the `/build-act` endpoint, the `act_api.py` module saves the file to the `uploads/act` folder.
* It then makes a POST request to the `software.py` module's `/software/act` endpoint, sending the uploaded file along.
* The `software.py` module receives the file, processes it, builds the ACT tree, and returns the JSON representation of the tree back to `act_api.py`.
* Finally, `act_api.py` returns this JSON response to the user.

### Dependencies

* Flask: A micro web framework for building web applications in Python.
* werkzeug: A WSGI utility library used for handling file uploads securely.
* pathlib: A module for working with file paths.
* ACT.src.act: The module containing the core ACT building and manipulation logic.
* ACT.src.text_validity_check: The module responsible for validating the structure of the input text.
* job.sample_job: The module containing sample job functions.

**Note:** Remember to replace the placeholder file paths and URLs in the `software.py` script with your actual file paths and URLs.



## Software Module Documentation (`software.py`)

The `software.py` module provides the backend functionality for processing PDF files, building ACT trees, and handling webhook requests related to ACT data.

### Endpoints

* **`/software/act` (POST):**
    1. Receives a PDF or text file from `act_api.py`.
    2. Processes the file.
    3. Builds an ACT tree.
    4. Returns the JSON representation of the ACT tree back to `act_api.py`.
* **`/software/act_webhook` (POST):**
    1. Receives a JSON representation of an ACT tree.
    2. Processes the tree.
    3. Returns a JSON message indicating success or error in processing.