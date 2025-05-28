import os
import json
from openai import AzureOpenAI
    
client = AzureOpenAI(
    api_key="*****",  
    api_version="2024-05-01-preview",
    azure_endpoint = "******"
    )

# Create an assistant
assistant = client.beta.assistants.create(
    name="score_01",
    instructions= 

    f"""You are an expert responsible for scoring a provided text (as part of an answer) based on provided criteria (as part of a rubric for an exam). Your role involves scoring and providing the reasons behind the generated scores.
    Assess whether the provided text meets the specified criterion.""" 
    f"""Reward a score of 0 if it does not meet the criterion and a score of 1 if it does."""
    f"""If the text partially meets the criterion, assign a score of 1 if the degree of compliance is greater than 65%; otherwise, assign a score of 0."""  
    f"""Additionally, provide a concise reason (less than 30 words) explaining the basis for your scoring decision"""
    f"""Output Format: Use "SCORE:" before stating the score and Use "REASON:" before stating the reason"""
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
        """follow this thread’s instructions and examples to generate a score, which is 0 or 1, and generate the reasons behind that score.
        The rubric criterion is: the section sould include information about at least one connection and communication experience with others and organizations 
        The provided text is: In my recent role as a community outreach coordinator, I engaged extensively with local businesses and nonprofit organizations to foster partnerships that would benefit both our initiatives and the community at large. One notable collaboration was with the Green Spaces Initiative, a project aimed at increasing urban greenery. Together, we organized monthly community gardening events, which not only beautified the neighborhood but also provided a platform for residents to connect and communicate with one another, strengthening community bonds. This partnership proved instrumental in enhancing our outreach efforts and demonstrated the power of effective communication and cooperation between organizations working towards a common goal."""
    )
)


client.beta.threads.messages.create(
    thread_id=thread_id,
    role="assistant",
    content=(
        """SCORE: 1
        REASON: The text successfully details a connection and communication experience, showcasing a collaborative effort between the community outreach coordinator and the Green Spaces Initiative, emphasizing effective organizational partnerships"""
    )
)


# Example 2:
client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=(
        """Great work! Please repeat the process for the newly provided rubric criterion and text. As with the previous messages, follow this thread’s instructions and examples to generate a score, which is 0 or 1, and generate the reasons behind that score.
        The new rubric criterion is: the section should include information about at least one connection and communication experience with others and organizations 
        the new provided text: As a community outreach coordinator, I have been focusing primarily on developing internal strategies to improve our team's efficiency and effectiveness. Over the past quarter, we’ve optimized our workflow by integrating new software tools that enhance project management and reporting capabilities. These improvements have led to a significant reduction in turnaround times for our projects and have increased our ability to handle multiple initiatives simultaneously. While these changes have greatly benefitted our internal operations, external communications and partnerships were not a focus during this period."""
    )
)

client.beta.threads.messages.create(
    thread_id=thread_id,
    role="assistant",
    content=(
        """SCORE: 0
        REASON: The text does not mention any connections or communications with other individuals or organizations, focusing solely on internal improvements and not fulfilling the criterion."""
    )
)


# Example 3:
client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=(
        """Great work! Please repeat the process for the newly provided rubric criterion and text. As with the previous messages, follow this thread’s instructions and examples to generate a score, which is 0 or 1, and generate the reasons behind that score.
        The new rubric criterion is: The response must mention at least one major location involved in the American Civil War, the approximate date range of the conflict, and at least two key historical figures. 
        The new provided text is: The American Civil war was important because it changed the country forever. Many people fought, and it had a big impact on politics."""
    )
)

client.beta.threads.messages.create(
    thread_id=thread_id,
    role="assistant",
    content=(
        """SCORE: 0
        REASON: No location, date, or figures mentioned."""
    )
)

# Example 4:
client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=(
        """Great work! Please repeat the process for the newly provided rubric criterion and text. As with the previous messages, follow this thread’s instructions and examples to generate a score, which is 0 or 1, and generate the reasons behind that score.
        The new rubric criterion is: The response must mention at least one major location involved in the American Civil War, the approximate date range of the conflict, and at least two key historical figures. 
        The new provided text is: The Civil War occurred in the mid-19th century, roughly from 1861 to 1865. It led to significant changes in the nation."""
        )
)

client.beta.threads.messages.create(
    thread_id=thread_id,
    role="assistant",
    content=(
        """SCORE: 0
        REASON: Only mentions the date range."""
    )
)

# Example 5:
client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=(
        """Great work! Please repeat the process for the newly provided rubric criterion and text. As with the previous messages, follow this thread’s instructions and examples to generate a score, which is 0 or 1, and generate the reasons behind that score.
        The new rubric criterion is: The response must mention at least one major location involved in the American Civil War, the approximate date range of the conflict, and at least two key historical figures.
        The new provided text is: The American Civil War started around 1861 and ended in 1865. A famous battle took place at Gettysburg. It was led, in part, by Abraham Lincoln, who was president at the time."""
    )
)

client.beta.threads.messages.create(
    thread_id=thread_id,
    role="assistant",
    content=(
        """SCORE: 1
        REASON: Adds location and one figure."""
    )
)

# Example 6:
client.beta.threads.messages.create(
    thread_id=thread_id,
    role="user",
    content=(
        """Great work! Please repeat the process for the newly provided rubric criterion and text. As with the previous messages, follow this thread’s instructions and examples to generate a score, which is 0 or 1, and generate the reasons behind that score.
        The new rubric criterion is: The response must mention at least one major location involved in the American Civil War, the approximate date range of the conflict, and at least two key historical figures.
        The new provided text is: The American Civil War lasted from 1861 to 1865 and was fought in several places, including Gettysburg, Pennsylvania. Key figures included President Abraham Lincoln, who issued the Emancipation Proclamation, and General Robert E. Lee, a leading commander of the Confederate Army."""
    )
)

client.beta.threads.messages.create(
    thread_id=thread_id,
    role="assistant",
    content=(
        """SCORE: 1
        REASON: Provides location, date range, and two figures."""
    )
)

# # Example 7:
# client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="user",
#     content=(
#         "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: present an analysis of a specific problem you encountered during the internship. This analysis of the problem should identify its significance, alternative solutions you considered in solving the problem, justification of solutions and outcomes."
#     )
# )

# client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="assistant",
#     content=(
#         "*** present an analysis of a specific problem you encountered during the internship. \n*** This analysis of the problem should identify its significance, alternative solutions you considered in solving the problem, justification of solutions and outcomes."
#     )
# )

# # Example 8:
# client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="user",
#     content=(
#         "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: The progress report should have weekly progress from week 1 to week 3 update sections (essentia} including a summary of completed tasks and current in-progress tasks for the weeks."
#     )
# )

# client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="assistant",
#     content=(
#         "*** Weekly Progress Update - Week 1 (essential) should include: \nSummary of completed tasks and Current in-progress tasks the  week \n*** Weekly Progress Update - Week 2 (essential) should include: Summary of completed tasks and Current in-progress tasks the  week \n*** Weekly Progress Update - Week 3 (essential) should include: Summary of completed tasks and Current in-progress tasks the  week"
#     )
# )

# # Example 9:
# client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="user",
#     content=(
#         "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: Weekly Progress Update - Week 1 (essential) should include: \nSummary of completed tasks \nCurrent in-progress tasks \nAny challenges or blockers faced \nPlan for the following week"
#     )
# )

# client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="assistant",
#     content=(
#         "*** Weekly Progress Update - Week 1 (essential) should include: \nSummary of completed tasks \n*** Weekly Progress Update - Week 1 (essential) should include: \nCurrent in-progress tasks \n*** Weekly Progress Update - Week 1 (essential) should include: \nAny challenges or blockers faced \n*** Weekly Progress Update - Week 1 (essential) should include: \nPlan for the following week'"
#     )
# )

# # Example 10:
# client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="user",
#     content=(
#         "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: The personal development section must be divided into two semester parts: S1, and S2 \nEach semester  S1, and S2. should consist of entries that address specifics from that period, encompassing: \n1.At least one major project or initiative \n2.At least one significant milestone or achievement \nFor all projects and initiatives, describe: \n-The personal growth experienced during the project \n-Evidence of skill application and integration during the project \nFor all milestones or achievements: \n- Reflect on the individual's feelings about learning through these experiences \n- Show how these experiences have contributed to personal and professional growth"
#     )
# )

# client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="assistant",
#     content=(
#         "*** The personal development section must be divided into two semester parts: S1, and S2 \n*** Each semester  S1, and S2. should consist of entries that address specifics from that period, encompassing: \n1.At least one major project or initiative \n2.At least one significant milestone or achievement \nFor all projects and initiatives, describe: \n-The personal growth experienced during the project \n-Evidence of skill application and integration during the project \nFor all milestones or achievements: \n- Reflect on the individual's feelings about learning through these experiences \n- Show how these experiences have contributed to personal and professional growth"
#     )
# )

# # Example 11:
# client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="user",
#     content=(
#         "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: semester  S1 should consist of entries that address specifics from that period, encompassing: \n1.At least one major project or initiative \n2.At least one significant milestone or achievement \nFor all projects and initiatives, describe: \n-The personal growth experienced during the project \n-Evidence of skill application and integration during the project \nFor all milestones or achievements: \n- Reflect on the individual's feelings about learning through these experiences \n- Show how these experiences have contributed to personal and professional growth"
#     )
# )

# client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="assistant",
#     content=(
#         "*** semester  S1 should consist of entries that address specifics from that period, encompassing at least one major project or initiative \nFor all projects and initiatives, describe: \n-The personal growth experienced during the project \n-Evidence of skill application and integration during the project  \n*** semester  S1 should consist of entries that address specifics from that period, encompassing at least one significant milestone or achievemen \nFor all milestones or achievements: \n- Reflect on the individual's feelings about learning through these experiences \n- Show how these experiences have contributed to personal and professional growth"
#     )
# )

# # Example 12:
# client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="user",
#     content=(
#         "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: The personal development section must be divided into four quarterly parts: Q1, Q2, Q3, and Q4."
#     )
# )

# client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="assistant",
#     content=(
#         "***The personal development section must be divided into four quarterly parts: Q1, Q2, Q3, and Q4."
#     )
# )

# # Example 13:
# client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="user",
#     content=(
#         "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: semester  S1 should consist of entries that address specifics from that period, encompassing at least one major project or initiative \nFor all projects and initiatives, describe: \n-The personal growth experienced during the project \n-Evidence of skill application and integration during the project"
#     )
# )

# client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="assistant",
#     content=(
#         "***semester  S1 should consist of entries that address specifics from that period, encompassing at least one major project or initiative \n*** For all projects and initiatives of semester S1, describe: \n-The personal growth experienced during the project  \n-Evidence of skill application and integration during the project"
#     )
# )

# # Example 14:
# client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="user",
#     content=(
#         "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: For all projects and initiatives of semester S1, describe: \n-The personal growth experienced during the project \n-Evidence of skill application and integration during the project"
#         )
# )

# client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="assistant",
#     content=(
#         "*** For all projects and initiatives of semester S1, describe: \n-The personal growth experienced during the project  \n*** For all projects and initiatives of semester S1, describe: \n-Evidence of skill application and integration during the project'"
#     )
# )

# # Example 15:
# client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="user",
#     content=(
#         "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: semester  S1 should consist of entries that address specifics from that period, encompassing at least one major project or initiative"
#     )
# )

# client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="assistant",
#     content=(
#         "***semester  S1 should consist of entries that address specifics from that period, encompassing at least one major project or initiative"
#     )
# )

# # Example 16:
# client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="user",
#     content=(
#         "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: Evaluate the effectiveness and efficiency of the tasks or assignments or activities"
#     )
# )

# client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="assistant",
#     content=(
#         "***Evaluate the effectiveness and efficiency of the tasks or assignments or activities"
#     )
# )

# # Example 17:
# client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="user",
#     content=(
#         "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: Analyze the student's own performance as a learner relted to connection and Communication expreince with others and organizations"
#     )
# )

# client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="assistant",
#     content=(
#         "***Analyze the student's own performance as a learner relted to connection and Communication expreince with others and organizations"
#     )
# )

# # Example 18:
# client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="user",
#     content=(
#         "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: Plan how the information related to connection and Communication expreince with others and organizations will be useful to the students"
#     )
# )

# client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="assistant",
#     content=(
#         "***Plan how the information related to connection and Communication expreince with others and organizations will be useful to the students"
#     )
# )

# # Example 19:
# client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="user",
#     content=(
#         "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: The submission must contain a dedicated section titled 'Project Progress Overview.' (essential) \nThe 'Project Progress Overview' should be broken down into 10 parts, each corresponding to Phases 1 through 10 of the project's lifecycle. \nFor each part related to Phases 1 through 10, the details on: 1) design or development obstacles, 2) key takeaways or learning points, 3) teamwork or expert consultation should address the following aspects: \nFor all design or development obstacles: \nAnalyze the difficulty and uniqueness of the obstacles faced. \nOffer a straightforward and unbiased description of the strategies used to address the issues, including any initial theories. \nFor all key takeaways or learning points: \nDiscuss “What did you uncover, realize, or modify during this phase?” in terms of key takeaways or learning points. \nProvide a neutral account and justification for the conclusions or discoveries made. \nFor all teamwork or expert consultation: \nAssess the success and influence of the collaboration or expert input. \nDetail the decisions or insights gained from collaborating with team members or consulting with experts."
#     )
# )

# client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="assistant",
#     content=(
#         "***The submission must contain a dedicated section titled 'Project Progress Overview. (essential) \n***The 'Project Progress Overview' should be broken down into 10 parts, each corresponding to Phases 1 through 10 of the project's lifecycle.  \n***For each part related to Phases 1 through 10, the details on: 1) design or development obstacles, 2) key takeaways or learning points, 3) teamwork or expert consultation should address the following aspects: \nFor all design or development obstacles: \nAnalyze the difficulty and uniqueness of the obstacles faced. \nOffer a straightforward and unbiased description of the strategies used to address the issues, including any initial theories. \nFor all key takeaways or learning points: \nDiscuss “What did you uncover, realize, or modify during this phase?” in terms of key takeaways or learning points. \nProvide a neutral account and justification for the conclusions or discoveries made. \nFor all teamwork or expert consultation: \nAssess the success and influence of the collaboration or expert input.  \nDetail the decisions or insights gained from collaborating with team members or consulting with experts."
#     )
# )


# # Example 20:
# client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="user",
#     content=(
#         "very good, do again for the next provided rubric criterion and like the previous messages, follow the instructions of this thread and examples to generate the sub-criteria for the new provided criterion. The new provided rubric criterion is: For each part related to Phases 1 have the details on: 1) design or development obstacles, 2) key takeaways or learning points, 3) teamwork or expert consultation, and  should address the following aspects: \nFor all design or development obstacles: \n-Analyze the difficulty and uniqueness of the obstacles faced. \n-Offer a straightforward and unbiased description of the strategies used to address the issues, including any initial theories. \nFor all key takeaways or learning points: \n-Discuss “What did you uncover, realize, or modify during this phase?” in terms of key takeaways or learning points. \nProvide a neutral account and justification for the conclusions or discoveries made. \nFor all teamwork or expert consultation: \n-Assess the success and influence of the collaboration or expert input. \n-Detail the decisions or insights gained from collaborating with team members or consulting with experts."
#     )
# )

# client.beta.threads.messages.create(
#     thread_id=thread_id,
#     role="assistant",
#     content=(
#         "***For each part related to Phases 1 have design or development obstacles. For all design or development obstacles: \n-Analyze the difficulty and uniqueness of the obstacles faced. \n-Offer a straightforward and unbiased description of the strategies used to address the issues, including any initial theories. \n*** For each part related to Phases 1 have key takeaways or learning points. For all key takeaways or learning points: \n-Discuss “What did you uncover, realize, or modify during this phase?” in terms of key takeaways or learning points. \nProvide a neutral account and justification for the conclusions or discoveries made. \n***For each part related to Phases 1 have teamwork or expert consultation. For all teamwork or expert consultation: \n-Assess the success and influence of the collaboration or expert input. \n-Detail the decisions or insights gained from collaborating with team members or consulting with experts."
#     )
# )


print(assistant_id)
print(thread_id)
