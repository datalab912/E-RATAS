from hmac import new
import os
from dotenv import load_dotenv

from GPT_assistant.base_assistant import BaseAssistant
from log_engine.log import Log
from utilities.utils import save_to_env_file
#from utils import save_to_env_file

load_dotenv()  # Load environment variables

#SR_100_WHOLE_MODEL = "gpt-4-0125-preview"
SR_100_WHOLE_MODEL = "gpt-4-turbo-2024-04-09"
#SR_100_WHOLE_MODEL = "gpt-3.5-turbo-0125"

SR_100_WHOLE_MODEL_NAME = "SR_100_WHOLE_ASSISTANT"
SR_100_WHOLE_MODEL_ID = f"{SR_100_WHOLE_MODEL_NAME}_ID"
SR_100_WHOLE_THREAD_ID = f"{SR_100_WHOLE_MODEL_NAME}_THREAD_ID"
# === Create Assistant ===



class SR_100_WHOLE_Assistant(BaseAssistant):
    ASSISTANT_INSTRUCTIONS = """Evaluate the provided text based on how well it meets the specified criterion. Assign a percentage score. Provide two lists of reasons: one listing positive aspects that contributed to the score, and another listing negative aspects that prevented a higher score. Each reason should be concise, not exceeding 40 words.
    Note that you will receive the text in several messages. You need to score and provide both a positive and a negative reasoning for all the messages collectively, not separately. In the last message, you will receive the provided criterion and the total number of messages that you need to score and reason (positive and negative) for, treating all these messages as one text
    Output Format: Use "SCORE:" before stating the score, Use "POSITIVE REASON:" before stating the positive reason part, and use "Negative REASON:" before stating the negative reason.For negative and positive reasons parts, using asterisks to start bullets (each bullet related to a different reason) of each part . Clearly distinguish between positive and negative reasons."""
    CREATE_THREAD_MESSAGE = """Please follow the instructions and the examples provided to generate the scores and reasons. """
    #SINGLE_TASK = """Please follow the examples that I Give you at the starting message of this thread."""
    EXAMPLES = {
        
   }

    logger = Log("SR_100_WHOLE_Assistant", "SR_100_WHOLE_assistant.log")

    def __init__(self, assistant_id=None, thread_id=None):

        logger = Log("SR_100_WHOLE_Assistant", "SR_100_WHOLE_assistant.log")
        #super().__init__(SR_MODEL_NAME, assistant_id, thread_id, logger)
        super().__init__(SR_100_WHOLE_MODEL_NAME, assistant_id, thread_id, self.logger)

        ASSISTANT_ID = os.getenv(SR_100_WHOLE_MODEL_ID)
        THREAD_ID = os.getenv(SR_100_WHOLE_THREAD_ID)

        # Flag to check if a new thread is created
        new_thread = False

        if not ASSISTANT_ID and not assistant_id:
            ASSISTANT_ID = self.create_assistant(
                SR_100_WHOLE_MODEL_NAME, self.ASSISTANT_INSTRUCTIONS, SR_100_WHOLE_MODEL
            )
            save_to_env_file(SR_100_WHOLE_MODEL_ID, ASSISTANT_ID)

        if not THREAD_ID and not thread_id:
            #THREAD_ID = self.create_thread()
            THREAD_ID = self.create_thread(user_message=self.CREATE_THREAD_MESSAGE)
            save_to_env_file(SR_100_WHOLE_THREAD_ID, THREAD_ID)
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

