import pandas as pd
from scoring_reasoning import Azure_direct_scoring
def scoring_function(text: str) -> float:
    """
    Example scoring function that returns a numeric score for the given text.
    Replace this logic with whatever scoring method you need (e.g., machine learning model, NLP processing, etc.).
    """
    # For demonstration: let's pretend the 'score' is simply the count of words in the text.
    if not text or not isinstance(text, str):
        return 0
    return float(len(text.split()))

def add_scores_to_csv(
    input_csv: str,
    output_csv: str,
    start_row: int,
    end_row: int,
    text_column: str = "text"
):
    """
    Reads 'input_csv', calculates a 'score' for rows in the range [start_row, end_row] using 'scoring_function',
    adds a new 'score' column for those rows, and writes the result to 'output_csv'.

    :param input_csv: Path to the input CSV file.
    :param output_csv: Path to the output CSV file (with new 'score' column).
    :param start_row: Index of the first row to be scored (0-based).
    :param end_row: Index of the last row to be scored (0-based, inclusive).
    :param text_column: Name of the column containing text to be scored.
    """
    # 1. Read the CSV into a Pandas DataFrame
    df = pd.read_csv(input_csv)

    # 2. Ensure the 'score' column exists (or create it)
    if "score" not in df.columns:
        df["score"] = None  # Initialize with None or NaN

    # 3. Iterate over the given row range and calculate scores
    #    We use .loc or .iloc. Here, we'll use .iloc for positional indexing.
    #    We'll also check boundaries to avoid out-of-range errors.
    max_index = len(df) - 1
    if start_row < 0:
        start_row = 0
    if end_row > max_index:
        end_row = max_index

    # 4. For each row in [start_row, end_row], compute the score from the text
    for row_index in range(start_row, end_row + 1):
        text_value = df.iloc[row_index][text_column]
        score_value = Azure_direct_scoring(text_value)
        df.at[row_index, "score"] = score_value

    # 5. Save the updated DataFrame to a new CSV
    df.to_csv(output_csv, index=False)
    print(f"Saved CSV with 'score' column to: {output_csv}")

if __name__ == "__main__":
    # Example usage:
    # Modify these paths and row indices as needed.
    input_csv_path = "weeks_extracted.csv"
    output_csv_path = "directGPTscore2.csv"

    # # Let's say we want to score rows from 10 through 20 (inclusive).
    # start_row_number = 0
    # end_row_number = 15
    df = pd.read_csv(input_csv_path)
    total_rows = len(df)

    # Process all rows (from first to last)
    start_row_number = 0
    end_row_number = total_rows - 1
    # The column that contains the text we want to score
    column_with_text = "text"

    # Call the function
    add_scores_to_csv(
        input_csv=input_csv_path,
        output_csv=output_csv_path,
        start_row=start_row_number,
        end_row=end_row_number,
        text_column=column_with_text
    )
