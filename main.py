import os
from pathlib import Path
from src.parser import ResumeParser

def run_parser_test():
    parser = ResumeParser()
    cv_folder = Path("sample_cvs")
    
    cv_files = list(cv_folder.glob("*.pdf")) + list(cv_folder.glob("*.docx"))
    
    if not cv_files:
        print("No CV files found in 'sample_cvs/' folder.")
        print("Drop a PDF or DOCX file into 'sample_cvs/' and rerun python main.py")
        return

    for cv_path in cv_files:
        print(f"\n==========================================")
        print(f" Parsing File: {cv_path.name}")
        print(f"==========================================")
        
        try:
            result = parser.parse(str(cv_path))
            print("\n[EXTRACTED SKILLS SECTION]:")
            print(result['sections']['skills'] if result['sections']['skills'] else "No distinct skills section found.")
            
            print("\n[EXTRACTED EXPERIENCE PREVIEW]:")
            print(result['sections']['experience'][:250] if result['sections']['experience'] else "No distinct experience section found.")
        except Exception as e:
            print(f"Error parsing {cv_path.name}: {e}")

if __name__ == "__main__":
    run_parser_test()