import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.llm.extractor import parse_cv_extraction

def test():
    raw_llm_json = {
        "education": [
            {"degree": "BS", "institution": "COMSATS University Islamabad", "year": "2020"},
            {"degree": "MS", "institution": "FAST", "year": "2022"}
        ]
    }
    
    parsed = parse_cv_extraction(raw_llm_json)
    print("Parsed Universities:")
    for ed in parsed.education:
        print(f"  Institution: {ed.institution} -> Normalized: {ed.normalized_institution}")

if __name__ == "__main__":
    test()
