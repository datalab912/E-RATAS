from hmac import new
import os
from dotenv import load_dotenv

from GPT_assistant.base_assistant import BaseAssistant
from log.log import Log
from utilities.utils import save_to_env_file

load_dotenv()  # Load environment variables

ACT_MODEL = "gpt-3.5-turbo-0125"
ACT_MODEL_NAME = "ACT_ASSISTANT"
ACT_MODEL_ID = f"{ACT_MODEL_NAME}_ID"
ACT_THREAD_ID = f"{ACT_MODEL_NAME}_THREAD_ID"
# === Create Assistant ===


class ACTAssistant(BaseAssistant):
    ASSISTANT_INSTRUCTIONS = """You are a goal detective! Your job is to find the main purpose hidden within a paragraph of text.
    Please extract the main goal in less than 3 bullet points. Remember, the main goal should cover all the concepts mentioned in the text"""
    CREATE_THREAD_MESSAGE = "You will be given several examples to follow."
    # SINGLE_PARAGRAPH_GOAL = """Please extract the main goal or abstractive summary of a text for a paragraph node,
    #         main goal need to cover all concept mention in the text. Please provide the goal in less than 3 bullet points."""
    EXAMPLES = {
        """In mathematics, fractions represent parts of a whole.
        The numerator (the number above the line) indicates how many parts we have, while the denominator (the number below the line) represents the total number of equal parts in the whole.
        For example, in the fraction 3/4, we have 3 out of 4 total parts.""": """- Fractions represent parts of a whole
        - Fractions use a numerator (top) to show parts taken and a denominator (bottom) to show total parts.""",
        """Symbolism in William Shakespeare's 'Hamlet' adds layers of meaning to the play.
        The recurring motif of poison symbolizes corruption and revenge.
        Ophelia's flowers represent themes of innocence, madness, and death.
        These symbols deepen the exploration of complex human emotions and motivations.""": """-Symbolism is a key literary device in 'Hamlet'.
        -Poison represents corruption/revenge, while Ophelia's flowers symbolize innocence, madness, and death.""",
        """The scientific method involves systematic observation and experimentation.
        Scientists start by asking a question, forming a hypothesis, and designing an experiment to test it.
        Data is collected and analyzed, leading to conclusions that either support or refute the hypothesis""": """- The scientific method is a process of inquiry and testing.
        - Key steps include questions, hypotheses, experiments, data analysis, and conclusions.""",
    }
    logger = Log("ACT_Assistant", "act_assistant.log")

    def __init__(self, assistant_id=None, thread_id=None):
        super().__init__(ACT_MODEL_NAME, assistant_id, thread_id, self.logger)

        # Check if the assistant ID and thread ID are already set in the environment
        ASSISTANT_ID = os.getenv(ACT_MODEL_ID)
        THREAD_ID = os.getenv(ACT_THREAD_ID)

        # Flag to check if a new thread is created
        new_thread = False

        # Create a new assistant if the ID is not set
        if not ASSISTANT_ID and not assistant_id:
            ASSISTANT_ID = self.create_assistant(
                ACT_MODEL_NAME, self.ASSISTANT_INSTRUCTIONS, ACT_MODEL
            )
            save_to_env_file(ACT_MODEL_ID, ASSISTANT_ID)

        # Create a new thread if the ID is not set
        if not THREAD_ID and not thread_id:
            THREAD_ID = self.create_thread(user_message=self.CREATE_THREAD_MESSAGE)
            save_to_env_file(ACT_THREAD_ID, THREAD_ID)
            new_thread = True

        # Set the assistant and thread IDs
        self.assistant_id = ASSISTANT_ID or assistant_id
        self.thread_id = THREAD_ID or thread_id

        # If thread is empty, add examples to the thread
        if new_thread:
            print("There is no thread id, adding examples to thread.")
            self.logger.info(f"Adding examples to the thread {self.thread_id}")
            # Add examples to the thread
            for paragraph, goal in self.EXAMPLES.items():
                self.add_example_to_thread(paragraph, goal)
            self.run_assistant_single_time()

    def run_assistant_single_time(self, instructions=None):
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id,
            instructions=instructions,
        )
        self.logger.info(f"Assistant run created with ID: {run.id}")
        return self.wait_for_run_completion(run.id)


# assistant = ACTAssistant()

# SAMPLE_PARAGRAPH = """
# ITIC global as many big names partner under their belt and the deliverable products they are
# working with has vast concept in upcoming times like cloud services, networking, cyber
# security, The ITIC is providing great opportunities to the new students of background of data
# science, cyber security and network engineers as well as it also providing the research
# centre for artificial intelligence which is remarkable and giving hands on experience of
# working on Telstra product and services for the students its big opportunity to grab in this
# crucial times where pandemic has given us big hit in all regards to have the opportunity to
# explore all these learning from the university was quite a challenge due to past
# circumstances while ITIC has taken the lead in that learning department and providing the
# chance to learn in professional environment will open new gates of opportunities for the
# students. The career consulting you get while getting their training program it should be
# highlighted here as it’s not an easy thing to get in real world. ITIC is doing an great job of
# creating opportunities in all big tech fields which is going to change the world and having
# experience to learn on cisco technologies for networking students is a great way of
# experiencing their theoretical concepts.
# """
# assistant.add_message_to_thread("Paragraph:\n" + SAMPLE_PARAGRAPH)
# assistant.run_assistant_single_time()
