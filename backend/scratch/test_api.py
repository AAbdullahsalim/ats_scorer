import requests
import json
import os

# Create dummy files
with open("dummy_jd.txt", "w") as f:
    f.write("Looking for a Python developer with 2 years of experience.")
    
with open("dummy_cv.txt", "w") as f:
    f.write("Jane Doe\njane@example.com\nPython Developer\nEducation: BS Computer Science from COMSATS University Islamabad, 2018-2022.\nExperience: 3 years as Python Dev.")

try:
    with open("dummy_jd.txt", "rb") as jd, open("dummy_cv.txt", "rb") as cv:
        files = {
            "jd_file": ("dummy_jd.txt", jd, "text/plain"),
            "cv_files": ("dummy_cv.txt", cv, "text/plain")
        }
        data = {
            "target_yoe": 0
        }
        
        response = requests.post("http://localhost:8001/analyze", files=files, data=data)
        
        print("Status Code:", response.status_code)
        
        if response.status_code == 200:
            res_json = response.json()
            candidates = res_json.get("candidates", [])
            for i, c in enumerate(candidates):
                print(f"Candidate {i}:")
                print(f"  Name: {c.get('candidate_name')}")
                print(f"  Universities: {c.get('normalized_universities')}")
                print(f"  Education: {json.dumps(c.get('education', []), indent=2)}")
        else:
            print("Response:", response.text)
finally:
    os.remove("dummy_jd.txt")
    os.remove("dummy_cv.txt")
