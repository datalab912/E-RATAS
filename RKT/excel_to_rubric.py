
import pandas as pd

def excel_to_rubric (excel_file_path):
    
    # Read the Excel file
    df = pd.read_excel(excel_file_path, engine='openpyxl')

    # Convert the DataFrame to a list of lists. Each sublist represents a row in the Excel file.
    # The .values attribute gets the numpy representation of the DataFrame,
    # and .tolist() converts it into a Python list.
    table_data = df.fillna('Null').values.tolist()

    # Optionally, add the headers as the first list in table_data if needed
    headers = df.columns.tolist()
    table_data.insert(0, headers)

    rubric_table = []

    # Skip the header row with [1:] and iterate over each row
    for row in table_data[1:]:
        criterion_dict = {
            "ID": row[0],
            "Basic-Criteria": row[1],
            "Score-Source" : row [2],
            "Answer-Section": row[3],
            "Conditions": []
        }

        # Iterate over condition and score pairs
        for i in range(4, len(row), 2):  # Start from index 3 and step by 2 to get condition and its score
            condition = row[i]
            score = row[i + 1]
            if condition != "Null" and score != "Null":
                criterion_dict["Conditions"].append({"Condition": condition, "Score": score})

        rubric_table.append(criterion_dict)

    return rubric_table