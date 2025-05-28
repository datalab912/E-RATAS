import os
import json
from openai import AzureOpenAI
    
client = AzureOpenAI(
    api_key="a1d43fe4425c41cdb5913f551bcd5b5d",  
    api_version="2024-05-01-preview",
    azure_endpoint = "https://prd-auae-core-oai-apim-01.azure-api.net/prd-auae-core-openai-api-02/"
    )

# Create an assistant
assistant = client.beta.assistants.create(
    name="Subcriteria_generation",
    instructions= 
    f"You are an expert responsible for working on the rubric criteria of an exam. Your role involves breaking down the provided criteria into simpler sub-criteria so that I can use these more straightforward sub-criteria to assess answers more easily."
    f"Divide the provided rubric criterion into distinct and simpler sub-criteria. Each sub-criterion should cover a different topic or area within the original criterion. All sub-criteria must be grouped under the same level of detail, able to reconstruct the original criterion when combined."
    f"Consider these 8 instruction during the criterion division:" 
    f"1- Read the Criterion Thoroughly: Understand the overall theme and elements of the criterion."
    f"2- Identify Distinct Areas: Look for distinct topics or areas within the criterion that can be separated."
    f"3- Construct Sub-Criteria: Create sub-criteria that focus on these distinct areas, ensuring each is comprehensive and preserves the content of the original criterion. Use '***' to start each sub-criterion."
    f"4- All divided subcriteria are of roughly equal worth in scoring and have approximately the same impact on scoring."
    f"6- Check Completeness: Ensure that all sub-criteria together cover the entire content of the original criterion without redundancy."
    f"7- Return Unchanged if Indivisible: If no distinct areas can be identified, return the original criterion unchanged."
    f"8- do not do summarization and uses all words when you want to generate sub-criteria"
    #f"9- Do not divide the content of the provided criterion using formats like "{{any text}}" or "{any text{WHOLE}}". This means that the entire content within this format should belong to a single subcriterion."
    ,
    #tools=[{"type": "text_interpreter"}],
    model="gpt-4o" #You must replace this value with the deployment name for your model.
)



# Create a new thread for conversation
title_thread = client.beta.threads.create()
thread_id = title_thread.id
assistant_id = assistant.id

# ADDING EXAMPLES TO THE THREAD:
# Example 1:
client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=(
        "Now, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: {The Document should have title page {essential}}. \nThe title page of the report must include: \na. Name of the organization \nb. Name of the internee, Student ID and session'\n"
    )
)


client.beta.threads.messages.create(
    thread_id=thread_id,
    role="assistant",
    content=(
        "***{Existing Title Page Section {essential}} \n***The title page of the report must include: \na. Name of the organization \nb. Name of the internee, Student ID and session"
    )
)


# Example 2:
client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=(
        "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: The title page of the report should include: \na. Name of the organization \n b. Name of the internee, Student ID and session"
    )
)

client.beta.threads.messages.create(
    thread_id=thread_id,
    role="assistant",
    content=(
        "***Title page of the report should include Name of the organization \n***Title page of the report should include Existing Name of the internee, Student ID and session"
    )
)


# Example 3:
client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=(
        "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: Title page should have Name of the organization'\n"
        "Ideal Output sub-criteria: '***Title page should have Name of the organization'"
    )
)

client.beta.threads.messages.create(
    thread_id=thread_id,
    role="assistant",
    content=(
        "***Title page should have Name of the organization"
    )
)

# Example 4:
client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=(
        "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is:Title page of the report should have Existing Name of the internee, Student ID and session"
        )
)

client.beta.threads.messages.create(
    thread_id=thread_id,
    role="assistant",
    content=(
        "***Title page of the report should have Existing Name of the internee \n***Title page of the report should have Student ID \n***Title page of the report should have session"
    )
)

# Example 5:
client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=(
        "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: The reflective journal section should include identification of at least 3 strengths and 3 weaknesses. describe how these strengths and weaknesses have been evidenced and addressed during your internship"
    )
)

client.beta.threads.messages.create(
    thread_id=thread_id,
    role="assistant",
    content=(
        "*** The reflective journal should include Identification of at least 3 strengths How these strengths have been evidenced and addressed during your internship\n*** The reflective journal should include Identification of at least 3 weaknesses. How these weaknesses have been evidenced and addressed during your internship"
    )
)

# Example 6:
client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=(
        "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: present an analysis of a specific problem you encountered during the internship. This analysis of the problem should identify its significance, alternative solutions you considered in solving the problem, justification of solutions and outcomes."
    )
)

client.beta.threads.messages.create(
    thread_id=thread_id,
    role="assistant",
    content=(
        "*** present an analysis of a specific problem you encountered during the internship. \n*** This analysis of the problem should identify its significance, alternative solutions you considered in solving the problem, justification of solutions and outcomes."
    )
)

# Example 7:
client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=(
        "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: present an analysis of a specific problem you encountered during the internship. This analysis of the problem should identify its significance, alternative solutions you considered in solving the problem, justification of solutions and outcomes."
    )
)

client.beta.threads.messages.create(
    thread_id=thread_id,
    role="assistant",
    content=(
        "*** present an analysis of a specific problem you encountered during the internship. \n*** This analysis of the problem should identify its significance, alternative solutions you considered in solving the problem, justification of solutions and outcomes."
    )
)

# Example 8:
client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=(
        "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: The progress report should have weekly progress from week 1 to week 3 update sections (essentia} including a summary of completed tasks and current in-progress tasks for the weeks."
    )
)

client.beta.threads.messages.create(
    thread_id=thread_id,
    role="assistant",
    content=(
        "*** Weekly Progress Update - Week 1 (essential) should include: \nSummary of completed tasks and Current in-progress tasks the  week \n*** Weekly Progress Update - Week 2 (essential) should include: Summary of completed tasks and Current in-progress tasks the  week \n*** Weekly Progress Update - Week 3 (essential) should include: Summary of completed tasks and Current in-progress tasks the  week"
    )
)

# Example 9:
client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=(
        "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: Weekly Progress Update - Week 1 (essential) should include: \nSummary of completed tasks \nCurrent in-progress tasks \nAny challenges or blockers faced \nPlan for the following week"
    )
)

client.beta.threads.messages.create(
    thread_id=thread_id,
    role="assistant",
    content=(
        "*** Weekly Progress Update - Week 1 (essential) should include: \nSummary of completed tasks \n*** Weekly Progress Update - Week 1 (essential) should include: \nCurrent in-progress tasks \n*** Weekly Progress Update - Week 1 (essential) should include: \nAny challenges or blockers faced \n*** Weekly Progress Update - Week 1 (essential) should include: \nPlan for the following week'"
    )
)

# Example 10:
client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=(
        "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: The personal development section must be divided into two semester parts: S1, and S2 \nEach semester  S1, and S2. should consist of entries that address specifics from that period, encompassing: \n1.At least one major project or initiative \n2.At least one significant milestone or achievement \nFor all projects and initiatives, describe: \n-The personal growth experienced during the project \n-Evidence of skill application and integration during the project \nFor all milestones or achievements: \n- Reflect on the individual's feelings about learning through these experiences \n- Show how these experiences have contributed to personal and professional growth"
    )
)

client.beta.threads.messages.create(
    thread_id=thread_id,
    role="assistant",
    content=(
        "*** The personal development section must be divided into two semester parts: S1, and S2 \n*** Each semester  S1, and S2. should consist of entries that address specifics from that period, encompassing: \n1.At least one major project or initiative \n2.At least one significant milestone or achievement \nFor all projects and initiatives, describe: \n-The personal growth experienced during the project \n-Evidence of skill application and integration during the project \nFor all milestones or achievements: \n- Reflect on the individual's feelings about learning through these experiences \n- Show how these experiences have contributed to personal and professional growth"
    )
)

# Example 11:
client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=(
        "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: semester  S1 should consist of entries that address specifics from that period, encompassing: \n1.At least one major project or initiative \n2.At least one significant milestone or achievement \nFor all projects and initiatives, describe: \n-The personal growth experienced during the project \n-Evidence of skill application and integration during the project \nFor all milestones or achievements: \n- Reflect on the individual's feelings about learning through these experiences \n- Show how these experiences have contributed to personal and professional growth"
    )
)

client.beta.threads.messages.create(
    thread_id=thread_id,
    role="assistant",
    content=(
        "*** semester  S1 should consist of entries that address specifics from that period, encompassing at least one major project or initiative \nFor all projects and initiatives, describe: \n-The personal growth experienced during the project \n-Evidence of skill application and integration during the project  \n*** semester  S1 should consist of entries that address specifics from that period, encompassing at least one significant milestone or achievemen \nFor all milestones or achievements: \n- Reflect on the individual's feelings about learning through these experiences \n- Show how these experiences have contributed to personal and professional growth"
    )
)

# Example 12:
client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=(
        "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: The personal development section must be divided into four quarterly parts: Q1, Q2, Q3, and Q4."
    )
)

client.beta.threads.messages.create(
    thread_id=thread_id,
    role="assistant",
    content=(
        "***The personal development section must be divided into four quarterly parts: Q1, Q2, Q3, and Q4."
    )
)

# Example 13:
client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=(
        "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: semester  S1 should consist of entries that address specifics from that period, encompassing at least one major project or initiative \nFor all projects and initiatives, describe: \n-The personal growth experienced during the project \n-Evidence of skill application and integration during the project"
    )
)

client.beta.threads.messages.create(
    thread_id=thread_id,
    role="assistant",
    content=(
        "***semester  S1 should consist of entries that address specifics from that period, encompassing at least one major project or initiative \n*** For all projects and initiatives of semester S1, describe: \n-The personal growth experienced during the project  \n-Evidence of skill application and integration during the project"
    )
)

# Example 14:
client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=(
        "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: For all projects and initiatives of semester S1, describe: \n-The personal growth experienced during the project \n-Evidence of skill application and integration during the project"
        )
)

client.beta.threads.messages.create(
    thread_id=thread_id,
    role="assistant",
    content=(
        "*** For all projects and initiatives of semester S1, describe: \n-The personal growth experienced during the project  \n*** For all projects and initiatives of semester S1, describe: \n-Evidence of skill application and integration during the project'"
    )
)

# Example 15:
client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=(
        "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: semester  S1 should consist of entries that address specifics from that period, encompassing at least one major project or initiative"
    )
)

client.beta.threads.messages.create(
    thread_id=thread_id,
    role="assistant",
    content=(
        "***semester  S1 should consist of entries that address specifics from that period, encompassing at least one major project or initiative"
    )
)

# Example 16:
client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=(
        "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: Evaluate the effectiveness and efficiency of the tasks or assignments or activities"
    )
)

client.beta.threads.messages.create(
    thread_id=thread_id,
    role="assistant",
    content=(
        "***Evaluate the effectiveness and efficiency of the tasks or assignments or activities"
    )
)

# Example 17:
client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=(
        "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: Analyze the student's own performance as a learner relted to connection and Communication expreince with others and organizations"
    )
)

client.beta.threads.messages.create(
    thread_id=thread_id,
    role="assistant",
    content=(
        "***Analyze the student's own performance as a learner relted to connection and Communication expreince with others and organizations"
    )
)

# Example 18:
client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=(
        "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: Plan how the information related to connection and Communication expreince with others and organizations will be useful to the students"
    )
)

client.beta.threads.messages.create(
    thread_id=thread_id,
    role="assistant",
    content=(
        "***Plan how the information related to connection and Communication expreince with others and organizations will be useful to the students"
    )
)

# Example 19:
client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=(
        "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: The submission must contain a dedicated section titled 'Project Progress Overview.' (essential) \nThe 'Project Progress Overview' should be broken down into 10 parts, each corresponding to Phases 1 through 10 of the project's lifecycle. \nFor each part related to Phases 1 through 10, the details on: 1) design or development obstacles, 2) key takeaways or learning points, 3) teamwork or expert consultation should address the following aspects: \nFor all design or development obstacles: \nAnalyze the difficulty and uniqueness of the obstacles faced. \nOffer a straightforward and unbiased description of the strategies used to address the issues, including any initial theories. \nFor all key takeaways or learning points: \nDiscuss “What did you uncover, realize, or modify during this phase?” in terms of key takeaways or learning points. \nProvide a neutral account and justification for the conclusions or discoveries made. \nFor all teamwork or expert consultation: \nAssess the success and influence of the collaboration or expert input. \nDetail the decisions or insights gained from collaborating with team members or consulting with experts."
    )
)

client.beta.threads.messages.create(
    thread_id=thread_id,
    role="assistant",
    content=(
        "***The submission must contain a dedicated section titled 'Project Progress Overview. (essential) \n***The 'Project Progress Overview' should be broken down into 10 parts, each corresponding to Phases 1 through 10 of the project's lifecycle.  \n***For each part related to Phases 1 through 10, the details on: 1) design or development obstacles, 2) key takeaways or learning points, 3) teamwork or expert consultation should address the following aspects: \nFor all design or development obstacles: \nAnalyze the difficulty and uniqueness of the obstacles faced. \nOffer a straightforward and unbiased description of the strategies used to address the issues, including any initial theories. \nFor all key takeaways or learning points: \nDiscuss “What did you uncover, realize, or modify during this phase?” in terms of key takeaways or learning points. \nProvide a neutral account and justification for the conclusions or discoveries made. \nFor all teamwork or expert consultation: \nAssess the success and influence of the collaboration or expert input.  \nDetail the decisions or insights gained from collaborating with team members or consulting with experts."
    )
)


# Example 20:
client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=(
        "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: For each part related to Phases 1 have the details on: 1) design or development obstacles, 2) key takeaways or learning points, 3) teamwork or expert consultation, and  should address the following aspects: \nFor all design or development obstacles: \n-Analyze the difficulty and uniqueness of the obstacles faced. \n-Offer a straightforward and unbiased description of the strategies used to address the issues, including any initial theories. \nFor all key takeaways or learning points: \n-Discuss “What did you uncover, realize, or modify during this phase?” in terms of key takeaways or learning points. \nProvide a neutral account and justification for the conclusions or discoveries made. \nFor all teamwork or expert consultation: \n-Assess the success and influence of the collaboration or expert input. \n-Detail the decisions or insights gained from collaborating with team members or consulting with experts."
    )
)

client.beta.threads.messages.create(
    thread_id=thread_id,
    role="assistant",
    content=(
        "***For each part related to Phases 1 have design or development obstacles. For all design or development obstacles: \n-Analyze the difficulty and uniqueness of the obstacles faced. \n-Offer a straightforward and unbiased description of the strategies used to address the issues, including any initial theories. \n*** For each part related to Phases 1 have key takeaways or learning points. For all key takeaways or learning points: \n-Discuss “What did you uncover, realize, or modify during this phase?” in terms of key takeaways or learning points. \nProvide a neutral account and justification for the conclusions or discoveries made. \n***For each part related to Phases 1 have teamwork or expert consultation. For all teamwork or expert consultation: \n-Assess the success and influence of the collaboration or expert input. \n-Detail the decisions or insights gained from collaborating with team members or consulting with experts."
    )
)


print(assistant_id)
print(thread_id)
