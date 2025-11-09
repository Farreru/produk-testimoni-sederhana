import re

def detect_xss(input_string):
    """
    Detects potential XSS vulnerabilities in the input string.
    Returns True if potential XSS is detected, False otherwise.
    
    This is a basic regex-based detector for common XSS patterns.
    It does not sanitize or escape the input; it only checks for suspicious patterns.
    Note: This is not foolproof; advanced obfuscated attacks may evade it.
    """
    # Common XSS patterns to detect
    xss_patterns = [
        r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>',  # <script> tags
        r'on\w+\s*=',  # Event handlers like onload=, onclick=, etc.
        r'javascript\s*:',  # javascript: protocol
        r'vbscript\s*:',  # vbscript: protocol
        r'data\s*:',  # data: protocol (can be used for XSS)
        r'<img\s+[^>]*src\s*=\s*["\']?[^"\']*javascript:',  # img src with javascript
        r'<iframe\s+[^>]*src\s*=\s*["\']?[^"\']*javascript:',  # iframe src with javascript
        r'expression\s*\(',  # CSS expression()
        r'<svg\s+[^>]*onload\s*=',  # SVG onload
        r'alert\s*\(',  # Common test payload like alert(
    ]
    
    for pattern in xss_patterns:
        if re.search(pattern, input_string, re.IGNORECASE):
            return True
    return False