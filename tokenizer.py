"""
Syntax Highlighting Editor - Tokenizer Component
"""
import re

class BaseTokenizer:
    """Base class for language tokenizers"""
    def tokenize(self, text):
        """
        Tokenize the input text.
        Returns a list of (token_type, start_position, end_position) tuples.
        """
        raise NotImplementedError("Subclasses must implement tokenize method")
    
    def _create_token(self, token_type, match, line_offset=0, col_offset=0):
        """
        Create a token from a regex match.
        Returns a tuple of (token_type, start_position, end_position).
        """
        start_line, start_col = self._get_position(match.start(), line_offset, col_offset)
        end_line, end_col = self._get_position(match.end(), line_offset, col_offset)
        
        return (token_type, (start_line, start_col), (end_line, end_col))
    
    def _get_position(self, index, line_offset, col_offset):
        """
        Convert a flat index to a (line, column) position.
        This is a placeholder - subclasses should implement this based on their text processing.
        """
        return (1, index)  # Default implementation


class PythonTokenizer(BaseTokenizer):
    """Tokenizer for Python code"""
    def __init__(self):
        # Define regex patterns for Python tokens
        self.patterns = [
            # Strings (triple-quoted) - must come before keywords to avoid matching keywords inside strings
            (r'""".*?"""|\'\'\'.*?\'\'\'', 'string'),
            
            # Strings (single and double quoted) - must come before keywords
            (r'"[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\'', 'string'),
            
            # Comments - must come before keywords
            (r'#.*$', 'comment'),
            
            # Keywords
            (r'\b(and|as|assert|async|await|break|class|continue|def|del|elif|else|except|'
             r'finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|'
             r'return|try|while|with|yield)\b', 'keyword'),
            
            # Decorators
            (r'@\w+', 'decorator'),
            
            # Numbers
            (r'\b\d+\.\d+\b|\b\d+\b', 'number'),
            
            # Function definitions
            (r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)', 'function'),
            
            # Class definitions
            (r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)', 'class'),
            
            # Function calls
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', 'function'),
            
            # Operators
            (r'[\+\-\*\/\%\=\<\>\!\&\|\^\~\:\,\.\;]', 'operator')
        ]
    
    def tokenize(self, text):
        """Tokenize the input text.
        Returns a list of (token_type, start_position, end_position) tuples.
        """
        tokens = []
        lines = text.split('\n')
        
        # Track state for multi-line constructs
        in_string = False
        in_comment = False
        string_start = (0, 0)
        comment_start = (0, 0)
        
        for line_num, line in enumerate(lines, 1):
            line_pos = 0
            while line_pos < len(line):
                # If we're not in a special state, look for tokens
                if not in_string and not in_comment:
                    match = None
                    for pattern, token_type in self.patterns:
                        regex = re.compile(pattern)
                        match = regex.search(line, line_pos)
                        if match and match.start() == line_pos:
                            # Found a token
                            start_pos = (line_num, match.start())
                            end_pos = (line_num, match.end())
                            tokens.append((token_type, start_pos, end_pos))
                            line_pos = match.end()
                            break
                    
                    # If no token found, move to the next character
                    if not match or match.start() != line_pos:
                        line_pos += 1
                else:
                    # We're in a string or comment, just move to the next character
                    line_pos += 1
        
        return tokens


class JavaScriptTokenizer(BaseTokenizer):
    """Tokenizer for JavaScript code"""
    def __init__(self):
        # Define regex patterns for JavaScript tokens
        self.patterns = [
            # Comments (multi-line) - must come first
            (r'\/\*[\s\S]*?\*\/', 'comment'),
            
            # Comments (single-line) - must come before strings
            (r'\/\/.*$', 'comment'),
            
            # Template string start/end backticks
            (r'`', 'string'),
            
            # Template string interpolation start
            (r'\${', 'operator'),
            
            # Template string interpolation end
            (r'}', 'operator'),
            
            # Strings (single and double quoted) - must come before keywords
            (r'"[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\'', 'string'),
            
            # Keywords
            (r'\b(break|case|catch|class|const|continue|debugger|default|delete|do|else|'
             r'export|extends|finally|for|function|if|import|in|instanceof|new|return|super|'
             r'switch|this|throw|try|typeof|var|void|while|with|yield|let|static|enum|await|'
             r'implements|package|protected|interface|private|public)\b', 'keyword'),
            
            # Numbers
            (r'\b\d+\.\d+\b|\b\d+\b', 'number'),
            
            # Function definitions
            (r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)', 'function'),
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*function', 'function'),
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*=>', 'function'),
            
            # Class definitions
            (r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)', 'class'),
            
            # Function calls
            (r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', 'function'),
            
            # Operators
            (r'[\+\-\*\/\%\=\<\>\!\&\|\^\~\:\,\.\;]', 'operator')
        ]
    
    def tokenize(self, text):
        """Tokenize JavaScript code with special handling for template strings"""
        tokens = []
        lines = text.split('\n')
        
        # Track state for multi-line constructs
        in_template_string = False
        in_interpolation = False
        in_comment = False
        template_string_start = (0, 0)
        
        for line_num, line in enumerate(lines, 1):
            line_pos = 0
            while line_pos < len(line):
                # Handle template strings specially
                if in_template_string and not in_interpolation:
                    # Look for either the end of the template string or the start of interpolation
                    backtick_pos = line.find('`', line_pos)
                    interp_pos = line.find('${', line_pos)
                    
                    if backtick_pos != -1 and (interp_pos == -1 or backtick_pos < interp_pos):
                        # Found end of template string
                        if line_pos < backtick_pos:
                            # Add the string content
                            tokens.append(('string', (line_num, line_pos), (line_num, backtick_pos)))
                        
                        # Add the closing backtick
                        tokens.append(('string', (line_num, backtick_pos), (line_num, backtick_pos + 1)))
                        in_template_string = False
                        line_pos = backtick_pos + 1
                    elif interp_pos != -1:
                        # Found start of interpolation
                        if line_pos < interp_pos:
                            # Add the string content
                            tokens.append(('string', (line_num, line_pos), (line_num, interp_pos)))
                        
                        # Add the ${
                        tokens.append(('operator', (line_num, interp_pos), (line_num, interp_pos + 2)))
                        line_pos = interp_pos + 2
                        in_interpolation = True
                    else:
                        # No backtick or interpolation in this line, just add the rest as string
                        tokens.append(('string', (line_num, line_pos), (line_num, len(line))))
                        line_pos = len(line)
                
                # Handle interpolation content
                elif in_template_string and in_interpolation:
                    # Look for the end of interpolation
                    brace_pos = line.find('}', line_pos)
                    
                    if brace_pos != -1:
                        # Handle any content inside the interpolation normally
                        current_pos = line_pos
                        while current_pos < brace_pos:
                            match = None
                            for pattern, token_type in self.patterns:
                                if pattern in (r'`', r'\${', r'}'): 
                                    continue  # Skip template string special patterns
                                
                                regex = re.compile(pattern)
                                match = regex.search(line, current_pos, brace_pos)
                                if match and match.start() == current_pos:
                                    tokens.append((token_type, (line_num, match.start()), (line_num, match.end())))
                                    current_pos = match.end()
                                    break
                            
                            if not match or match.start() != current_pos:
                                current_pos += 1
                        
                        # Add the closing brace
                        tokens.append(('operator', (line_num, brace_pos), (line_num, brace_pos + 1)))
                        line_pos = brace_pos + 1
                        in_interpolation = False
                    else:
                        # No closing brace in this line
                        # Handle any content inside the interpolation normally
                        current_pos = line_pos
                        while current_pos < len(line):
                            match = None
                            for pattern, token_type in self.patterns:
                                if pattern in (r'`', r'\${', r'}'): 
                                    continue  # Skip template string special patterns
                                
                                regex = re.compile(pattern)
                                match = regex.search(line, current_pos)
                                if match and match.start() == current_pos:
                                    tokens.append((token_type, (line_num, match.start()), (line_num, match.end())))
                                    current_pos = match.end()
                                    break
                            
                            if not match or match.start() != current_pos:
                                current_pos += 1
                        
                        line_pos = len(line)
                
                # Normal processing
                else:
                    # Check for backtick to start template string
                    if line[line_pos:line_pos+1] == '`':
                        tokens.append(('string', (line_num, line_pos), (line_num, line_pos + 1)))
                        in_template_string = True
                        line_pos += 1
                    else:
                        # Normal token processing
                        match = None
                        for pattern, token_type in self.patterns:
                            regex = re.compile(pattern)
                            match = regex.search(line, line_pos)
                            if match and match.start() == line_pos:
                                tokens.append((token_type, (line_num, match.start()), (line_num, match.end())))
                                line_pos = match.end()
                                break
                        
                        if not match or match.start() != line_pos:
                            line_pos += 1
        
        return tokens


class HTMLTokenizer(BaseTokenizer):
    """Tokenizer for HTML code"""
    def __init__(self):
        # Define regex patterns for HTML tokens
        self.patterns = [
            # Comments - must come first
            (r'<!--[\s\S]*?-->', 'comment'),
            
            # Doctype
            (r'<!DOCTYPE[^>]*>', 'tag'),
            
            # Tags (opening)
            (r'<([a-zA-Z][a-zA-Z0-9_:-]*)', 'tag'),
            
            # Tags (closing)
            (r'</([a-zA-Z][a-zA-Z0-9_:-]*)', 'tag'),
            
            # Tag end
            (r'>', 'tag'),
            
            # Self-closing tag end
            (r'/>', 'tag'),
            
            # Attributes - must come before strings
            (r'\s([a-zA-Z][a-zA-Z0-9_:-]*)\s*=', 'attribute'),
            
            # Strings (attribute values)
            (r'"[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\'', 'string')
        ]
        
    def tokenize(self, text):
        """Tokenize HTML code with special handling for text content and comments"""
        tokens = []
        lines = text.split('\n')
        
        # Track HTML parsing state
        in_tag = False
        
        for line_num, line in enumerate(lines, 1):
            line_pos = 0
            while line_pos < len(line):
                # Check for comment start
                if line_pos < len(line) - 3 and line[line_pos:line_pos+4] == '<!--':
                    comment_end = line.find('-->', line_pos)
                    if comment_end != -1:
                        # Add the entire comment as a single token
                        tokens.append(('comment', (line_num, line_pos), (line_num, comment_end + 3)))
                        line_pos = comment_end + 3
                        continue
                    else:
                        # Comment extends to end of line
                        tokens.append(('comment', (line_num, line_pos), (line_num, len(line))))
                        line_pos = len(line)
                        continue
                
                # Check for tag start/end to track state
                if line_pos < len(line) - 1 and line[line_pos:line_pos+2] == '<!':
                    # Start of doctype
                    in_tag = True
                
                elif line_pos < len(line) and line[line_pos] == '<':
                    # Start of an opening or closing tag
                    in_tag = True
                
                elif line_pos < len(line) and line[line_pos] == '>':
                    # End of tag
                    tokens.append(('tag', (line_num, line_pos), (line_num, line_pos + 1)))
                    in_tag = False
                    line_pos += 1
                    continue
                
                # Inside a tag, apply normal token processing
                if in_tag:
                    match = None
                    for pattern, token_type in self.patterns:
                        if token_type == 'comment':
                            continue  # Skip comment pattern, already handled
                        regex = re.compile(pattern)
                        match = regex.search(line, line_pos)
                        if match and match.start() == line_pos:
                            tokens.append((token_type, (line_num, match.start()), (line_num, match.end())))
                            line_pos = match.end()
                            break
                    
                    if not match or match.start() != line_pos:
                        line_pos += 1
                else:
                    # Not in a tag - find the next tag start
                    next_tag = line.find('<', line_pos)
                    if next_tag != -1:
                        # Skip text content until next tag (don't tokenize it)
                        line_pos = next_tag
                    else:
                        # No more tags in this line
                        line_pos = len(line)
        
        return tokens

class CSSTokenizer(BaseTokenizer):
    """Tokenizer for CSS code"""
    def __init__(self):
        # Define regex patterns for CSS tokens
        self.patterns = [
            # Comments - must come first
            (r'\/\*[\s\S]*?\*\/', 'comment'),
            
            # Selectors
            (r'[a-zA-Z0-9_\-\.\#\[\]\:\,\>\+\~\*]+\s*\{', 'tag'),
            
            # Properties
            (r'([a-zA-Z\-]+)\s*:', 'property'),
            
            # Values
            (r':\s*([^;]+);', 'value'),
            
            # Colors
            (r'#[0-9a-fA-F]{3,6}', 'number'),
            
            # Units
            (r'\b\d+\.?\d*(%|px|em|rem|vh|vw|pt|pc|in|cm|mm|ex|ch|vmin|vmax)?\b', 'number'),
            
            # Important
            (r'!important', 'keyword'),
            
            # Media queries
            (r'@media\b', 'keyword'),
            
            # Other at-rules
            (r'@[a-zA-Z\-]+', 'keyword'),
            
            # Braces, semicolons, etc.
            (r'[\{\}\;\:\,]', 'operator')
        ]
    
    def tokenize(self, text):
        """Tokenize the input text.
        Returns a list of (token_type, start_position, end_position) tuples.
        """
        tokens = []
        lines = text.split('\n')
        
        # Track state for multi-line constructs
        in_string = False
        in_comment = False
        string_start = (0, 0)
        comment_start = (0, 0)
        
        for line_num, line in enumerate(lines, 1):
            line_pos = 0
            while line_pos < len(line):
                # If we're not in a special state, look for tokens
                if not in_string and not in_comment:
                    match = None
                    for pattern, token_type in self.patterns:
                        regex = re.compile(pattern)
                        match = regex.search(line, line_pos)
                        if match and match.start() == line_pos:
                            # Found a token
                            start_pos = (line_num, match.start())
                            end_pos = (line_num, match.end())
                            tokens.append((token_type, start_pos, end_pos))
                            line_pos = match.end()
                            break
                    
                    # If no token found, move to the next character
                    if not match or match.start() != line_pos:
                        line_pos += 1
                else:
                    # We're in a string or comment, just move to the next character
                    line_pos += 1
        
        return tokens