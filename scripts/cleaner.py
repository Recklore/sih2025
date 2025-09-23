import re

def clean_ocr_text(text):
    """
    A multi-stage pipeline to clean OCR'd text.
    """
    # Split the text by pages to process them individually
    pages = text.split('--------------------------------------------------------------------------------')
    
    cleaned_pages = []
    
    for page_content in pages:
        # Step 1: Basic Regex Cleanup
        # Remove page number markers
        content = re.sub(r'Page \d+:', '', page_content)
        # Remove non-ASCII characters (often OCR garbage)
        content = re.sub(r'[^\x00-\x7F]+', '', content)
        
        # Step 3 (done early): Reconstruct paragraphs by fixing line breaks
        # This is a bit tricky. Let's join lines that are likely part of the same paragraph.
        lines = content.strip().split('\n')
        # Filter out empty lines and join with a space
        meaningful_lines = [line.strip() for line in lines if line.strip()]
        reconstructed_text = ' '.join(meaningful_lines)
        
        # Remove excessive whitespace
        reconstructed_text = re.sub(r'\s+', ' ', reconstructed_text).strip()
        
        # Step 2: Content-Aware Filtering
        # Identify and remove common headers/footers (add your specific ones)
        common_headers = ["9th ANNUAL REPORT 2017-2018", "CENTRAL UNIVERSITY OF RAJASTHAN"]
        for header in common_headers:
            reconstructed_text = reconstructed_text.replace(header, "")
            
        # Discard "pages" with very little content
        if len(reconstructed_text.split()) < 10:
            continue
            
        cleaned_pages.append(reconstructed_text)
        
    return "\n\n".join(cleaned_pages)


# Your example text
raw_text = """
 abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789
"""

cleaned_text = clean_ocr_text(raw_text)
print(cleaned_text)