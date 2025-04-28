#!/usr/bin/env python3
"""
Syntax Highlighting Editor - Main Application
"""
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import os
from editor import SyntaxEditor

class SyntaxHighlightingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Syntax Highlighting Editor")
        self.root.geometry("1000x700")
        
        # Create a frame for the toolbar
        self.toolbar = tk.Frame(self.root)
        self.toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        
        # Add language selection dropdown
        self.language_var = tk.StringVar(value="python")  # Default language
        self.language_dropdown = ttk.Combobox(
            self.toolbar,
            textvariable=self.language_var,
            values=["python", "javascript", "html", "css"],
            state="readonly",
            width=15
        )
        self.language_dropdown.pack(side=tk.LEFT, padx=5)
        self.language_dropdown.bind("<<ComboboxSelected>>", self.on_language_change)
        
        # Add a label for the dropdown
        tk.Label(self.toolbar, text="Language:").pack(side=tk.LEFT)
        
        # Set up the menu bar
        self.setup_menu()
        
        # Create the main editor component
        self.editor = SyntaxEditor(self.root)
        self.editor.pack(fill=tk.BOTH, expand=True)
        
        # Track the current file
        self.current_file = None
        
        # Set up keyboard shortcuts
        self.setup_shortcuts()
    
    def setup_menu(self):
        """Set up the application menu bar"""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.exit_app, accelerator="Alt+F4")
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all, accelerator="Ctrl+A")
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Toggle Line Numbers", command=self.toggle_line_numbers)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def setup_shortcuts(self):
        """Set up keyboard shortcuts for common operations"""
        self.root.bind("<Control-n>", lambda event: self.new_file())
        self.root.bind("<Control-o>", lambda event: self.open_file())
        self.root.bind("<Control-s>", lambda event: self.save_file())
        self.root.bind("<Control-Shift-S>", lambda event: self.save_as_file())
        self.root.bind("<Control-a>", lambda event: self.select_all())
    
    def on_language_change(self, event=None):
        """Handle language selection from dropdown"""
        language = self.language_var.get()
        self.set_language(language)
    
    def new_file(self):
        """Create a new empty file"""
        if self.editor.is_modified():
            if not self.prompt_save_changes():
                return
        
        self.editor.clear()
        self.current_file = None
        self.root.title("Syntax Highlighting Editor - Untitled")
        self.language_var.set("python")  # Reset to default language
    
    def open_file(self):
        """Open an existing file"""
        if self.editor.is_modified():
            if not self.prompt_save_changes():
                return
        
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Python Files", "*.py"),
                ("JavaScript Files", "*.js"),
                ("HTML Files", "*.html"),
                ("CSS Files", "*.css"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                
                self.editor.set_content(content)
                self.current_file = file_path
                self.root.title(f"Syntax Highlighting Editor - {os.path.basename(file_path)}")
                
                # Auto-detect language based on file extension
                ext = os.path.splitext(file_path)[1].lower()
                if ext == '.py':
                    self.set_language("python")
                    self.language_var.set("python")
                elif ext == '.js':
                    self.set_language("javascript")
                    self.language_var.set("javascript")
                elif ext == '.html':
                    self.set_language("html")
                    self.language_var.set("html")
                elif ext == '.css':
                    self.set_language("css")
                    self.language_var.set("css")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {str(e)}")
    
    def save_file(self):
        """Save the current file"""
        if self.current_file:
            try:
                content = self.editor.get_content()
                with open(self.current_file, 'w') as file:
                    file.write(content)
                self.editor.set_modified(False)
                return True
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
                return False
        else:
            return self.save_as_file()
    
    def save_as_file(self):
        """Save the current file with a new name"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[
                ("Python Files", "*.py"),
                ("JavaScript Files", "*.js"),
                ("HTML Files", "*.html"),
                ("CSS Files", "*.css"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            self.current_file = file_path
            self.root.title(f"Syntax Highlighting Editor - {os.path.basename(file_path)}")
            # Update language based on saved file extension
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.py':
                self.language_var.set("python")
                self.set_language("python")
            elif ext == '.js':
                self.language_var.set("javascript")
                self.set_language("javascript")
            elif ext == '.html':
                self.language_var.set("html")
                self.set_language("html")
            elif ext == '.css':
                self.language_var.set("css")
                self.set_language("css")
            return self.save_file()
        return False
    
    def prompt_save_changes(self):
        """Prompt the user to save changes before closing the current file"""
        response = messagebox.askyesnocancel(
            "Unsaved Changes",
            "Do you want to save changes before closing?"
        )
        
        if response is None:  # Cancel
            return False
        elif response:  # Yes
            return self.save_file()
        else:  # No
            return True
    
    def exit_app(self):
        """Exit the application"""
        if self.editor.is_modified():
            if not self.prompt_save_changes():
                return
        
        self.root.quit()
    
    def undo(self):
        """Undo the last action"""
        self.editor.undo()
    
    def redo(self):
        """Redo the last undone action"""
        self.editor.redo()
    
    def cut(self):
        """Cut selected text"""
        self.editor.cut()
    
    def copy(self):
        """Copy selected text"""
        self.editor.copy()
    
    def paste(self):
        """Paste text from clipboard"""
        self.editor.paste()
    
    def select_all(self):
        """Select all text in the editor"""
        self.editor.select_all()
    
    def toggle_line_numbers(self):
        """Toggle display of line numbers"""
        self.editor.toggle_line_numbers()
    
    def set_language(self, language):
        """Set the syntax highlighting language"""
        self.editor.set_language(language)
    
    def show_about(self):
        """Show the about dialog"""
        messagebox.showinfo(
            "About Syntax Highlighting Editor",
            "Syntax Highlighting Editor\n\n"
            "A lightweight text editor with syntax highlighting capabilities.\n"
            "Created for the Programming Language Concepts final project."
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = SyntaxHighlightingApp(root)
    root.mainloop()