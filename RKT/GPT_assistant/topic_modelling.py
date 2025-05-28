from hmac import new
import os
from dotenv import load_dotenv

from GPT_assistant.base_assistant import BaseAssistant
from log_engine.log import Log
from utilities.utils import save_to_env_file
#from utils import save_to_env_file

load_dotenv()  # Load environment variables

#TM_MODEL = "gpt-4-0125-preview"
TM_MODEL = "gpt-4-turbo-2024-04-09"
#M_MODEL = "gpt-3.5-turbo-0125"

TM_MODEL_NAME = "TM_ASSISTANT"
TM_MODEL_ID = f"{TM_MODEL_NAME}_ID"
TM_THREAD_ID = f"{TM_MODEL_NAME}_THREAD_ID"
# === Create Assistant ===



class TM_Assistant(BaseAssistant):
    ASSISTANT_INSTRUCTIONS = """You are an expert responsible for working on the rubric criteria of an exam. Your role involves breaking down the provided criteria into simpler sub-criteria so that I can use these more straightforward sub-criteria to assess answers more easily.
    Divide the provided rubric criterion into distinct and simpler sub-criteria. Each sub-criterion should cover a different topic or area within the original criterion. All sub-criteria must be grouped under the same level of detail, able to reconstruct the original criterion when combined. Consider these 7 instruction during the criterion division: 
    1- Read the Criterion Thoroughly: Understand the overall theme and elements of the criterion.
    2- Identify Distinct Areas: Look for distinct topics or areas within the criterion that can be separated.
    3- Construct Sub-Criteria: Create sub-criteria that focus on these distinct areas, ensuring each is comprehensive and preserves the content of the original criterion. Use "***" to start each sub-criterion.
    4- All divided subcriteria are of roughly equal worth in scoring and have approximately the same impact on scoring.
    6- Check Completeness: Ensure that all sub-criteria together cover the entire content of the original criterion without redundancy.
    7- Return Unchanged if Indivisible: If no distinct areas can be identified, return the original criterion unchanged.
    8- do not do summarization or delete any words when you want to generate sub-criteria
    9- Do not divide the content of the provided criterion using formats like {{any text}} or {any text{WHOLE}}. This means that the entire content within this format should belong to a single subcriterion."""
    CREATE_THREAD_MESSAGE = """Please follow the instructions and following examples to generate the sub-criteria."""
    #SINGLE_TASK = """Please follow the examples that I Give you at the starting message of this thread."""
    EXAMPLES = {
        """The Document should have title page (essential).
        The title page of the report must include:
        a. Name of the organization
        b. Name of the internee, Student ID and session""":
        """***Existing Title Page Section (essential)
        ***The title page of the report must include:
        a. Name of the organization
        b. Name of the internee, Student ID and session""",

        """The title page of the report should include:
        a. Name of the organization
        b. Name of the internee, Student ID and session""": 
        """***Title page of the report should include Name of the organization
        ***Title page of the report should include Existing Name of the internee, Student ID and session""",

        """Title page should have Name of the organization""": 
        """***Title page should have Name of the organization""",

        """Title page of the report should have Existing Name of the internee, Student ID and session""":
        """***Title page of the report should have Existing Name of the internee
        ***Title page of the report should have Student ID 
        ***Title page of the report should have session""",

        """The reflective journal section should include identification of at least 3 strengths and 3 weaknesses. describe how these strengths and weaknesses have been evidenced and addressed during your internship""":
        """*** The reflective journal should include Identification of at least 3 strengths
        How these strengths have been evidenced and addressed during your internship
        *** The reflective journal should include Identification of at least 3 weaknesses.
        How these weaknesses have been evidenced and addressed during your internship""",

        """present an analysis of a specific problem you encountered during the internship. This analysis of the problem should identify its significance, alternative solutions you considered in solving the problem, justification of solutions and outcomes.""":
        """*** present an analysis of a specific problem you encountered during the internship. 
        *** This analysis of the problem should identify its significance, alternative solutions you considered in solving the problem, justification of solutions and outcomes.""",

        """The progress report should have weekly progress from week 1 to week 3 update sections (essential) including a summary of completed tasks and current in-progress tasks for the weeks.""":
        """*** Weekly Progress Update - Week 1 (essential) should include:
        Summary of completed tasks and Current in-progress tasks the  week

        *** Weekly Progress Update - Week 2 (essential) should include:
        Summary of completed tasks and Current in-progress tasks the  week

        *** Weekly Progress Update - Week 3 (essential) should include:
        Summary of completed tasks and Current in-progress tasks the  week """,

        """Weekly Progress Update - Week 1 (essential) should include:
        Summary of completed tasks
        Current in-progress tasks
        Any challenges or blockers faced
        Plan for the following week""":
        """*** Weekly Progress Update - Week 1 (essential) should include:
        Summary of completed tasks
        *** Weekly Progress Update - Week 1 (essential) should include:
        Current in-progress tasks
        *** Weekly Progress Update - Week 1 (essential) should include:
        Any challenges or blockers faced
        *** Weekly Progress Update - Week 1 (essential) should include:
        Plan for the following week""",

        """The personal development section must be divided into two semester parts: S1, and S2
        Each semester  S1, and S2. should consist of entries that address specifics from that period, encompassing:
        1.At least one major project or initiative
        2.At least one significant milestone or achievement

        For all projects and initiatives, describe:
        -The personal growth experienced during the project
        -Evidence of skill application and integration during the project

        For all milestones or achievements:
        - Reflect on the individual's feelings about learning through these experiences
        - Show how these experiences have contributed to personal and professional growth""":
        """*** The personal development section must be divided into two semester parts: S1, and S2

        *** Each semester  S1, and S2. should consist of entries that address specifics from that period, encompassing:
        1.At least one major project or initiative
        2.At least one significant milestone or achievement

        For all projects and initiatives, describe:
        -The personal growth experienced during the project
        -Evidence of skill application and integration during the project

        For all milestones or achievements:
        - Reflect on the individual's feelings about learning through these experiences
        - Show how these experiences have contributed to personal and professional growth""",

        """semester  S1 should consist of entries that address specifics from that period, encompassing:

        1.At least one major project or initiative
        2.At least one significant milestone or achievement

        For all projects and initiatives, describe:
        -The personal growth experienced during the project
        -Evidence of skill application and integration during the project

        For all milestones or achievements:
        - Reflect on the individual's feelings about learning through these experiences
        - Show how these experiences have contributed to personal and professional growth""":

        """*** semester  S1 should consist of entries that address specifics from that period, encompassing at least one major project or initiative

        For all projects and initiatives, describe:
        -The personal growth experienced during the project
        -Evidence of skill application and integration during the project

        *** semester  S1 should consist of entries that address specifics from that period, encompassing at least one significant milestone or achievemen

        For all milestones or achievements:
        - Reflect on the individual's feelings about learning through these experiences
        - Show how these experiences have contributed to personal and professional growth""",

        """The personal development section must be divided into four quarterly parts: Q1, Q2, Q3, and Q4.""":
        """***The personal development section must be divided into four quarterly parts: Q1, Q2, Q3, and Q4.""",

        """semester  S1 should consist of entries that address specifics from that period, encompassing at least one major project or initiative

        For all projects and initiatives, describe:
        -The personal growth experienced during the project
        -Evidence of skill application and integration during the project""":
        """***semester  S1 should consist of entries that address specifics from that period, encompassing at least one major project or initiative

        *** For all projects and initiatives of semester S1, describe:
        -The personal growth experienced during the project
        -Evidence of skill application and integration during the project""",


        """For all projects and initiatives of semester S1, describe:
        -The personal growth experienced during the project
        -Evidence of skill application and integration during the project""":
        """*** For all projects and initiatives of semester S1, describe:
        -The personal growth experienced during the project

        *** For all projects and initiatives of semester S1, describe:
        -Evidence of skill application and integration during the project""",

        """semester  S1 should consist of entries that address specifics from that period, encompassing at least one major project or initiative""":
        """***semester  S1 should consist of entries that address specifics from that period, encompassing at least one major project or initiative""",

        """Evaluate the effectiveness and efficiency of the tasks or assignments or activities""":
        """***Evaluate the effectiveness and efficiency of the tasks or assignments or activities""",

        """Analyze the student's own performance as a learner relted to connection and Communication expreince with others and organizations""":
        """***Analyze the student's own performance as a learner relted to connection and Communication expreince with others and organizations""",

        """Plan how the information related to connection and Communication expreince with others and organizations will be useful to the students""":
        """***Plan how the information related to connection and Communication expreince with others and organizations will be useful to the students""",

        """The submission must contain a dedicated section titled 'Project Progress Overview.' (essential)
        The 'Project Progress Overview' should be broken down into 10 parts, each corresponding to Phases 1 through 10 of the project's lifecycle.
        For each part related to Phases 1 through 10, the details on: 1) design or development obstacles, 2) key takeaways or learning points, 3) teamwork or expert consultation should address the following aspects:
        For all design or development obstacles:
        Analyze the difficulty and uniqueness of the obstacles faced.
        Offer a straightforward and unbiased description of the strategies used to address the issues, including any initial theories.
        For all key takeaways or learning points:
        Discuss “What did you uncover, realize, or modify during this phase?” in terms of key takeaways or learning points.
        Provide a neutral account and justification for the conclusions or discoveries made.
        For all teamwork or expert consultation:
        Assess the success and influence of the collaboration or expert input.
        Detail the decisions or insights gained from collaborating with team members or consulting with experts.""":
        """***The submission must contain a dedicated section titled 'Project Progress Overview.' (essential)

        ***The 'Project Progress Overview' should be broken down into 10 parts, each corresponding to Phases 1 through 10 of the project's lifecycle.

        ***For each part related to Phases 1 through 10, the details on: 1) design or development obstacles, 2) key takeaways or learning points, 3) teamwork or expert consultation should address the following aspects:

        For all design or development obstacles:
        Analyze the difficulty and uniqueness of the obstacles faced.
        Offer a straightforward and unbiased description of the strategies used to address the issues, including any initial theories.

        For all key takeaways or learning points:
        Discuss “What did you uncover, realize, or modify during this phase?” in terms of key takeaways or learning points.
        Provide a neutral account and justification for the conclusions or discoveries made.

        For all teamwork or expert consultation:
        Assess the success and influence of the collaboration or expert input.
        Detail the decisions or insights gained from collaborating with team members or consulting with experts.""",

        """For each part related to Phases 1 have the details on: 1) design or development obstacles, 2) key takeaways or learning points, 3) teamwork or expert consultation, and  should address the following aspects:

        For all design or development obstacles:
        -Analyze the difficulty and uniqueness of the obstacles faced.
        -Offer a straightforward and unbiased description of the strategies used to address the issues, including any initial theories.

        For all key takeaways or learning points:
        -Discuss “What did you uncover, realize, or modify during this phase?” in terms of key takeaways or learning points.
        Provide a neutral account and justification for the conclusions or discoveries made.

        For all teamwork or expert consultation:
        -Assess the success and influence of the collaboration or expert input.
        -Detail the decisions or insights gained from collaborating with team members or consulting with experts.""" :
        """***For each part related to Phases 1 have design or development obstacles. For all design or development obstacles:
        -Analyze the difficulty and uniqueness of the obstacles faced.
        -Offer a straightforward and unbiased description of the strategies used to address the issues, including any initial theories.

        *** For each part related to Phases 1 have key takeaways or learning points. For all key takeaways or learning points:
        -Discuss “What did you uncover, realize, or modify during this phase?” in terms of key takeaways or learning points.
        Provide a neutral account and justification for the conclusions or discoveries made.

        ***For each part related to Phases 1 have teamwork or expert consultation. For all teamwork or expert consultation:
        -Assess the success and influence of the collaboration or expert input.
        -Detail the decisions or insights gained from collaborating with team members or consulting with experts.
        """,
    }

    logger = Log("TM_Assistant", "tm_assistant.log")

    def __init__(self, assistant_id=None, thread_id=None):

        logger = Log("TM_Assistant", "tm_assistant.log")
        #super().__init__(TM_MODEL_NAME, assistant_id, thread_id, logger)
        super().__init__(TM_MODEL_NAME, assistant_id, thread_id, self.logger)

        ASSISTANT_ID = os.getenv(TM_MODEL_ID)
        THREAD_ID = os.getenv(TM_THREAD_ID)

        ASSISTANT_ID = "asst_8enXPhdXd3OlB2ZSnpD1wsT2"
        THREAD_ID = "thread_R7gBZ9uIxChJEscUXWEKyuGi"

        # Flag to check if a new thread is created
        new_thread = False

        if not ASSISTANT_ID and not assistant_id:
            ASSISTANT_ID = self.create_assistant(
                TM_MODEL_NAME, self.ASSISTANT_INSTRUCTIONS, TM_MODEL
            )
            save_to_env_file(TM_MODEL_ID, ASSISTANT_ID)

        if not THREAD_ID and not thread_id:
            #THREAD_ID = self.create_thread()
            THREAD_ID = self.create_thread(user_message=self.CREATE_THREAD_MESSAGE)
            save_to_env_file(TM_THREAD_ID, THREAD_ID)
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

