"""
Syntax Highlighting Editor - Syntax Highlighter Component
"""
import tkinter as tk
import re
from tokenizer import PythonTokenizer, JavaScriptTokenizer, HTMLTokenizer, CSSTokenizer

class SyntaxHighlighter:
    """Handles syntax highlighting for the text editor"""
    def __init__(self, text_widget):
        self.text = text_widget
        
        # Define tag configurations for different token types
        self._setup_tags()
        
        # Initialize tokenizers
        self.tokenizers = {
            "python": PythonTokenizer(),
            "javascript": JavaScriptTokenizer(),
            "html": HTMLTokenizer(),
            "css": CSSTokenizer()
        }
    
    def _setup_tags(self):
        """Set up text tags for syntax highlighting with a cheerful color scheme"""
        # Keywords - bright purple
        self.text.tag_configure("keyword", foreground="#9D00FF", font=("Courier New", 12, "bold"))
        
        # Strings - vibrant green
        self.text.tag_configure("string", foreground="#00CC66")
        
        # Comments - teal blue
        self.text.tag_configure("comment", foreground="#00A5A5", font=("Courier New", 12, "italic"))
        
        # Numbers - bright orange
        self.text.tag_configure("number", foreground="#FF6600")
        
        # Functions - royal blue
        self.text.tag_configure("function", foreground="#4169E1")
        
        # Classes - crimson
        self.text.tag_configure("class", foreground="#DC143C", font=("Courier New", 12, "bold"))
        
        # Operators - deep pink
        self.text.tag_configure("operator", foreground="#FF1493")
        
        # Decorators (Python)
        self.text.tag_configure("decorator", foreground="#FF8C00")
        
        # HTML/XML tags - bright blue
        self.text.tag_configure("tag", foreground="#1E90FF")
        
        # HTML/XML attributes - coral
        self.text.tag_configure("attribute", foreground="#FF7F50")
        
        # CSS properties - fuchsia
        self.text.tag_configure("property", foreground="#FF00FF")
        
        # CSS values - lime green
        self.text.tag_configure("value", foreground="#32CD32")
    
    def highlight_text(self, language):
        """Apply syntax highlighting to the text"""
        # Get the text content
        content = self.text.get("1.0", tk.END)
        
        # Remove all existing tags
        for tag in self.text.tag_names():
            if tag != "sel":  # Don't remove selection tag
                self.text.tag_remove(tag, "1.0", tk.END)
        
        # Get the tokenizer for the selected language
        tokenizer = self.tokenizers.get(language)
        if not tokenizer:
            return  # No tokenizer available for this language
        
        # Tokenize the content
        tokens = tokenizer.tokenize(content)
        
        # Apply highlighting based on token types
        for token_type, start, end in tokens:
            start_index = self._get_index_from_position(start)
            end_index = self._get_index_from_position(end)
            
            # Apply the appropriate tag
            if token_type in self.text.tag_names():
                # Make sure we're not overlapping with existing tags
                self.text.tag_add(token_type, start_index, end_index)
                
                # Special handling for function calls to highlight parentheses
                if token_type == "function":
                    # Find the opening parenthesis position
                    text_range = self.text.get(start_index, end_index)
                    paren_pos = text_range.rfind("(")
                    if paren_pos >= 0:
                        # Calculate the position of the opening parenthesis
                        paren_index = f"{start[0]}.{start[1] + paren_pos}"
                        # Apply operator tag to the parenthesis
                        self.text.tag_add("operator", paren_index, f"{start[0]}.{start[1] + paren_pos + 1}")
    
    def _get_index_from_position(self, position):
        """Convert a (line, column) position to a Tkinter text index"""
        line, col = position
        return f"{line}.{col}"
