from hmac import new
import os
from dotenv import load_dotenv

from GPT_assistant.base_assistant import BaseAssistant
from log_engine.log import Log
from utilities.utils import save_to_env_file
#from utils import save_to_env_file

load_dotenv()  # Load environment variables

#SR_100_MODEL = "gpt-4-0125-preview"
SR_100_MODEL = "gpt-4-turbo-2024-04-09"
#SR_100_MODEL = "gpt-3.5-turbo-0125"

SR_100_MODEL_NAME = "SR_100_ASSISTANT"
SR_100_MODEL_ID = f"{SR_100_MODEL_NAME}_ID"
SR_100_THREAD_ID = f"{SR_100_MODEL_NAME}_THREAD_ID"
# === Create Assistant ===



class SR_100_Assistant(BaseAssistant):
    ASSISTANT_INSTRUCTIONS = """Evaluate the provided text based on how well it meets the specified criterion. Assign a percentage score. Provide two lists of reasons: one listing positive aspects that contributed to the score, and another listing negative aspects that prevented a higher score. Each reason should be concise, not exceeding 40 words.
    Output Format: Use "SCORE:" before stating the score, Use "POSITIVE REASON:" before stating the positive reason part, and use "Negative REASON:" before stating the negative reason.For negative and positive reasons parts, using asterisks to start bullets (each bullet related to a different reason) of each part . Clearly distinguish between positive and negative reasons."""
    CREATE_THREAD_MESSAGE = """Please follow the instructions and following examples to generate the scores and reasons."""
    #SINGLE_TASK = """Please follow the examples that I Give you at the starting message of this thread."""
    EXAMPLES = {
        """the provided text: As part of our recent community initiative, we partnered with the local Chamber of Commerce to host a series of networking events. These gatherings were designed to foster connections and facilitate communication among small business owners and local leaders. The events proved highly successful, creating numerous new collaborations and enhancing community engagement. Our direct communication with these organizations enabled us to tailor the events to the specific needs and interests of all participants.
        the provide criterion: the section include information about at least one connection and communication experience with others and organizations""":
        """SCORE: 100%
        POSITIVE REASONS:
        *Describes a successful partnership with the local Chamber of Commerce.
        *Clearly mentions the facilitation of networking events designed to foster communication and connections.
        NEGATIVE REASONS:
        *None.""",

        """In our latest quarterly review, we focused on evaluating the impact of our community projects. While we gathered significant data on the effectiveness of our initiatives, we briefly mentioned a joint effort with a local school to enhance educational programs. However, detailed interactions with the school or other organizations were not covered, limiting the depth of communication information provided.
        the provide criterion: the section include information about at least one connection and communication experience with others and organizations""":
        """SCORE: 50%
        POSITIVE REASONS:
        *Mentions a joint effort with a local school, indicating some level of organizational interaction.
        NEGATIVE REASONS:
        *Lacks detailed information about the communication process with the school or other organizations.
        *Provides limited insight into the nature and effectiveness of the connections made.
        """,

        """Our latest quarterly report focused solely on internal staff training sessions aimed at enhancing individual skills within our team. We concentrated on developing new techniques in data analysis and project management. No external collaborations or communications with other organizations or community members were initiated or mentioned during this period, as the focus was strictly on internal capacity building.
        the provide criterion: the section include information about at least one connection and communication experience with others and organizations""":
        """SCORE: 0%
        POSITIVE REASONS:
        *None.
        NEGATIVE REASONS:
        *Completely omits any mention of external collaborations or communications.
        *Focuses exclusively on internal staff training without any reference to interactions with other organizations or community efforts.
        """,
   }

    logger = Log("SR_100_Assistant", "SR_100_assistant.log")

    def __init__(self, assistant_id=None, thread_id=None):

        logger = Log("SR_100_Assistant", "SR_100_assistant.log")
        #super().__init__(SR_MODEL_NAME, assistant_id, thread_id, logger)
        super().__init__(SR_100_MODEL_NAME, assistant_id, thread_id, self.logger)

        ASSISTANT_ID = os.getenv(SR_100_MODEL_ID)
        THREAD_ID = os.getenv(SR_100_THREAD_ID)

        # Flag to check if a new thread is created
        new_thread = False

        if not ASSISTANT_ID and not assistant_id:
            ASSISTANT_ID = self.create_assistant(
                SR_100_MODEL_NAME, self.ASSISTANT_INSTRUCTIONS, SR_100_MODEL
            )
            save_to_env_file(SR_100_MODEL_ID, ASSISTANT_ID)

        if not THREAD_ID and not thread_id:
            #THREAD_ID = self.create_thread()
            THREAD_ID = self.create_thread(user_message=self.CREATE_THREAD_MESSAGE)
            save_to_env_file(SR_100_THREAD_ID, THREAD_ID)
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

