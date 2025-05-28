from paragraph_extract import extract_text_from_pdf
import tqdm

with open(file_path, 'r') as file:
  lines = file.readlines()
  for result in find_top_scores(lines, all_score, top_n=5):
    print(f"Rank {result['Rank']}: Score {result['Score']} - Paragraph:\n{result['Paragraph']}\n{'=' * 50}")