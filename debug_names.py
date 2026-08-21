"""Debug script to examine raw PDF text extraction for name detection."""
import sys
sys.path.insert(0, 'backend')
from src.parser.pdf_extractor import extract_blocks_from_pdf
from src.parser.text_cleaner import extract_name_from_text, extract_name_from_blocks, clean_text

cv_paths = [
    'sample_cvs/Jose Morales Patching _ Senior Software Engineer, Java NinjaOne.pdf',
    'sample_cvs/Abby Syeid (1).pdf',
    'sample_cvs/Abdullah-Salim-resume (2).pdf',
]

for path in cv_paths:
    print(f"\n{'='*60}")
    print(f"CV: {path.split('/')[-1]}")
    print('='*60)
    blocks = extract_blocks_from_pdf(path)
    full_text = clean_text('\n'.join(b['text'] for b in blocks))
    
    name_from_blocks = extract_name_from_blocks(blocks)
    name_from_text = extract_name_from_text(full_text)
    
    print(f"  Name from blocks: '{name_from_blocks}'")
    print(f"  Name from text:   '{name_from_text}'")
    
    # Show top candidates by font size
    print(f"\n  Top font-size blocks in first 25:")
    top_blocks = sorted(
        [(b['font_size'], b['text'][:60].replace('\n', ' ').strip()) for b in blocks[:25] if b['font_size'] > 0],
        reverse=True
    )[:5]
    for size, text in top_blocks:
        print(f"    size={size:5.1f}: '{text}'")
