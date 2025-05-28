import fitz  # PyMuPDF
import re  # For regular expressions, if used


def clean_section_text(text):  # Moved from top-level function
    """Removes trailing numbers, extra whitespace, and trims the text."""
    # Remove trailing page numbers (modify the regex if needed)
    text = re.sub(r"\s+\d+$", "", text.strip())

    return text.strip()  # Remove leading and trailing whitespace


def extract_content_for_header(doc, headers, header_text):
    for i, (header, page_number) in enumerate(headers):
        if header == header_text:
            all_text = ""
            start_index = find_header_index_in_page(doc, page_number, header_text)

            # Find the end index (the position of the next header)
            if i < len(headers) - 1:
                next_header, next_page_number = headers[i + 1]

                for i in range(page_number, next_page_number + 1):
                    all_text += doc[i - 1].get_text("text")

                end_index = find_header_in_text(all_text, next_header)
            else:
                for i in range(page_number, len(doc) + 1):
                    all_text += doc[i - 1].get_text("text")
                end_index = None  # Handle the case of the last header

            return extract_section_content(
                all_text, page_number, start_index, end_index
            )

    return None  # If the header is not found


def find_header_in_text(page_text, header_text):
    """Finds the index of the header within the page text."""
    return page_text.find(header_text)


def find_header_index_in_page(doc, page_number, header_text):
    """Finds the precise index of the header within the page text."""
    page = doc[page_number - 1]
    page_text = page.get_text()
    return page_text.find(header_text)


def extract_section_content(all_text, page_number, start_index, end_index):
    """Extracts the section content from the specified page."""
    if end_index:
        section_text = all_text[start_index:end_index]
    else:
        section_text = all_text[start_index:]

    return clean_section_text(section_text)  # Apply cleaning


def is_title(paragraph):
    """Checks if a paragraph is likely a title."""
    MAX_TITLE_WORDS = 10  # Adjust this limit as needed

    words = paragraph.split()
    return (
        len(paragraph.splitlines()) == 1
        and len(words) <= MAX_TITLE_WORDS
        and len(words) > 0
    )


def split_into_paragraphs(text):
    """Splits the text into a list of paragraphs."""
    paragraphs = text.split("\n \n")
    return [p.strip() for p in paragraphs if p.strip()]  # Remove empty paragraphs


def get_section_text(file_text, current_start, current_len, next_start=None):

    if current_start == -1:
        # Handle section not found
        return None

    # Find the next header (considering hierarchy)
    end_index = next_start if next_start else len(file_text)

    return file_text[current_start + current_len : end_index]
