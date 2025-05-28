import PyPDF2
import re
import glob
from tqdm import tqdm

def extract_text_from_pdf(pdf_path):
    reader = PyPDF2.PdfReader(pdf_path)
    number_of_pages = len(reader.pages)
    all_text = ''
    # Update the total number of pages in the main tqdm loop
    for i in tqdm(range(number_of_pages), desc=f"Processing {pdf_path}"):
        page = reader.pages[i]
        all_text += page.extract_text()

    return all_text

def clean_paragraphs(paragraphs):
    cleaned_paragraphs = []
    for paragraph in paragraphs:
        # Remove special symbols using regex
        cleaned_paragraph = re.sub(r'[^\w\s]', '', paragraph)
        cleaned_paragraphs.append(cleaned_paragraph)

    return cleaned_paragraphs

# Function to process paragraphs and apply the rule
def process_paragraphs(paragraphs):
    processed_paragraphs = []
    for paragraph in paragraphs:
        lines = paragraph.split('\n')
        processed_lines = []
        for line in lines:
            # Check if the line is not empty
            if line.strip():
                # Apply the rule only to the first character of the first word
                line = line[0].upper() + line[1:]
                processed_lines.append(line)
        processed_paragraphs.append('\n'.join(processed_lines))
    return processed_paragraphs

# Initialize the main tqdm progress bar for the entire process
pdf_files = list(glob.iglob('raw_data/**/*.pdf', recursive=True))
with tqdm(total=len(pdf_files), desc="Processing PDF files") as main_pbar:
    for filename in pdf_files:
        all_text = extract_text_from_pdf(filename)
        
        # Process the extracted text (add your logic here)
        paragraphs = re.split(r'\s{2,}|\n', all_text)  # Updated regex pattern
        # New paragraph detection rule
        refined_paragraphs = []
        current_paragraph = ""
        for paragraph in paragraphs:
            if current_paragraph: 
                if len(paragraph) > 0 and paragraph[0].isupper():  # New rule check
                    refined_paragraphs.append(current_paragraph)
                    current_paragraph = paragraph
                else: 
                    current_paragraph += " " + paragraph
            else:
                current_paragraph = paragraph

        if current_paragraph:
            refined_paragraphs.append(current_paragraph)
        paragraphs = refined_paragraphs
        paragraphs = [paragraph for paragraph in paragraphs if len(paragraph.split()) >= 30]
        paragraphs = clean_paragraphs(paragraphs)
        paragraphs = [paragraph.replace('\n', '').strip() for paragraph in paragraphs]

        if(len(paragraphs) < 10):
            print(f"Warning: {filename} has less than 10 paragraphs")
        
        if ('This report details the duties I completed successfully whether they were easy or tough as well as the tasks I attempted to carry out but was unable to do during my internship with' in all_text):
            print(f"Warning: {filename} has a specific paragraph")
        
        # Update the main tqdm progress bar
        main_pbar.update(1)

        # Write to the output file (add your logic here)
        with open('paragraph_from_pdf.txt', 'a') as file:
            for paragraph in paragraphs:
                file.write(paragraph + '\n')


e