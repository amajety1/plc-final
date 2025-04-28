"""
Syntax Highlighting Editor - Editor Component
"""
import tkinter as tk
from tkinter import font, scrolledtext
import re
from highlighter import SyntaxHighlighter

class LineNumbers(tk.Canvas):
    """Canvas widget for displaying line numbers"""
    def __init__(self, parent, text_widget, **kwargs):
        super().__init__(parent, **kwargs)
        self.text_widget = text_widget
        self.text_font = font.Font(font=text_widget['font'])
        self.config(width=30)
        
        # Bind events to update line numbers
        self.text_widget.bind('<KeyPress>', self.redraw)
        self.text_widget.bind('<KeyRelease>', self.redraw)
        self.text_widget.bind('<MouseWheel>', self.redraw)
        self.text_widget.bind('<Configure>', self.redraw)
        self.text_widget.bind('<<Change>>', self.redraw)
        self.text_widget.bind('<FocusIn>', self.redraw)
    
    def redraw(self, *args):
        
        """Redraw the line numbers"""
        self.delete("all")
        
        # Get visible range of text
        i = self.text_widget.index("@0,0")
        while True:
            dline = self.text_widget.dlineinfo(i)
            if dline is None:
                break
            
            # Get the line number
            line_num = str(i).split('.')[0]
            
            # Draw the line number
            x = 2
            y = dline[1]
            self.create_text(x, y, anchor="nw", text=line_num, font=self.text_font, fill="#9D00FF")
            
            i = self.text_widget.index(f"{i}+1line")


class SyntaxEditor(tk.Frame):
    """Main editor component with syntax highlighting"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Create a custom font
        self.text_font = font.Font(family="Courier New", size=12)
        
        # Create a frame for the line numbers and text widget
        self.editor_frame = tk.Frame(self)
        self.editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the text widget
        self.text = scrolledtext.ScrolledText(
            self.editor_frame,
            wrap=tk.NONE,
            font=self.text_font,
            undo=True,
            maxundo=-1,
            autoseparators=True,
            bg="#f5f5ff",  # Light lavender background
            fg="#333333",  # Dark gray text for better contrast
            insertbackground="#FF1493",  # Bright pink cursor
            selectbackground="#c5e1ff",  # Light blue selection
            selectforeground="#000000",  # Black text in selection
            padx=5,
            pady=5
        )
        
        # Create line numbers
        self.line_numbers = LineNumbers(self.editor_frame, self.text, bg="#e8e8f0")
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Pack the text widget
        self.text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Configure horizontal scrolling
        self.x_scrollbar = tk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.text.xview)
        self.x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.text.config(xscrollcommand=self.x_scrollbar.set)
        
        # Create status bar
        self.status_bar = tk.Label(
            self, 
            text="Line: 1, Column: 0", 
            bd=1, 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            bg="#e0e8ff",  # Light blue background
            fg="#333333"   # Dark gray text
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Initialize syntax highlighter
        self.highlighter = SyntaxHighlighter(self.text)
        self.current_language = "python"  # Default language
        
        # Track modification state
        self._modified = False
        self.text.bind("<<Modified>>", self._on_modified)
        
        # Track cursor position for status bar
        self.text.bind("<KeyRelease>", self._update_status_bar)
        self.text.bind("<ButtonRelease-1>", self._update_status_bar)
        
        # Bind tab key to insert spaces instead of tab character
        self.text.bind("<Tab>", self._handle_tab)
        
        # Initialize with default content
        self.set_content("")
        self.set_language("python")
    
    def _handle_tab(self, event):
        """Handle tab key to insert spaces instead of tab character"""
        self.text.insert(tk.INSERT, " " * 4)
        return "break"  # Prevent default tab behavior
    
    def _on_modified(self, event):
        """Handle text modification events"""
        if self.text.edit_modified():
            self._modified = True
            self.text.edit_modified(False)
            
            # Update syntax highlighting
            self.highlighter.highlight_text(self.current_language)
    
    def _update_status_bar(self, event=None):
        """Update the status bar with cursor position"""
        position = self.text.index(tk.INSERT).split(".")
        line, column = int(position[0]), int(position[1])
        self.status_bar.config(text=f"Line: {line}, Column: {column}")
    
    def is_modified(self):
        """Check if the text has been modified"""
        return self._modified
    
    def set_modified(self, modified):
        """Set the modification state"""
        self._modified = modified
    
    def clear(self):
        """Clear the editor content"""
        self.text.delete(1.0, tk.END)
        self._modified = False
    
    def set_content(self, content):
        """Set the editor content"""
        self.clear()
        self.text.insert(tk.END, content)
        self._modified = False
        self.highlighter.highlight_text(self.current_language)
    
    def get_content(self):
        """Get the editor content"""
        return self.text.get(1.0, tk.END)
    
    def undo(self):
        """Undo the last action"""
        try:
            self.text.edit_undo()
        except tk.TclError:
            pass
    
    def redo(self):
        """Redo the last undone action"""
        try:
            self.text.edit_redo()
        except tk.TclError:
            pass
    
    def cut(self):
        """Cut selected text"""
        self.text.event_generate("<<Cut>>")
    
    def copy(self):
        """Copy selected text"""
        self.text.event_generate("<<Copy>>")
    
    def paste(self):
        """Paste text from clipboard"""
        self.text.event_generate("<<Paste>>")
    
    def select_all(self):
        """Select all text in the editor"""
        self.text.tag_add(tk.SEL, "1.0", tk.END)
        self.text.mark_set(tk.INSERT, "1.0")
        self.text.see(tk.INSERT)
    
    def toggle_line_numbers(self):
        """Toggle display of line numbers"""
        if self.line_numbers.winfo_ismapped():
            self.line_numbers.pack_forget()
        else:
            self.line_numbers.pack(side=tk.LEFT, fill=tk.Y, before=self.text)
    
    def set_language(self, language):
        """Set the syntax highlighting language"""
        self.current_language = language
        self.highlighter.highlight_text(language)
