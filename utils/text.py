# Character width measurements based on the Frame's font
# Using '12345678901234567890' as reference (20 chars wide)
CHAR_WIDTHS = {
    ' ': 1,
    'i': 1,
    'l': 1,
    'I': 1,
    '1': 1,
    '!': 1,
    '.': 1,
    ',': 1,
    "'": 1,
    '"': 1,
    ';': 1,
    ':': 1,
    '|': 1,
    '`': 1,
    ' ': 1,
    'm': 2,
    'w': 2,
    'M': 2,
    'W': 2,
    '@': 2,
    '#': 2,
    '$': 2,
    '%': 2,
    '&': 2,
    '0': 1,
    '1': 1,
    '2': 1,
    '3': 1,
    '4': 1,
    '5': 1,
    '6': 1,
    '7': 1,
    '8': 1,
    '9': 1,
    'a': 1,
    'b': 1,
    'c': 1,
    'd': 1,
    'e': 1,
    'f': 1,
    'g': 1,
    'h': 1,
    'i': 1,
    'j': 1,
    'k': 1,
    'l': 1,
    'm': 2,
    'n': 1,
    'o': 1,
    'p': 1,
    'q': 1,
    'r': 1,
    's': 1,
    't': 1,
    'u': 1,
    'v': 1,
    'w': 2,
    'x': 1,
    'y': 1,
    'z': 1,
    'A': 1,
    'B': 1,
    'C': 1,
    'D': 1,
    'E': 1,
    'F': 1,
    'G': 1,
    'H': 1,
    'I': 1,
    'J': 1,
    'K': 1,
    'L': 1,
    'M': 2,
    'N': 1,
    'O': 1,
    'P': 1,
    'Q': 1,
    'R': 1,
    'S': 1,
    'T': 1,
    'U': 1,
    'V': 1,
    'W': 2,
    'X': 1,
    'Y': 1,
    'Z': 1,
}

def get_text_width(text: str) -> int:
    """
    Calculate the width of a text string based on character widths.
    
    Args:
        text: The text to measure
    
    Returns:
        Total width of the text in units
    """
    return sum(CHAR_WIDTHS.get(c, 1) for c in text)  # Default to 1 for unknown characters

def format_text_for_frame(text: str, max_line_length: int = 20, max_lines: int = 6, ellipsis: bool = True) -> list[str]:
    """
    Format text to fit the Frame's display constraints and return as blocks of text.
    
    Args:
        text: The input text to format
        max_line_length: Maximum width in units (default: 20 based on '12345678901234567890')
        max_lines: Number of lines per block (default: 6)
        ellipsis: Whether to add ellipsis to truncated blocks (default: True)
    
    Returns:
        List of text blocks, each block containing max_lines lines joined by newlines
    """
    # First, split the input text into words
    words = text.split()
    all_lines = []
    current_line = []
    current_width = 0
    
    for word in words:
        word_width = get_text_width(word)
        
        # If the word itself is longer than max_line_length, we need to break it up
        if word_width > max_line_length:
            # If we have a current line, add it first
            if current_line:
                all_lines.append(' '.join(current_line))
                current_line = []
                current_width = 0
            
            # Break up the long word into chunks that fit
            remaining = word
            while remaining:
                chunk = ''
                chunk_width = 0
                for char in remaining:
                    char_width = get_text_width(char)
                    if chunk_width + char_width <= max_line_length:
                        chunk += char
                        chunk_width += char_width
                    else:
                        break
                
                all_lines.append(chunk)
                remaining = remaining[len(chunk):]
            
            continue
        
        # Normal word processing
        if current_width + word_width + (1 if current_line else 0) > max_line_length:
            # Add the current line to lines and start a new one
            if current_line:
                all_lines.append(' '.join(current_line))
                current_line = []
                current_width = 0
        
        # Add the word to the current line
        current_line.append(word)
        current_width += word_width + (1 if len(current_line) > 1 else 0)
    
    # Add the last line if there is one
    if current_line:
        all_lines.append(' '.join(current_line))
    
    # Split lines into blocks of max_lines
    blocks = []
    for i in range(0, len(all_lines), max_lines):
        block = all_lines[i:i + max_lines]
        # Add ellipsis to the last line if we're truncating and ellipsis is enabled
        if ellipsis and len(all_lines) > i + max_lines:
            block[-1] = block[-1] + '...'
        blocks.append('\n'.join(block))
    
    return blocks 