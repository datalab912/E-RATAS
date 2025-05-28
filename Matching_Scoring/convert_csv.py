import json
import csv
import sys

def sort_by_id_str(id_str):
    """
    Converts an ID string like '1.2.3' into a list of integers [1,2,3]
    so that sorting is done in proper numeric ascending order (1.9 < 1.10).
    """
    return [int(part) for part in id_str.split('.') if part.isdigit()]

def traverse_tree(node, rows):
    row = {}
    row['id'] = node.get('id', '')
    row['separate_criteria_number'] = node.get('separate_criteria_number', 0)

    # --- SCORE SOURCE ---
    score_source_value = node.get('score_source', [])
    # if it's not a list, wrap it in a list
    if not isinstance(score_source_value, list):
        score_source_value = [score_source_value]
    # now join
    row['score_source'] = '\n'.join(str(item) for item in score_source_value)

    # --- INFLUENCE TYPE / SCORING ---
    row['influence_type'] = node.get('influence_type', '')
    row['influence_on_scoring'] = node.get('influence_on_scoring', '')

    # --- SCORE BREAKDOWN ---
    score_breakdown_value = node.get('score_breakdown', [])
    if not isinstance(score_breakdown_value, list):
        score_breakdown_value = [score_breakdown_value]
    row['score_breakdown'] = '\n'.join(str(item) for item in score_breakdown_value)

    # --- SCORE ---
    row['score'] = node.get('score', '')

    rows.append(row)

    # Sort children by ID, then recurse
    children = node.get('children', [])
    children_sorted = sorted(children, key=lambda c: sort_by_id_str(c.get('id', '')))
    for child in children_sorted:
        traverse_tree(child, rows)



def json_to_csv(input_json_path, output_csv_path):
    """
    Loads the RKT tree from a JSON file, traverses it in pre-order, and writes
    only specific columns to a CSV file, preserving hierarchy order.
    """

    # 1) Load data
    with open(input_json_path, 'r', encoding='utf-8') as f:
        root = json.load(f)

    # 2) Traverse and collect rows
    rows = []
    traverse_tree(root, rows)

    # 3) Define the CSV header
    fieldnames = [
        'id',
        'separate_criteria_number',
        'score_source',
        'influence_type',
        'influence_on_scoring',
        'score_breakdown',
        'score'
    ]

    # 4) Write to CSV
    with open(output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

if __name__ == "__main__":
    """
    Example usage from a terminal or command prompt:
        python json_to_csv.py input.json output.csv
    """
    if len(sys.argv) >= 3:
        input_json = sys.argv[1]
        output_csv = sys.argv[2]
    else:
        # Fallback to default file names
        input_json = 'output_ReflectiveJournal_light/score_s1-2022_Final report_46139001-pages#.json'
        output_csv = 'output_ReflectiveJournal_light/score_s1-2022_Final report_46139001-pages#.csv'

    json_to_csv(input_json, output_csv)
    print(f"Successfully converted '{input_json}' to '{output_csv}'.")
