import os
from dotenv import load_dotenv

from GPT_assistant.base_assistant import BaseAssistant
from log_engine.log import Log
from utilities.utils import save_to_env_file
#from utils import save_to_env_file

load_dotenv()  # Load environment variables

TM_MODEL = "gpt-4-0125-preview"
TM_MODEL_NAME = "CT_ASSISTANT"
TM_MODEL_ID = f"{TM_MODEL_NAME}_ID"
TM_THREAD_ID = f"{TM_MODEL_NAME}_THREAD_ID"
# === Create Assistant ===


class TM_Assistant(BaseAssistant):
    ASSISTANT_INSTRUCTIONS = """You are an expert that work on a rubric criterion and divided it to some simpler criteria"""
    CREATE_THREAD_MESSAGE = """Divide the provided rubric criterion into distinct sub-criteria. Each sub-criterion should cover a different topic or area within the original criterion. All sub-criteria must be grouped under the same level of detail, able to reconstruct the original criterion when combined (except for exact duplications). Begin each sub-criterion with three asterisks (***). If the criterion is indivisible due to its homogeneous content, return it unchanged."""
    SINGLE_TASK = """concider these 7 instruction during the the criterion devision: 
    1- Read the Criterion Thoroughly: Understand the overall theme and elements of the criterion.
    2- Identify Distinct Areas: Look for distinct topics or areas within the criterion that can be separated.
    3- Construct Sub-Criteria: Create sub-criteria that focus on these distinct areas, ensuring each is comprehensive and preserves the content of the original criterion.
    4- Distinct Sections: Each sub-criterion should focus on a unique area. Use "***" to start each sub-criterion.
    5- Format the Output: Start each sub-criterion with "***" to indicate a new section.
    7- Check Completeness: Ensure that all sub-criteria together cover the entire content of the original criterion without redundancy.
    8- Return Unchanged if Indivisible: If no distinct areas can be identified, return the original criterion unchanged."""
    EXAMPLE_MESSAGE = "Please follow this example:\n\n"

    def __init__(self, assistant_id=None, thread_id=None):

        logger = Log("CT_Assistant", "ct_assistant.log")
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
