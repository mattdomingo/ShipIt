# Resume Parser

This module will handle resume file parsing and extraction of skills, education, and experience.

**Structure*
parser/
  ├── __init__.py
  ├── file_handler.py      # Handles file input/storage
  ├── converter.py         # Converts PDF/DOCX to text
  ├── extractor.py         # NLP/rule-based extraction logic
  ├── schema.py            # Defines output data structure
  └── tests/
        └── test_parser.py

Notes:
- pdfplumber vs PyPDF (converter.py)
    - pdfplumber
        - Extracts text with layout
        - Better handling of resumes (which can have a complex structure)
        - Pulls positional data which can help with organizing
        - Slightly slower
    - PyPDF
        - Simple PDFs welcome
        - Faster and lighter
        - Not the best for resumes
- Packages
    - Use conda for cross platform consistency