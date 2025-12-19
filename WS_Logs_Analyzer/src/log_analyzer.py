import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import os
import re
from collections import defaultdict

# --- Pre-compiled Regex for Performance ---
HIGHLIGHT_PATTERNS = {
    "error": re.compile(r'\b(ERROR|EXCEPTION|CRITICAL|FAILED)\b', re.IGNORECASE),
    "warning": re.compile(r'\b(WARNING|WARN|DEPRECATED)\b', re.IGNORECASE),
    "info": re.compile(r'\b(COMMAND|EXECUTE|INVOKE|STEP)\b', re.IGNORECASE),
    "loglevel_engine": re.compile(r'\bEngine\b'),
    "loglevel_debug": re.compile(r'\bDebug\b'),
    "loglevel_info": re.compile(r'\bInfo\b'),
    "loglevel_trace": re.compile(r'\bTrace\b'),
    # Error level is already covered by the 'error' tag pattern
}


class LogAnalyzerApp:
    """
    Advanced log analysis tool for application.log* files with filtering, 
    timing analysis, and real-time monitoring capabilities.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Log Analyzer - Wave Studio")
        self.root.geometry("1200x800")

        # --- State Variables ---
        self.log_dir = r"C:\workspace\WS_Logs_Analyzer"
        self.all_log_lines = []
        self.current_file = ""
        self.file_size = 0
        self.log_selection_window = None
        self.level_filter_vars = {}
        self.source_engine_only_var = tk.BooleanVar(value=False)

        # --- UI Setup ---
        self._setup_widgets()


    def _setup_widgets(self):
        """Create and arrange all the GUI widgets."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True, pady=(0, 10))

        # Tab 1: Log Viewer
        self.viewer_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.viewer_frame, text="Log Viewer")
        self._setup_viewer_tab()

    def _setup_viewer_tab(self):
        """Setup the main log viewer tab."""
        frm = ttk.Frame(self.viewer_frame, padding="10")
        frm.pack(fill="both", expand=True)

        # --- Top Controls (File Loading) ---
        controls_frame = ttk.Frame(frm)
        controls_frame.pack(fill="x", pady=(0, 10))

        load_button = ttk.Button(controls_frame, text="Browse for Logs...", command=self.open_log_browser)
        load_button.pack(side="left", padx=(0, 10))

        self.file_label_var = tk.StringVar(value="No file loaded.")
        file_label = ttk.Label(controls_frame, textvariable=self.file_label_var, anchor="w", relief="sunken", width=40)
        file_label.pack(side="left", fill="x", expand=True)

        # --- Filter Controls ---
        filter_frame = ttk.Frame(frm)
        filter_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(filter_frame, text="Search:").pack(side="left", padx=(0, 5))
        self.filter_var = tk.StringVar()
        self.filter_var.trace_add("write", self.on_filter_change)
        filter_entry = ttk.Entry(filter_frame, textvariable=self.filter_var, width=40)
        filter_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        clear_button = ttk.Button(filter_frame, text="Clear", command=self.clear_filter)
        clear_button.pack(side="left", padx=(0, 5))

        self.case_sensitive_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(filter_frame, text="Case Sensitive", variable=self.case_sensitive_var, 
                       command=self.apply_filter).pack(side="left")
        
        self.command_only_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(filter_frame, text="Command Only", variable=self.command_only_var,
                       command=self.apply_filter).pack(side="left", padx=(10, 0))

        ttk.Checkbutton(filter_frame, text="Source 'Engine' Only", variable=self.source_engine_only_var,
                       command=self.apply_filter).pack(side="left", padx=(10, 0))

        # --- Log Level Filter ---
        level_filter_frame = ttk.Frame(frm)
        level_filter_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(level_filter_frame, text="Levels:").pack(side="left", padx=(0, 5))

        levels = ["TRACE", "ENGINE", "DEBUG", "INFO", "ERROR"]
        for level in levels:
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(level_filter_frame, text=level, variable=var, command=self.apply_filter)
            cb.pack(side="left", padx=5)
            self.level_filter_vars[level] = var

        # Option to force highlighting even for large result sets
        # (removed Always highlight checkbox to avoid accidental heavy highlighting)

        # --- Log Display Area ---
        self.log_text = scrolledtext.ScrolledText(
            frm,
            wrap=tk.NONE,
            font=("Courier New", 9),
            state="disabled"
        )
        self.log_text.pack(fill="both", expand=True)

        # Configure tags for highlighting
        self.log_text.tag_configure("highlight", background="yellow", foreground="black", font=("Courier New", 9, "bold"))
        self.log_text.tag_configure("error", background="red", foreground="white")
        self.log_text.tag_configure("warning", background="orange", foreground="black")
        self.log_text.tag_configure("info", background="lightblue", foreground="black")
        # Log level tags
        self.log_text.tag_configure("loglevel_engine", background="#FFD700", foreground="black", font=("Courier New", 9, "bold"))  # Gold
        self.log_text.tag_configure("loglevel_debug", background="#87CEEB", foreground="black", font=("Courier New", 9, "bold"))   # Sky Blue
        self.log_text.tag_configure("loglevel_info", background="#90EE90", foreground="black", font=("Courier New", 9, "bold"))    # Light Green
        self.log_text.tag_configure("loglevel_trace", background="#DDA0DD", foreground="black", font=("Courier New", 9, "bold"))   # Plum
        self.log_text.tag_configure("loglevel_error", background="#FF6B6B", foreground="white", font=("Courier New", 9, "bold"))   # Red

    def apply_filter(self):
        """Filter and highlight log lines based on the search term and selected levels."""
        filter_term = self.filter_var.get()

        # Start with all lines
        working_lines = self.all_log_lines

        # --- Level Filtering ---
        if hasattr(self, 'level_filter_vars') and self.level_filter_vars:
            selected_levels = [level for level, var in self.level_filter_vars.items() if var.get()]
            
            if selected_levels:
                level_pattern = r'\b(' + '|'.join(re.escape(level) for level in selected_levels) + r')\b'
                level_regex = re.compile(level_pattern, re.IGNORECASE)
                
                level_filtered_lines = []
                for line in working_lines:
                    parts = line.split(" - ")
                    if len(parts) >= 2:
                        line_level = parts[1].strip()
                        if level_regex.search(line_level):
                            level_filtered_lines.append(line)
                working_lines = level_filtered_lines
            else:
                # No levels selected, show nothing.
                working_lines = []

        # --- Source 'Engine' Filtering ---
        if self.source_engine_only_var.get():
            engine_filtered_lines = []
            for line in working_lines:
                parts = line.split(" - ")
                if len(parts) >= 3:
                    source = parts[2].strip()
                    if source == "Engine":
                        engine_filtered_lines.append(line)
            working_lines = engine_filtered_lines

        # --- Text Filtering ---
        if filter_term:
            case_sensitive = self.case_sensitive_var.get()

            if case_sensitive:
                text_filtered_lines = [line for line in working_lines if filter_term in line]
            else:
                text_filtered_lines = [line for line in working_lines if filter_term.lower() in line.lower()]
            working_lines = text_filtered_lines
        
        self.display_logs(working_lines, highlight_term=filter_term, is_regex=False)

    def open_log_browser(self):
        """Open a dialog to select a directory and then show a log selection window."""
        default_log_dir = r"C:\ProgramData\MVG\Wave Studio"
        initial_dir = default_log_dir if os.path.isdir(default_log_dir) else (self.log_dir if os.path.isdir(self.log_dir) else os.getcwd())
        
        dir_path = filedialog.askdirectory(
            initialdir=initial_dir,
            title="Select Directory Containing Logs"
        )
        
        if not dir_path:
            return

        log_files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f)) and re.match(r"^application\.log(\.\d+)?$", f)]
        log_files.sort(key=lambda f: int(f.split('.')[-1]) if f.split('.')[-1].isdigit() else -1) # Sort numerically

        if not log_files:
            messagebox.showinfo("No Logs Found", f"No 'application.log' or 'application.log.X' files found in '{dir_path}'.")
            return

        self._create_log_selection_window(dir_path, log_files)

    def _create_log_selection_window(self, dir_path, log_files):
        """Creates a Toplevel window for selecting which log files to load."""
        if self.log_selection_window and self.log_selection_window.winfo_exists():
            self.log_selection_window.destroy()

        self.log_selection_window = tk.Toplevel(self.root)
        self.log_selection_window.title("Select Logs to Load")
        self.log_selection_window.geometry("400x500")

        frm = ttk.Frame(self.log_selection_window, padding=10)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text=f"Found logs in: {dir_path}", wraplength=380).pack(fill="x", pady=(0, 10))

        # --- File list with checkboxes ---
        list_frame = ttk.Frame(frm)
        list_frame.pack(fill="both", expand=True, pady=5)
        
        self.log_file_vars = {}
        for i, log_file in enumerate(log_files):
            # Default to selecting only the first log file (application.log)
            is_selected = (i == 0)
            var = tk.BooleanVar(value=is_selected)
            cb = ttk.Checkbutton(list_frame, text=log_file, variable=var)
            cb.pack(anchor="w")
            self.log_file_vars[log_file] = var

        # --- Control buttons ---
        btn_frame = ttk.Frame(frm)
        btn_frame.pack(fill="x", pady=(10, 0))

        load_btn = ttk.Button(btn_frame, text="Load Selected Logs", 
                              command=lambda: self.load_selected_logs(dir_path))
        load_btn.pack(side="right")

        cancel_btn = ttk.Button(btn_frame, text="Cancel", command=self.log_selection_window.destroy)
        cancel_btn.pack(side="right", padx=(0, 10))

    def load_selected_logs(self, dir_path):
        """Concatenates and loads the logs selected in the browser window."""
        selected_files = [os.path.join(dir_path, f) for f, var in self.log_file_vars.items() if var.get()]

        if not selected_files:
            messagebox.showwarning("No Selection", "Please select at least one log file to load.")
            return

        try:
            combined_content = self._concatenate_and_sort_logs(selected_files)
            self.all_log_lines = combined_content.splitlines(True) # Keep newlines
            
            total_size = sum(os.path.getsize(f) for f in selected_files)
            file_count = len(selected_files)
            self.file_label_var.set(f"Loaded {file_count} files ({total_size/1024:.1f} KB, {len(self.all_log_lines)} lines)")
            
            self.apply_filter()
            
            if self.log_selection_window:
                self.log_selection_window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load or process logs: {e}")
            self.all_log_lines = []

    def on_filter_change(self, *args):
        """Callback function that triggers filtering when the user types."""
        self.apply_filter()

    def clear_filter(self):
        """Clear the filter entry and re-apply filters."""
        self.filter_var.set("")
        self.apply_filter()

    def _concatenate_and_sort_logs(self, file_paths):
        """
        Reads multiple log files, concatenates their content, and sorts it chronologically.
        """
        all_lines = []
        timestamp_pattern = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}")

        for path in file_paths:
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        # Only include lines that appear to be valid log entries
                        if timestamp_pattern.match(line):
                            all_lines.append(line)
            except IOError as e:
                messagebox.showerror("File Error", f"Error reading file {path}: {e}")
                return ""

        # The timestamp format (YYYY-MM-DD HH:MM:SS,ms) is naturally sortable as a string.
        all_lines.sort()

        return "".join(all_lines)

    def display_logs(self, lines_to_display, highlight_term=None, is_regex=False):
        """
        Updates the text widget with the given lines and optionally highlights a term.
        For very large results, skip highlighting to prevent hang.
        Formats columns clearly with alignment, or shows command-only if enabled.
        """
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", tk.END)
        # Clear all tags before re-populating
        for tag in self.log_text.tag_names():
            self.log_text.tag_remove(tag, "1.0", tk.END)

        # Determine formatting and prepare search term regex if needed
        if self.command_only_var.get():
            line_formatter = self._extract_command
            # Insert header for command-only view
            self.log_text.insert(tk.END, "Command / Message\n", ("header",))
            self.log_text.insert(tk.END, ("-" * 120) + "\n", ("header",))
        else:
            line_formatter = self._format_log_line
            # Insert header for full log view
            header = f"{'DateTime':<24} {'Level':<10} {'Source':<25} {'Message'}\n"
            self.log_text.insert(tk.END, header, ("header",))
            self.log_text.insert(tk.END, ("-" * 120) + "\n", ("header",))

        search_term_regex = None
        if highlight_term:
            try:
                # For plain text search, escape special characters
                pattern = highlight_term if is_regex else re.escape(highlight_term)
                search_term_regex = re.compile(pattern, re.IGNORECASE)
            except re.error:
                search_term_regex = None # Ignore invalid regex

        # --- Highlighting Logic ---
        # Process and insert line by line, applying tags during insertion
        for line in lines_to_display:
            formatted_line = line_formatter(line)
            
            # Collect all matches for this line (syntax and search term)
            matches = defaultdict(list)
            
            # Syntax highlighting matches
            if not self.command_only_var.get():
                for tag, pattern in HIGHLIGHT_PATTERNS.items():
                    for match in pattern.finditer(formatted_line):
                        matches[tag].append(match.span())

            # User search term matches
            if search_term_regex:
                for match in search_term_regex.finditer(formatted_line):
                    matches["highlight"].append(match.span())

            # If no matches, insert the whole line at once (fast path)
            if not matches:
                self.log_text.insert(tk.END, formatted_line + '\n')
                continue

            # If there are matches, insert the line in tagged segments
            last_end = 0
            all_spans = sorted([(start, end, tag) for tag, spans in matches.items() for start, end in spans])

            for start, end, tag in all_spans:
                if start >= last_end:
                    # Insert text before the current match
                    if start > last_end:
                        self.log_text.insert(tk.END, formatted_line[last_end:start])
                    # Insert the matched text with its tag
                    self.log_text.insert(tk.END, formatted_line[start:end], (tag,))
                    last_end = end
            
            # Insert any remaining text after the last match
            if last_end < len(formatted_line):
                self.log_text.insert(tk.END, formatted_line[last_end:])
            
            self.log_text.insert(tk.END, '\n')

        self.log_text.config(state="disabled")

    def _extract_command(self, line):
        """Extract only the command/message part from a log line.
        
        Log format: DATE TIME - LEVEL - SOURCE - COMMAND
        Example: 2025-11-26 11:28:31,281 - DEBUG - Ieee488Connection - TCPIP0::10.1.53.153::hislip0::INSTR <-- FETCh:DUT:MODem:STATe:RRC?
        We want: FETCh:DUT:MODem:STATe:RRC?
        """
        # Split by " - " to separate columns
        parts = line.split(" - ")
        
        if len(parts) >= 4:
            # Format: DATE TIME | LEVEL | SOURCE | COMMAND
            # Get the 4th part and everything after (in case command contains " - ")
            command = " - ".join(parts[3:]).rstrip()
            return command
        elif len(parts) >= 3:
            # Fallback: DATE TIME | LEVEL | COMMAND
            command = " - ".join(parts[2:]).rstrip()
            return command
        else:
            # No dashes found, return the whole line
            return line.rstrip()

    def _format_log_line(self, line):
        """Parse and format a log line with aligned columns.
        
        Log format: DATE TIME - LEVEL - SOURCE - MESSAGE
        Example: 2025-11-26 11:28:31,281 - DEBUG - Ieee488Connection - TCPIP0::...
        """
        # Split by " - " to get the dash-separated parts
        parts = line.split(" - ")
        
        if len(parts) >= 3:
            # Extract: date+time, level, source, message
            datetime_col = parts[0].strip() if len(parts) > 0 else ""
            level_col = parts[1].strip() if len(parts) > 1 else ""
            source_col = parts[2].strip() if len(parts) > 2 else ""
            message = " - ".join(parts[3:]).strip() if len(parts) > 3 else ""
            
            # Format with fixed column widths for alignment
            # Date (12) | Time (12) | Level (10) | Source (25) | Message
            formatted = f"{datetime_col:<24} {level_col:<10} {source_col:<25} {message}"
            return formatted
        else:
            # Fallback for malformed lines
            return line.rstrip()


def main():
    root = tk.Tk()
    app = LogAnalyzerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
