import fitz
import pypdf
import pdfplumber 
from pathlib import Path


#move Test_PDF from archive to the root folder

pdf_path = Path("Test_PDF/NaturePaper.pdf")

def extract_with_pymupdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n\n---PAGE BREAK---\n\n"
    return text

def extract_with_pdfplumber(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n\n---PAGE BREAK---\n\n"
    return text

def extract_with_pypdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = pypdf.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n\n---PAGE BREAK---\n\n"
    return text

if __name__ == "__main__":
    print("Testing PyMuPDF...")
    text1 = extract_with_pymupdf(pdf_path)
    print(f"Length of text1: {len(text1)}")
    print(text1[:500])
    with open("output_pymupdf.txt", "w", encoding="utf-8") as f:
        f.write(text1)

    print("Testing PDFPlumber...")
    text2 = extract_with_pdfplumber(pdf_path)
    print(f"Length of text2: {len(text2)}")
    print(text2[:500])
    with open("output_pdfplumber.txt", "w", encoding="utf-8") as f:
        f.write(text2)

    print("Testing PyPDF...")
    text3 = extract_with_pypdf(pdf_path)
    print(f"Length of text3: {len(text3)}")
    print(text3[:500])
    with open("output_pypdf.txt", "w", encoding="utf-8") as f:
        f.write(text3)
    print("All tests completed successfully")
    print("Output files saved to output_pymupdf.txt, output_pdfplumber.txt, and output_pypdf.txt")


        
