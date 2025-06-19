"""
converter.py

Converts resume files (PDF/DOCX) to plain text for parsing.
Enhanced with positional data extraction for better section detection.
"""
import os
from typing import Optional, Dict, List, Any

try:
    import pdfplumber # type: ignore
except ImportError:
    pdfplumber = None #Handles  import gracefully if pdfplumber is not installed. Prevents crash on import error.
try:
    import docx
except ImportError:
    docx = None

def convert_to_text(file_path: str) -> Optional[str]:
    """
    Detects file type and extracts text from PDF or DOCX.
    Returns extracted text as a string, or None if unsupported.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extract_pdf_text(file_path)
    elif ext == '.docx':
        return extract_docx_text(file_path)
    else:
        return None

def extract_pdf_with_layout(file_path: str) -> Dict[str, Any]:
    """
    Extract text with positional and formatting data from PDF.
    Returns structured data including text content, font sizes, positions, etc.
    
    Returns:
        Dict containing:
        - 'text': Plain text content
        - 'lines': List of line objects with position/formatting data
        - 'sections': Detected sections based on visual layout
    """
    if not pdfplumber:
        raise ImportError("pdfplumber is not installed.")
    
    result = {
        'text': '',
        'lines': [],
        'sections': []
    }
    
    all_lines = []
    
    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            # Extract text
            page_text = page.extract_text() or ""
            result['text'] += page_text
            
            # Extract words with positioning
            words = page.extract_words()
            
            # Group words into lines based on y-coordinates
            lines = _group_words_into_lines(words)
            
            # Add page context to lines
            for line in lines:
                line['page'] = page_num
                line['is_potential_header'] = _analyze_header_potential(line, lines)
                all_lines.append(line)
    
    result['lines'] = all_lines
    result['sections'] = _detect_sections_from_layout(all_lines)
    
    return result

def _group_words_into_lines(words: List[Dict]) -> List[Dict]:
    """Group words into lines based on y-coordinates."""
    if not words:
        return []
    
    # Sort words by y-coordinate (top to bottom), then x-coordinate (left to right)
    words.sort(key=lambda w: (round(w['top']), w['x0']))
    
    lines = []
    current_line = None
    current_y = None
    
    for word in words:
        word_y = round(word['top'])
        
        # If this is a new line (different y-coordinate)
        if current_y is None or abs(word_y - current_y) > 2:  # 2pt tolerance
            # Finalize previous line
            if current_line:
                lines.append(_finalize_line(current_line))
            
            # Start new line
            current_line = {
                'words': [word],
                'y': word_y,
                'x0': word['x0'],
                'x1': word['x1']
            }
            current_y = word_y
        else:
            # Add to current line
            current_line['words'].append(word)
            current_line['x0'] = min(current_line['x0'], word['x0'])
            current_line['x1'] = max(current_line['x1'], word['x1'])
    
    # Don't forget the last line
    if current_line:
        lines.append(_finalize_line(current_line))
    
    return lines

def _finalize_line(line_data: Dict) -> Dict:
    """Finalize a line by computing derived properties."""
    words = line_data['words']
    
    # Combine text
    text = ' '.join(word['text'] for word in words)
    
    # Calculate average font size (handle missing size data)
    font_sizes = [word.get('size', 12) for word in words if word.get('size')]
    avg_font_size = sum(font_sizes) / len(font_sizes) if font_sizes else 12
    
    # Determine if text is bold (heuristic)
    bold_words = sum(1 for word in words if 'bold' in word.get('fontname', '').lower())
    is_bold = bold_words > len(words) / 2
    
    # Check for all caps (common in headers)
    is_all_caps = text.isupper() and len(text.strip()) > 1
    
    return {
        'text': text.strip(),
        'y': line_data['y'],
        'x0': line_data['x0'],
        'x1': line_data['x1'],
        'font_size': avg_font_size,
        'is_bold': is_bold,
        'is_all_caps': is_all_caps,
        'word_count': len(words),
        'char_count': len(text)
    }

def _analyze_header_potential(line: Dict, all_lines: List[Dict]) -> bool:
    """Analyze if a line is likely to be a section header."""
    text = line['text'].strip()
    
    if not text or len(text) > 50:  # Headers are usually short
        return False
    
    # Calculate average font size in document (handle missing data)
    valid_font_sizes = [l['font_size'] for l in all_lines if l.get('font_size')]
    avg_font_size = sum(valid_font_sizes) / len(valid_font_sizes) if valid_font_sizes else 12
    
    header_indicators = []
    
    # Font size larger than average
    if line.get('font_size', 12) > avg_font_size * 1.2:
        header_indicators.append('large_font')
    
    # Bold text
    if line.get('is_bold', False):
        header_indicators.append('bold')
    
    # All caps
    if line.get('is_all_caps', False):
        header_indicators.append('all_caps')
    
    # Short text (typical of headers)
    if line.get('word_count', 0) <= 3:
        header_indicators.append('short')
    
    # Left-aligned (x0 close to left margin)
    if line.get('x0', 0) < 100:  # Assuming typical left margin
        header_indicators.append('left_aligned')
    
    # Contains typical section keywords
    text_lower = text.lower()
    section_keywords = ['education', 'experience', 'skills', 'projects', 'certifications', 'references']
    if any(keyword in text_lower for keyword in section_keywords):
        header_indicators.append('section_keyword')
    
    # Require at least 2 indicators for header classification
    return len(header_indicators) >= 2

def _detect_sections_from_layout(lines: List[Dict]) -> List[Dict]:
    """Detect sections based on visual layout analysis."""
    sections = []
    current_section = None
    
    for i, line in enumerate(lines):
        if line.get('is_potential_header'):
            # Finalize previous section
            if current_section:
                sections.append(current_section)
            
            # Start new section
            current_section = {
                'title': line['text'],
                'start_line': i,
                'lines': [line],
                'content': line['text']
            }
        elif current_section:
            # Add to current section
            current_section['lines'].append(line)
            current_section['content'] += '\n' + line['text']
    
    # Don't forget the last section
    if current_section:
        sections.append(current_section)
    
    return sections

def extract_pdf_text(file_path: str) -> str:
    """
    Extracts text from a PDF file using pdfplumber.
    """
    if not pdfplumber:
        raise ImportError("pdfplumber is not installed.") # Handles error if the function is used without the library available.
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

def extract_docx_text(file_path: str) -> str:
    """
    Extracts text from a DOCX file using python-docx.
    """
    if not docx:
        raise ImportError("python-docx is not installed.")
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])
