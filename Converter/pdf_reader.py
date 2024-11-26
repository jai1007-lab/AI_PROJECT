from PyPDF2 import PdfReader


class PDFReader:

    def __init__(self, pdf_file):
        self.pdf_file = pdf_file


    def read_pdf_content(self, pdf_file):
        """
        Reads the content of a PDF file and returns the extracted text.
        
        :param file_path: Path to the PDF file.
        :return: Extracted text as a single string.
        """
        try:
            reader = PdfReader(pdf_file)
            pdf_text = ""

            # Iterate through all the pages
            for page in reader.pages:
                pdf_text += page.extract_text()
            
            return " ".join(pdf_text.split())
        except Exception as e:
            print(f"Error reading PDF file: {e}")
            return None
"""
# Example usage
file_path = "example.pdf"  # Replace with your PDF file path
content = read_pdf_content(file_path)
if content:
    print("Extracted Text:")
    print(content)
else:
    print("Failed to extract text from the PDF.")
"""