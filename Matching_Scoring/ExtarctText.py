import os
import json
import csv
import re

def extract_weeks_from_json(json_path):
    """
    Reads a single ACT JSON file and extracts each (week_num, week_text).
    Returns a list of tuples: (week_num, week_text).
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []

    # We assume the top-level node has a "children" list:
    #   [ { nodeType="title", text="week X" }, { nodeType="paragraph", text="..." }, ... ]
    # We'll look for 'title' nodes containing "week X", then take the next paragraph as the week text.
    children = data.get("children", [])
    i = 0
    while i < len(children):
        node = children[i]
        node_type = node.get("nodeType", "").lower()
        if node_type == "title":
            # Check if title node text is "week X"
            title_text = node.get("text", "")
            match = re.search(r"week\s+(\d+)", title_text, re.IGNORECASE)
            if match:
                week_num = match.group(1)
                # Next sibling is presumably the paragraph for this week:
                week_content = ""
                if i + 1 < len(children):
                    paragraph_node = children[i+1]
                    if paragraph_node.get("nodeType", "").lower() == "paragraph":
                        week_content = paragraph_node.get("text", "")
                results.append((week_num, week_content))
        i += 1

    return results

def save_weeks_to_csv(json_folder, output_csv_path):
    """
    - Reads all .json files in 'json_folder'.
    - For each file, extracts all (week_num, text) pairs.
    - Saves them in one CSV file at 'output_csv_path' with columns:
        [json_file, week_section_number, text].
    """
    rows = []
    for filename in os.listdir(json_folder):
        if filename.lower().endswith(".json"):
            json_file_path = os.path.join(json_folder, filename)
            week_data = extract_weeks_from_json(json_file_path)
            for (week_num, week_text) in week_data:
                rows.append([filename, week_num, week_text])

    # Write all results to a single CSV
    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["json_file", "week_section_number", "text"])
        writer.writerows(rows)

    print(f"CSV file created at: {os.path.abspath(output_csv_path)}")

if __name__ == "__main__":
    # Folder containing your ACT JSON files
    json_folder = "input_ReflectiveJournal_light"
    # Output CSV file path (can be in the same or another folder)
    output_csv_file = "weeks_extracted.csv"

    save_weeks_to_csv(json_folder, output_csv_file)
