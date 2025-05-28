import pandas as pd

sample_data = pd.read_excel("../../raw_data/Rubric_Style.xlsx", sheet_name="samples")
print(sample_data.head())
