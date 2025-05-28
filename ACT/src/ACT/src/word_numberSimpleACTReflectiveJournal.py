import os
import json
import csv
import re

def count_words_in_string(text):
    """
    Returns the number of words in the given text.
    Splits on whitespace. Adjust as needed for more precise counting.
    """
    if not text or not text.strip():
        return 0
    return len(text.split())

def process_json_file(json_path):
    """
    Reads a JSON file (produced by the ACT tree extraction),
    finds each 'week X' Title node and the subsequent Paragraph node.
    Returns a list of (week_number, word_count) tuples.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []
    if "children" not in data or not isinstance(data["children"], list):
        return results  # No children -> no week data

    # We'll do a simple pass through top-level children
    # Title nodes and their subsequent Paragraph nodes typically come in pairs.
    children = data["children"]

    i = 0
    while i < len(children):
        node = children[i]
        if node.get("nodeType") and node["nodeType"].lower() == "title":
            # Check if this title text is "week <number>"
            title_text = node.get("text", "")
            match = re.search(r"week\s+(\d+)", title_text, re.IGNORECASE)
            if match:
                week_num = match.group(1)  # e.g., "6"

                # The next sibling *should* be the paragraph for this week
                paragraph_text = ""
                if i + 1 < len(children):
                    next_node = children[i + 1]
                    if next_node.get("nodeType") and next_node["nodeType"].lower() == "paragraph":
                        paragraph_text = next_node.get("text", "")

                # Count words in the paragraph text
                word_count = count_words_in_string(paragraph_text)

                # Store the result
                results.append((week_num, word_count))

        i += 1

    return results

def process_jsons_in_folder(input_folder, output_csv):
    """
    Reads all .json files in the specified folder, extracts (week_num, word_count) info,
    and writes them to a CSV file with columns:
      [json_file, week_section_number, word_count].
    """
    rows = []
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".json"):
            json_path = os.path.join(input_folder, filename)

            # Process the JSON file to get week info
            week_info = process_json_file(json_path)
            # Each item in week_info is (week_num, word_count)

            # For each week section in this file, add a row
            for (week_num, word_count) in week_info:
                rows.append([filename, week_num, word_count])

    # Write results to CSV
    with open(output_csv, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        # Write header
        writer.writerow(["json_file", "week_section_number", "word_count"])
        # Write data rows
        for row in rows:
            writer.writerow(row)

    print(f"CSV file has been created at: {os.path.abspath(output_csv)}")

if __name__ == "__main__":
    # Folder containing all the JSON files (produced by the ACT extraction)
    folder_path = "src/ACT/src/output"
    # Path to save the CSV file
    output_csv_path = "src/ACT/src/output/week_word_counts.csv"

    process_jsons_in_folder(folder_path, output_csv_path)
