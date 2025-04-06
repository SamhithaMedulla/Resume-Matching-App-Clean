from pdfminer.high_level import extract_text

try:
    print("Starting text extraction...")
    text = extract_text('example.pdf')
    print(f"Extracted text: {text}")
    print(text)
except Exception as e:
    print(f"Error extracting text: {e}")
