import re

# Canonical names for Pakistani Universities + Other
class Universities:
    LUMS = "LUMS (Lahore University of Management Sciences)"
    FAST = "FAST (National University of Computer and Emerging Sciences)"
    NUST = "NUST (National University of Sciences and Technology)"
    PUCIT = "PUCIT (Punjab University College of Information Technology)"
    UET = "UET (University of Engineering and Technology)"
    COMSATS = "COMSATS University Islamabad"
    GCU = "GCU (Government College University)"
    ITU = "ITU (Information Technology University)"
    GIKI = "GIKI (Ghulam Ishaq Khan Institute)"
    BAHRIA = "Bahria University"
    IBA = "IBA (Institute of Business Administration)"
    OTHER = "Other"

# Mapping regex patterns to Canonical Names
# We use regex to handle whitespace, case insensitivity, and common abbreviations
UNIVERSITY_MAPPING = [
    (r"\b(lums|lahore\s+university\s+of\s+management\s+sciences)\b", Universities.LUMS),
    (r"\b(fast|nuces|national\s+university\s+of\s+computer\s+and\s+emerging\s+sciences|fast-nuces|fast\s+nuces)\b", Universities.FAST),
    (r"\b(nust|national\s+university\s+of\s+sciences\s+and\s+technology)\b", Universities.NUST),
    (r"\b(pucit|punjab\s+university\s+college\s+of\s+information\s+technology|pu|university\s+of\s+the\s+punjab|punjab\s+university)\b", Universities.PUCIT),
    (r"\b(uet|university\s+of\s+engineering\s+and\s+technology)\b", Universities.UET),
    (r"\b(comsats|comsat|ciit)\b", Universities.COMSATS),
    (r"\b(gcu|gc|government\s+college|government\s+college\s+university)\b", Universities.GCU),
    (r"\b(itu|information\s+technology\s+university)\b", Universities.ITU),
    (r"\b(giki|ghulam\s+ishaq\s+khan)\b", Universities.GIKI),
    (r"\b(bahria|buic|bahria\s+university)\b", Universities.BAHRIA),
    (r"\b(iba|institute\s+of\s+business\s+administration)\b", Universities.IBA),
]

def normalize_university(raw_name: str) -> str:
    """
    Takes a raw university string extracted by the LLM and maps it to a Canonical Name.
    Handles None, empty strings, and whitespace robustly.
    If no match is found, returns 'Other'.
    """
    if not raw_name or not isinstance(raw_name, str):
        return Universities.OTHER
    
    clean_name = raw_name.strip().lower()
    
    # Remove excessive whitespace or newlines
    clean_name = re.sub(r'\s+', ' ', clean_name)

    if not clean_name or len(clean_name) < 2:
        return Universities.OTHER
        
    for pattern, canonical_name in UNIVERSITY_MAPPING:
        if re.search(pattern, clean_name):
            return canonical_name
            
    return Universities.OTHER
