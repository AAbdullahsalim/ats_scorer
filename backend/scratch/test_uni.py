import sys
import os

# Add the backend src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from utils.university_normalizer import normalize_university, Universities

def test_normalizer():
    tests = [
        ("LUMS", Universities.LUMS),
        ("Lahore University of Management Sciences", Universities.LUMS),
        ("fast-nuces", Universities.FAST),
        ("National University of Computer and Emerging Sciences", Universities.FAST),
        ("GC University", Universities.GCU),
        ("Punjab University", Universities.PUCIT),
        ("PUCIT", Universities.PUCIT),
        ("UET Lahore", Universities.UET),
        ("NUST Islamabad", Universities.NUST),
        ("Information Technology University", Universities.ITU),
        ("Unknown University", Universities.OTHER),
        ("", Universities.OTHER),
        (None, Universities.OTHER),
        ("   ", Universities.OTHER),
    ]

    print("Running University Normalizer Tests...\n")
    for raw, expected in tests:
        result = normalize_university(raw)
        status = "PASS" if result == expected else "FAIL"
        print(f"{status} | Raw: '{raw}' -> Expected: '{expected}', Got: '{result}'")

if __name__ == "__main__":
    test_normalizer()
