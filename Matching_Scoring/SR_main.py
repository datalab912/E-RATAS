from scoring_reasoning import scoring
from reason_stroy import reason_story
from converting_RKT_ACT import ACTNode, RKTNode, load_tree, write_rkt_to_json, display_table 

import json
import yaml
import time

rkt_json_path= 'input_data/ReflectiveJournalRubric_light.json'




act_json_path= 'input_ReflectiveJournal_light/s2-2022_Mahdi Kobeissi- Final Report (CyberCX)-pages.json'
matching_threshold = 0.3


output_json_path = 'output_ReflectiveJournal_light/score_s2-2022_Mahdi Kobeissi- Final Report (CyberCX)-pages.json'
rkt_tree = load_tree(rkt_json_path, RKTNode)
write_rkt_to_json(rkt_tree, output_json_path)   

start_time = time.time()

scoring(rkt_json_path,act_json_path,matching_threshold, output_json_path)

End_time = time.time()

print(End_time-start_time)


act_json_path= 'input_ReflectiveJournal_light/s2-2022_Final_report_YIQUN_LI_47007567-pages.json'
matching_threshold = 0.3

output_json_path = 'output_ReflectiveJournal_light/score_s2-2022_Final_report_YIQUN_LI_47007567-pages.json'
rkt_tree = load_tree(rkt_json_path, RKTNode)
write_rkt_to_json(rkt_tree, output_json_path)   

start_time = time.time()

scoring(rkt_json_path,act_json_path,matching_threshold, output_json_path)

End_time = time.time()

print(End_time-start_time)


act_json_path= 'input_ReflectiveJournal_light/s2-2022_Internship report-pages.json'
matching_threshold = 0.3

output_json_path = 'output_ReflectiveJournal_light/score_s2-2022_Internship report-pages.json'
rkt_tree = load_tree(rkt_json_path, RKTNode)
write_rkt_to_json(rkt_tree, output_json_path)   

start_time = time.time()

scoring(rkt_json_path,act_json_path,matching_threshold, output_json_path)

End_time = time.time()

print(End_time-start_time)