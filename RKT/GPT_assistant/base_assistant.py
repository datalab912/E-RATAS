from openai import OpenAI
import time
from dotenv import load_dotenv
import openai
from log_engine.log import Log

logger = Log("BaseAssistant", "base_assistant.log")

load_dotenv()  # Load environment variables

#DEFAULT_MODEL = "gpt-3.5-turbo-0125"
DEFAULT_MODEL = "gpt-4-turbo-2024-04-09"
#DEFAULT_MODEL = "gpt-4-0125-preview"

class BaseAssistant:
    def __init__(
        self,
        assistant_name: str,
        assistant_id: str,
        thread_id: str = None,
        logger=logger,
    ):
        """
        Initializes a new instance of the BaseAssistant class.

        Args:
            assistant_name (str): The name of the assistant.
            assistant_id (str): The ID of the assistant.
            thread_id (str, optional): The ID of the thread. Defaults to None.
            logger (Logger, optional): The logger instance to use for logging. Defaults to logger.

        """
        self.assistant_name = assistant_name
        self.assistant_id = assistant_id
        self.thread_id = thread_id
        self.client = OpenAI(api_key="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")
        self.logger = logger

    def create_assistant(
        self, assistant_name: str, instructions: str, model: str = DEFAULT_MODEL
    ):
        """
        Create an assistant instance.

        Args:
            assistant_name (str): The name of the assistant.
            instructions (str): The instructions for the assistant.
            model (str, optional): The model to use. Defaults to DEFAULT_MODEL.

        Returns:
            str: The ID of the assistant.

        """
        assistant = self.client.beta.assistants.create(
            name=assistant_name, instructions=instructions, model=model
        )
        self.assistant_id = assistant.id
        self.logger.info(f"Assistant created with ID: {self.assistant_id}")

        return self.assistant_id

    def create_thread(self, user_message=None):
        """
        Creates a new thread.

        Args:
            user_message (str, optional): The user message to start the thread with. Defaults to None.

        Returns:
            str: The ID of the created thread.

        """
        if user_message:
            thread = self.client.beta.threads.create(
                messages=[{"role": "user", "content": user_message}]
            )
        else:
            thread = self.client.beta.threads.create()

        self.logger.info(f"Thread created with ID: {thread.id}")

        self.thread_id = thread.id
        return self.thread_id

    def add_message_to_thread(self, message):
        """
        Adds a message to the thread.

        Args:
            message (str): The message to add.

        """
        message = self.client.beta.threads.messages.create(
            thread_id=self.thread_id, role="user", content=message
        )
        self.logger.info(
            f"Added message: {message.content}, to thread_id: {self.thread_id}"
        )

    def run_assistant(self):
        pass

    def add_example_to_thread(self, example_input: str, example_output: str):
        self.add_message_to_thread(
            f"Example: **Input:**\n\n{example_input}\n\n**Output:**\n\n{example_output}"
        )

    def wait_for_run_completion(
        self,
        run_id,
        sleep_interval=1,
    ):
        """
        Waits for the completion of a run.

        Args:
            run_id (str): The ID of the run.
            sleep_interval (int, optional): The interval between retries in seconds. Defaults to 5.
            max_retries (int, optional): The maximum number of retries. Defaults to 3.
            timeout (int, optional): The timeout for retrieving the run. Defaults to 10.

        Returns:
            str: The response from the assistant.

        """
        run = self.client.beta.threads.runs.retrieve(
            thread_id=self.thread_id, run_id=run_id
        )
        while run.status in ["in_progress", "queued"]:
            time.sleep(sleep_interval)
            run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread_id, run_id=run.id
            )

        if run.status == "completed":
            elapsed_time = run.completed_at - run.created_at
            formatted_elapsed_time = time.strftime(
                "%H:%M:%S", time.gmtime(elapsed_time)
            )
            self.logger.info(f"Run {run_id} completed in {formatted_elapsed_time}")
            messages = self.client.beta.threads.messages.list(thread_id=self.thread_id)
            last_message = messages.data[0]
            response = last_message.content[0].text.value
            self.logger.info(f"Assistant Response: {response}")
            return response
        else:
            self.logger.error(f"Run {run_id} failed with error: {run.last_error}")
            raise RuntimeError("Assistant run failed.")
