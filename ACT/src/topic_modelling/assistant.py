import os
from dotenv import load_dotenv

from GPT_assistant.base_assistant import BaseAssistant
from log.log import Log
from utilities.utils import save_to_env_file

load_dotenv()  # Load environment variables

TM_MODEL = "gpt-4-0125-preview"
TM_MODEL_NAME = "TM_ASSISTANT"
TM_MODEL_ID = f"{TM_MODEL_NAME}_ID"
TM_THREAD_ID = f"{TM_MODEL_NAME}_THREAD_ID"
# === Create Assistant ===


class TM_Assistant(BaseAssistant):
    ASSISTANT_INSTRUCTIONS = """Extract bullet points from the following text, ensuring all points are at the same level
    and retain the original content without summarization or paraphrasing."""
    CREATE_THREAD_MESSAGE = "Hello, I have a paragraph that I would like to summarize."
    SINGLE_TASK = """Task: List the following points as individual bullet points at the same level,
    and retain the original content without summarization or paraphrasing.
    Special Case: If there is only one point to extract,
    output "No Need" instead of a bullet point.

    **Desired Output Format:**

    * Bullet point 1
    * Bullet point 2
    * ..."""
    EXAMPLE_MESSAGE = "Please follow this example:\n\n"

    def __init__(self, assistant_id=None, thread_id=None):

        logger = Log("TM_Assistant", "tm_assistant.log")
        super().__init__(TM_MODEL_NAME, assistant_id, thread_id, logger)

        ASSISTANT_ID = os.getenv(TM_MODEL_ID)
        THREAD_ID = os.getenv(TM_THREAD_ID)

        if not ASSISTANT_ID and not assistant_id:
            ASSISTANT_ID = self.create_assistant(
                TM_MODEL_NAME, self.ASSISTANT_INSTRUCTIONS, TM_MODEL
            )
            save_to_env_file(TM_MODEL_ID, ASSISTANT_ID)

        if not THREAD_ID and not thread_id:
            THREAD_ID = self.create_thread()
            save_to_env_file(TM_THREAD_ID, THREAD_ID)

        self.assistant_id = ASSISTANT_ID or assistant_id
        self.thread_id = THREAD_ID or thread_id

    def run_assistant_single_text(self, instructions=None):
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id,
            instructions=instructions or self.SINGLE_TASK,
        )
        self.logger.info(f"Assistant run created with ID: {run.id}")
        return self.wait_for_run_completion(run.id)

    def add_example_by_batching(self, examples: list):
        for example in examples:
            self.add_example_to_thread(example["input"], example["output"])


# assistant = TM_Assistant()

# SAMPLE_PARAGRAPH =  """
# The Document should have a Work Sample Section(essential)
# Work sample Section should cover 2 example of the student's work (such as news stories, articles, interviews, projects etc.)
# work Example 1 And work Example 2 sould cover these content:
# short description of your role in that work sample
# how you used the sample.
# """


# example_input = """
# The Document should have title page (essential).
# (No title page, then -10%)
# The title page of the report must include:
# a. Name of the organization
# b. Name of the internee, Student ID and session
# c. Submission date of the internship report
# d. Name of the University
# """

# example_output = """
# *Existing Title Page Section
# *Existing Name of the organization
# *Existing Name of the internee, Student ID and session
# *Existing Submission date of the internship report
# *Existing  Name of the University
# """
# assistant.add_example_to_thread(example_input, example_output)

# # assistant.add_message_to_thread("Paragraph:\n" + SAMPLE_PARAGRAPH)
# assistant.run_assistant_single_text()
