from scoring_reasoning import scoring
from reason_stroy import reason_story
from converting_RKT_ACT import ACTNode, RKTNode, load_tree, write_rkt_to_json, display_table 

import json
import yaml
import time



output_json_path = 'output_ReflectiveJournal_light/score_s1-2022_43670121_FinalReport_COMP8852-pages_light.json'
output_txt_path = 'output_ReflectiveJournal_light/score_s1-2022_43670121_FinalReport_COMP8852-pages_light.txt'
reason_story(output_json_path, output_txt_path)