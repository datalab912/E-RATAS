## Job Module

This module provides functionality for managing background jobs within your application. It relies on the following libraries:

* **Redis:** An in-memory data store used as a message broker for the job queue.
* **RQ (Redis Queue):** A simple Python library for queueing jobs and processing them in the background.

## Functions

### `sample_job_that_run_for_10_seconds(input_str: str)`

This is a sample job function that demonstrates how to create a job that runs in the background.

* **Functionality:**
    * Simulates a 10-second task.
    * Logs the start and completion of the job using the `Log` class.
    * Makes a POST request to an external webhook (replace with your actual webhook URL) after completion.

* **Parameters:**
    * `input_str` (str): The input string for the job (not used in this sample, but you can pass data to your custom job functions).

* **Returns:**
    * A string indicating the job has completed.

### `enqueue_sample_job(input_str: str)`

This function enqueues the `sample_job_that_run_for_10_seconds` job into the default RQ queue.

* **Functionality:**
    * Connects to the Redis server.
    * Enqueues the job with the given input string.
    * Logs that the job has been enqueued.

* **Parameters:**
    * `input_str` (str): The input string for the job.

* **Returns:**
    * A string confirming that the job has been enqueued.

## How to Use

**1. Start Redis and the RQ Worker:**

Open a terminal and run the following commands:

```bash
redis-server
rq worker --with-scheduler
```
- **`redis-server`:** Starts the Redis server, which will act as the backend for the job queue.
- **`rq worker --with-scheduler`:** This command launches an RQ worker process that will process jobs from the queue.

**2. Start the RQ Dashboard (Optional):**

In a separate terminal, you can run:
```bash
rq-dashboard
```
- This command launches a web interface for monitoring the status of your queues and jobs.

**3. Enqueue Jobs:**

In your main Python code, import the `enqueue_sample_job` function and use it to enqueue jobs as needed:

```python
from job import enqueue_sample_job

# Example:
input_text = "your_input_string"
enqueue_sample_job(input_text)
```

**4. Run the webserver:**

You can run the webserver by typing this command:

```bash
flask --app act_api run --debug
```



**Key Points**

* **Flexibility:** You can replace `sample_job_that_run_for_10_seconds` with your own job functions to execute any background tasks.
* **Customization:** The provided example is basic. Tailor it to your specific project needs.
* **Scaling:** RQ and Redis allow you to easily scale your job processing if you have a large volume of tasks.