import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.docx_converter import convert_docx_to_pdf

def test():
    # Create a dummy docx (but wait, docx2pdf needs a valid docx file, not a txt file renamed to docx)
    # I should use an existing docx file or create a valid one using python-docx
    pass

if __name__ == "__main__":
    test()
