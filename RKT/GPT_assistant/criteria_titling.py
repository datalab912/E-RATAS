from hmac import new
import os
from dotenv import load_dotenv

from GPT_assistant.base_assistant import BaseAssistant
from log_engine.log import Log
from utilities.utils import save_to_env_file
#from utils import save_to_env_file

load_dotenv()  # Load environment variables

#CT_MODEL = "gpt-4-0125-preview"
CT_MODEL = "gpt-4-turbo-2024-04-09"
#CT_MODEL = "gpt-3.5-turbo-0125"

CT_MODEL_NAME = "CT_ASSISTANT"
CT_MODEL_ID = f"{CT_MODEL_NAME}_ID"
CT_THREAD_ID = f"{CT_MODEL_NAME}_THREAD_ID"
# === Create Assistant ===


class CT_Assistant(BaseAssistant):
    ASSISTANT_INSTRUCTIONS = """You are an expert responsible for find main feature of a provided criterion.
    I have a scoring criterion from a rubric and a corresponding answer. I want to identify the relevant parts of the answer that need to be evaluated against this criterion. 
    Please specify the features of the content that is related to the criterion. just give me the combination of words (like a title with less than 20 words) that shows this feature"""
    CREATE_THREAD_MESSAGE = """Please follow the instructions and the following examples to generate the specific feature-based title."""
    #SINGLE_TASK = """Please follow the examples that I Give you at the starting message of this thread."""
    EXAMPLES = {
        """Plan how the learning from doing tasks or assignments or activities will be useful to students""":
        """Application of Taskor or assignments or activities Learning to Student Benefits""",

        """For subsection week 1 the information connection and Communication expreince with others and organizations  should cover these contents:
        - Evaluate the effectiveness and efficiency of connection and Communication expreince with others and organizations
        - Describe the student's conclusions about connection and Communication expreince with others and organizations 
        - Describe the student's feelings about connection and Communication expreince with others and organizations
        - Describe In what ways the learning experience related to connection and Communication expreince with others and organizations will serve the student in his/her future
        - Analyze the student's own performance as a learner relted to connection and Communication expreince with others and organizations
        - Plan how the information related to connection and Communication expreince with others and organizations will be useful to the students
        - Describe the student's recommendations about the connection and Communication expreince with others and organizations
        - Demonstrate transfer of learning relted to connection and Communication expreince with others and organizations""": 
        """Comprehensive Analysis of Communication and Connection Experiences""",

        """The title page of the report must include:
            a. Name of the organization
            b. Name of the internee, Student ID and session
            c. Submission date of the internship report
            d. Name of the University""": 
        """***Title page content""",
    }

    logger = Log("CT_Assistant", "ct_assistant.log")

    def __init__(self, assistant_id=None, thread_id=None):

        logger = Log("CT_Assistant", "ct_assistant.log")
        #super().__init__(TM_MODEL_NAME, assistant_id, thread_id, logger)
        super().__init__(CT_MODEL_NAME, assistant_id, thread_id, self.logger)

        ASSISTANT_ID = os.getenv(CT_MODEL_ID)
        THREAD_ID = os.getenv(CT_THREAD_ID)

        ASSISTANT_ID="asst_91wpIqpZ5xcNhxAXMMs9BVoc"
        THREAD_ID="thread_tVon84r4TXVF71y2Hl4ThBM4"

        # Flag to check if a new thread is created
        new_thread = False

        if not ASSISTANT_ID and not assistant_id:
            ASSISTANT_ID = self.create_assistant(
                CT_MODEL_NAME, self.ASSISTANT_INSTRUCTIONS, CT_MODEL
            )
            save_to_env_file(CT_MODEL_ID, ASSISTANT_ID)

        if not THREAD_ID and not thread_id:
            #THREAD_ID = self.create_thread()
            THREAD_ID = self.create_thread(user_message=self.CREATE_THREAD_MESSAGE)
            save_to_env_file(CT_THREAD_ID, THREAD_ID)
            new_thread = True

        self.assistant_id = ASSISTANT_ID or assistant_id
        self.thread_id = THREAD_ID or thread_id
        # If thread is empty, add examples to the thread
        if new_thread:
            print("There is no thread id, adding examples to thread.")
            self.logger.info(f"Adding examples to the thread {self.thread_id}")
            # Add examples to the thread
            for criterion, simpler_criterion in self.EXAMPLES.items():
                self.add_example_to_thread(criterion, simpler_criterion)
            self.run_assistant_single_time()

    def run_assistant_single_time(self, instructions=None):
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id,
            instructions=instructions,
        )
        self.logger.info(f"Assistant run created with ID: {run.id}")
        return self.wait_for_run_completion(run.id)

    def add_example_by_batching(self, examples: list):
        for example in examples:
            self.add_example_to_thread(example["input"], example["output"])

