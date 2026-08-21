"""Quick API test against the live backend."""
import requests
import json
import time
import urllib.request

# Wait for server to be ready
for i in range(8):
    try:
        r = urllib.request.urlopen('http://localhost:8001/health', timeout=2)
        print('Server ready:', r.status)
        break
    except Exception as e:
        print(f'Attempt {i+1}: waiting... ({e})')
        time.sleep(2)
else:
    print("Server not available!")
    exit(1)

cv_paths = [
    'sample_cvs/Jose Morales Patching _ Senior Software Engineer, Java NinjaOne.pdf',
    'sample_cvs/Abby Syeid (1).pdf',
    'sample_cvs/Abdullah-Salim-resume (2).pdf',
]
jd_path = 'jds/SE JD.pdf'

files_to_send = []
open_files = []
fh = open(jd_path, 'rb')
open_files.append(fh)
files_to_send.append(('jd_file', ('SE JD.pdf', fh, 'application/pdf')))

for p in cv_paths:
    fh = open(p, 'rb')
    open_files.append(fh)
    files_to_send.append(('cv_files', (p.split('/')[-1], fh, 'application/pdf')))

print(f"\nSending {len(cv_paths)} CVs + 1 JD...")
try:
    resp = requests.post(
        'http://localhost:8001/analyze',
        files=files_to_send,
        data={'target_yoe': 3.0},
        timeout=180
    )
    print(f'Status: {resp.status_code}')
    if resp.status_code == 200:
        data = resp.json()
        print(f"\nLLM mode: {data['llm_mode']}")
        print(f"Processing time: {data['processing_time_seconds']}s\n")
        print("Candidates:")
        print("-" * 80)
        for c in data['candidates']:
            name = c['candidate_name']
            score = c['final_score_pct']
            yoe = c['candidate_yoe']
            llm = c['llm_enhanced']
            matched = len(c['matched_skills'])
            missing = len(c['missing_skills'])
            print(f"  {name:<40} | Score: {score:5.1f}% | YOE: {yoe:4.1f} | LLM: {str(llm):<5} | Matched: {matched} | Missing: {missing}")
        print("-" * 80)
    else:
        print(f'Error: {resp.text[:1000]}')
finally:
    for fh in open_files:
        fh.close()
