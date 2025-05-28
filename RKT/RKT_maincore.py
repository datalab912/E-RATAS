from RKT_Tree import RKTNode, load_tree_from_json, save_RKT_to_json, Constructing_Rubric_based_Tree, display_table
from tree_drawing import tree_drawing
from excel_to_rubric import excel_to_rubric


# Input Data
excel_file_path = '.\\input_data\\ReflectiveJournalRubric_light.xlsx'
Rubric_ID = '.1'

complexity_threshold = 0.3
list_of_concepts = "list_of_concepts"

rubric_table = excel_to_rubric (excel_file_path)

print (rubric_table)


RKT = RKTNode(id='.1')



RKT = Constructing_Rubric_based_Tree(Rubric_ID, rubric_table, list_of_concepts, complexity_threshold)

#RKT.display()

save_RKT_to_json(RKT, './/output//v3_short_RKT.json')

display_table(RKT)
#tree_drawing(RKT, '.\output\output_tree.jpeg')


