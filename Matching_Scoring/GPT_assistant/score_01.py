from hmac import new
import os
from dotenv import load_dotenv  

from GPT_assistant.base_assistant import BaseAssistant
from log_engine.log import Log
from utilities.utils import save_to_env_file
#from utils import save_to_env_file

load_dotenv()  # Load environment variables

#SR_01_MODEL = "gpt-4-0125-preview"
SR_01_MODEL = "gpt-4-turbo-2024-04-09"
#SR_01_MODEL = "gpt-3.5-turbo-0125"

SR_01_MODEL_NAME = "SR_01_ASSISTANT_v2"
SR_01_MODEL_ID = f"{SR_01_MODEL_NAME}_ID"
SR_01_THREAD_ID = f"{SR_01_MODEL_NAME}_THREAD_ID"
# === Create Assistant ===


class SR_01_Assistant(BaseAssistant):
    ASSISTANT_INSTRUCTIONS = """You are an expert responsible for scoring a provided text (as part of an answer) based on provided criteria (as part of a rubric for an exam). Your role involves scoring and providing the reasons behind the generated scores.
    Assess whether the provided text meets the specified criterion. Reward a score of 0 if it does not meet the criterion and a score of 1 if it does. Additionally, provide a concise reason (less than 20 words) explaining the basis for your scoring decision.
    Output Format: Use "SCORE:" before stating the score and Use "REASON:" before stating the reason"""
    CREATE_THREAD_MESSAGE = """Please follow the instructions and following examples to generate the scores and reasons."""
    #SINGLE_TASK = """Please follow the examples that I Give you at the starting message of this thread."""
    EXAMPLES = {
        """the provided text: In my recent role as a community outreach coordinator, I engaged extensively with local businesses and nonprofit organizations to foster partnerships that would benefit both our initiatives and the community at large. One notable collaboration was with the Green Spaces Initiative, a project aimed at increasing urban greenery. Together, we organized monthly community gardening events, which not only beautified the neighborhood but also provided a platform for residents to connect and communicate with one another, strengthening community bonds. This partnership proved instrumental in enhancing our outreach efforts and demonstrated the power of effective communication and cooperation between organizations working towards a common goal.
        the provide criterion: the section include information about at least one connection and communication experience with others and organizations""":
        """SCORE: 1
        REASON: The text successfully details a connection and communication experience, showcasing a collaborative effort between the community outreach coordinator and the Green Spaces Initiative, emphasizing effective organizational partnerships""",

        """As a community outreach coordinator, I have been focusing primarily on developing internal strategies to improve our team's efficiency and effectiveness. Over the past quarter, we’ve optimized our workflow by integrating new software tools that enhance project management and reporting capabilities. These improvements have led to a significant reduction in turnaround times for our projects and have increased our ability to handle multiple initiatives simultaneously. While these changes have greatly benefitted our internal operations, external communications and partnerships were not a focus during this period.
        the provide criterion: the section include information about at least one connection and communication experience with others and organizations""":
        """SCORE: 0
        REASON: The text does not mention any connections or communications with other individuals or organizations, focusing solely on internal improvements and not fulfilling the criterion.""",
   }

    logger = Log("SR_01_Assistant", "SR_01_assistant.log")

    def __init__(self, assistant_id=None, thread_id=None):

        logger = Log("SR_01_Assistant", "SR_01_assistant.log")
        #super().__init__(SR_MODEL_NAME, assistant_id, thread_id, logger)
        super().__init__(SR_01_MODEL_NAME, assistant_id, thread_id, self.logger)

        ASSISTANT_ID = os.getenv(SR_01_MODEL_ID)
        THREAD_ID = os.getenv(SR_01_THREAD_ID)

        ASSISTANT_ID="asst_NpAP5aeB2TUX1qsdEF8BG4AV"
        THREAD_ID="thread_CNu8i9h7yF6VCJRPchuvCD2N"

        # Flag to check if a new thread is created
        new_thread = False

        if not ASSISTANT_ID and not assistant_id:
            ASSISTANT_ID = self.create_assistant(
                SR_01_MODEL_NAME, self.ASSISTANT_INSTRUCTIONS, SR_01_MODEL
            )
            save_to_env_file(SR_01_MODEL_ID, ASSISTANT_ID)

        if not THREAD_ID and not thread_id:
            #THREAD_ID = self.create_thread()
            THREAD_ID = self.create_thread(user_message=self.CREATE_THREAD_MESSAGE)
            save_to_env_file(SR_01_THREAD_ID, THREAD_ID)
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

