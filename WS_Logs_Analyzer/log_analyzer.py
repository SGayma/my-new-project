import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import os
import re
from datetime import datetime
import threading
import time

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
        self.monitoring = False
        self.monitor_thread = None

        # Filter preset patterns
        self.filter_presets = {
            "Errors": r"(?i)(error|failed|exception|critical)",
            "Warnings": r"(?i)(warning|warn|deprecated)",
            "Commands": r"(?i)(command|cmd|execute|invoke)",
            "Timing": r"(?i)(time|duration|elapsed|ms|sec)",
            "All": ""
        }

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

        # Tab 2: Time Analysis
        self.timing_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.timing_frame, text="Command Timing")
        self._setup_timing_tab()

        # Tab 3: Real-time Monitor
        self.monitor_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.monitor_frame, text="Real-Time Monitor")
        self._setup_monitor_tab()

    def _setup_viewer_tab(self):
        """Setup the main log viewer tab."""
        frm = ttk.Frame(self.viewer_frame, padding="10")
        frm.pack(fill="both", expand=True)

        # --- Top Controls (File Loading) ---
        controls_frame = ttk.Frame(frm)
        controls_frame.pack(fill="x", pady=(0, 10))

        load_button = ttk.Button(controls_frame, text="Load Log File", command=self.load_log_file)
        load_button.pack(side="left", padx=(0, 10))

        self.file_label_var = tk.StringVar(value="No file loaded.")
        file_label = ttk.Label(controls_frame, textvariable=self.file_label_var, anchor="w", relief="sunken", width=40)
        file_label.pack(side="left", fill="x", expand=True)

        # --- Filter Type Selection ---
        filter_type_frame = ttk.Frame(frm)
        filter_type_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(filter_type_frame, text="Filter Type:").pack(side="left", padx=(0, 5))
        self.filter_type_var = tk.StringVar(value="Keyword Search")
        filter_types = ["Keyword Search", "Errors", "Warnings", "Commands", "Timing", "Custom Regex"]
        self.filter_type_combo = ttk.Combobox(filter_type_frame, textvariable=self.filter_type_var, 
                                              values=filter_types, state="readonly", width=20)
        self.filter_type_combo.pack(side="left", padx=(0, 10))
        self.filter_type_combo.bind("<<ComboboxSelected>>", self._on_filter_type_change)

        ttk.Label(filter_type_frame, text="Search Term:").pack(side="left", padx=(0, 5))
        self.filter_var = tk.StringVar()
        self.filter_var.trace_add("write", self.on_filter_change)
        filter_entry = ttk.Entry(filter_type_frame, textvariable=self.filter_var, width=40)
        filter_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        clear_button = ttk.Button(filter_type_frame, text="Clear", command=self.clear_filter)
        clear_button.pack(side="left", padx=(0, 5))

        self.case_sensitive_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(filter_type_frame, text="Case Sensitive", variable=self.case_sensitive_var, 
                       command=self.apply_filter).pack(side="left")

        # --- Log Display Area ---
        self.log_text = scrolledtext.ScrolledText(
            frm,
            wrap=tk.WORD,
            font=("Courier New", 9),
            state="disabled"
        )
        self.log_text.pack(fill="both", expand=True)

        # Configure tags for highlighting
        self.log_text.tag_configure("highlight", background="yellow", foreground="black", font=("Courier New", 9, "bold"))
        self.log_text.tag_configure("error", background="red", foreground="white")
        self.log_text.tag_configure("warning", background="orange", foreground="black")
        self.log_text.tag_configure("info", background="lightblue", foreground="black")

    def _setup_timing_tab(self):
        """Setup the command timing analysis tab."""
        frm = ttk.Frame(self.timing_frame, padding="10")
        frm.pack(fill="both", expand=True)

        # Controls
        ctrl_frame = ttk.Frame(frm)
        ctrl_frame.pack(fill="x", pady=(0, 10))

        ttk.Button(ctrl_frame, text="Analyze Timings", command=self.analyze_timings).pack(side="left", padx=(0, 10))
        ttk.Button(ctrl_frame, text="Export Results", command=self.export_timings).pack(side="left")

        ttk.Label(ctrl_frame, text="Command Pattern:").pack(side="left", padx=(10, 5))
        self.timing_pattern_var = tk.StringVar(value=r"(?i)(command|execute|step)")
        ttk.Entry(ctrl_frame, textvariable=self.timing_pattern_var, width=40).pack(side="left", padx=(0, 10))

        # Results display
        results_frame = ttk.Frame(frm)
        results_frame.pack(fill="both", expand=True)

        ttk.Label(results_frame, text="Timing Analysis Results:", font=("Arial", 10, "bold")).pack(anchor="w")

        self.timing_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            font=("Courier New", 9),
            state="disabled",
            height=20
        )
        self.timing_text.pack(fill="both", expand=True)

    def _setup_monitor_tab(self):
        """Setup the real-time log monitoring tab."""
        frm = ttk.Frame(self.monitor_frame, padding="10")
        frm.pack(fill="both", expand=True)

        # Controls
        ctrl_frame = ttk.Frame(frm)
        ctrl_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(ctrl_frame, text="Log File Path:").pack(side="left", padx=(0, 5))
        self.monitor_path_var = tk.StringVar(value=r"C:\workspace\WS_Logs_Analyzer\application.log")
        self.monitor_path_entry = ttk.Entry(ctrl_frame, textvariable=self.monitor_path_var, width=60)
        self.monitor_path_entry.pack(side="left", padx=(0, 10), fill="x", expand=True)

        ttk.Button(ctrl_frame, text="Browse", command=self._browse_monitor_file).pack(side="left", padx=(0, 10))

        self.monitor_button = ttk.Button(ctrl_frame, text="Start Monitoring", command=self.toggle_monitoring, 
                                        style="")
        self.monitor_button.pack(side="left", padx=(0, 10))

        ttk.Label(ctrl_frame, text="Refresh (sec):").pack(side="left", padx=(0, 5))
        self.refresh_rate_var = tk.StringVar(value="1")
        ttk.Spinbox(ctrl_frame, from_=0.5, to=10, textvariable=self.refresh_rate_var, width=5).pack(side="left")

        # Status indicator
        self.monitor_status_var = tk.StringVar(value="Status: Idle")
        ttk.Label(ctrl_frame, textvariable=self.monitor_status_var, foreground="gray").pack(side="left", padx=(10, 0))

        # Real-time display
        self.monitor_text = scrolledtext.ScrolledText(
            frm,
            wrap=tk.WORD,
            font=("Courier New", 9),
            state="disabled"
        )
        self.monitor_text.pack(fill="both", expand=True)
        self.monitor_text.tag_configure("new_line", background="lightgreen")

    def _browse_monitor_file(self):
        """Browse for a log file to monitor."""
        filepath = filedialog.askopenfilename(
            initialdir=self.log_dir if os.path.isdir(self.log_dir) else os.getcwd(),
            title="Select log file to monitor",
            filetypes=(("Log files", "application.log*"), ("All files", "*.*"))
        )
        if filepath:
            self.monitor_path_var.set(filepath)

    def _on_filter_type_change(self, *args):
        """Handle filter type selection change."""
        filter_type = self.filter_type_var.get()
        if filter_type in self.filter_presets and filter_type != "Keyword Search":
            self.filter_var.set(self.filter_presets[filter_type])

    def load_log_file(self):
        """Open a file dialog to select and load a log file."""
        filepath = filedialog.askopenfilename(
            initialdir=self.log_dir if os.path.isdir(self.log_dir) else os.getcwd(),
            title="Select a log file",
            filetypes=(("Log files", "application.log*"), ("All files", "*.*"))
        )
        if not filepath:
            return

        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                self.all_log_lines = f.readlines()
            self.current_file = filepath
            self.file_size = os.path.getsize(filepath)
            file_size_kb = self.file_size / 1024
            self.file_label_var.set(f"Loaded: {os.path.basename(filepath)} ({file_size_kb:.1f} KB, {len(self.all_log_lines)} lines)")
            self.display_logs(self.all_log_lines)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {e}")
            self.all_log_lines = []

    def on_filter_change(self, *args):
        """Callback function that triggers filtering when the user types."""
        self.apply_filter()

    def apply_filter(self):
        """Filter and highlight log lines based on the search term."""
        filter_term = self.filter_var.get()
        if not self.all_log_lines:
            return

        if not filter_term:
            self.display_logs(self.all_log_lines)
            return

        case_sensitive = self.case_sensitive_var.get()
        filter_type = self.filter_type_var.get()
        
        try:
            if filter_type == "Custom Regex":
                filtered_lines = [line for line in self.all_log_lines 
                                if re.search(filter_term, line, 0 if case_sensitive else re.IGNORECASE)]
                self.display_logs(filtered_lines, highlight_term=filter_term, is_regex=True)
            else:
                filtered_lines = [line for line in self.all_log_lines 
                                if filter_term.lower() in line.lower()] if not case_sensitive else \
                               [line for line in self.all_log_lines if filter_term in line]
                self.display_logs(filtered_lines, highlight_term=filter_term, is_regex=False)
        except re.error as e:
            messagebox.showerror("Regex Error", f"Invalid regex pattern: {e}")

    def clear_filter(self):
        """Clear the filter entry and show all log lines."""
        self.filter_var.set("")
        self.display_logs(self.all_log_lines)

    def display_logs(self, lines_to_display, highlight_term=None, is_regex=False):
        """
        Updates the text widget with the given lines and optionally highlights a term.
        """
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", tk.END)

        for line in lines_to_display:
            self.log_text.insert(tk.END, line)

        if highlight_term:
            self.highlight_matches(highlight_term, is_regex)

        self.log_text.config(state="disabled")

    def highlight_matches(self, term, is_regex=False):
        """Finds and applies highlighting to all occurrences of a term."""
        self.log_text.tag_remove("highlight", "1.0", tk.END)
        start_pos = "1.0"
        
        try:
            if is_regex:
                content = self.log_text.get("1.0", tk.END)
                for match in re.finditer(term, content, re.IGNORECASE):
                    start_idx = match.start()
                    end_idx = match.end()
                    start_pos = self.log_text.index(f"1.0+{start_idx}c")
                    end_pos = self.log_text.index(f"1.0+{end_idx}c")
                    self.log_text.tag_add("highlight", start_pos, end_pos)
            else:
                while True:
                    start_pos = self.log_text.search(term, start_pos, stopindex=tk.END, nocase=True)
                    if not start_pos:
                        break
                    end_pos = f"{start_pos}+{len(term)}c"
                    self.log_text.tag_add("highlight", start_pos, end_pos)
                    start_pos = end_pos
        except Exception as e:
            messagebox.showerror("Highlight Error", f"Error highlighting text: {e}")

    def analyze_timings(self):
        """Analyze command timing from log file."""
        if not self.all_log_lines:
            messagebox.showwarning("No Data", "Load a log file first")
            return

        pattern = self.timing_pattern_var.get()
        try:
            timestamps = []
            command_times = []
            
            # Extract timestamps and commands
            for line in self.all_log_lines:
                # Try to extract timestamp (common formats: HH:MM:SS, [HH:MM:SS.mmm], etc.)
                time_match = re.search(r'\[?(\d{1,2}:\d{2}:\d{2}(?:\.\d+)?)\]?', line)
                if time_match:
                    timestamps.append(time_match.group(1))
                
                if re.search(pattern, line, re.IGNORECASE):
                    command_times.append(time_match.group(1) if time_match else "N/A")

            # Calculate time differences
            results = "=== Command Timing Analysis ===\n\n"
            results += f"Total log lines: {len(self.all_log_lines)}\n"
            results += f"Lines with timestamps: {len(timestamps)}\n"
            results += f"Commands found: {len(command_times)}\n"
            results += f"Pattern used: {pattern}\n"
            results += "\n" + "="*40 + "\n\n"

            if len(timestamps) > 1:
                results += "Time intervals between log entries:\n"
                for i in range(min(20, len(timestamps)-1)):
                    results += f"  Entry {i+1} to {i+2}: Timestamp {timestamps[i]} -> {timestamps[i+1]}\n"
                if len(timestamps) > 20:
                    results += f"  ... and {len(timestamps)-20} more entries\n"

            results += "\n" + "="*40 + "\n"
            results += "Commands detected:\n"
            for i, cmd_time in enumerate(command_times[:30], 1):
                results += f"  Command {i}: {cmd_time}\n"
            if len(command_times) > 30:
                results += f"  ... and {len(command_times)-30} more commands\n"

            self.timing_text.config(state="normal")
            self.timing_text.delete("1.0", tk.END)
            self.timing_text.insert(tk.END, results)
            self.timing_text.config(state="disabled")

        except re.error as e:
            messagebox.showerror("Regex Error", f"Invalid pattern: {e}")

    def export_timings(self):
        """Export timing analysis to a file."""
        if not self.timing_text.get("1.0", tk.END).strip():
            messagebox.showwarning("No Data", "Run analysis first")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filepath:
            try:
                with open(filepath, 'w') as f:
                    f.write(self.timing_text.get("1.0", tk.END))
                messagebox.showinfo("Success", f"Results exported to: {filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")

    def toggle_monitoring(self):
        """Toggle real-time log monitoring."""
        if self.monitoring:
            self.monitoring = False
            self.monitor_button.config(text="Start Monitoring")
            self.monitor_status_var.set("Status: Stopped")
        else:
            filepath = self.monitor_path_var.get()
            if not os.path.isfile(filepath):
                messagebox.showerror("Error", "Invalid file path")
                return
            self.monitoring = True
            self.monitor_button.config(text="Stop Monitoring")
            self.monitor_status_var.set("Status: Monitoring...")
            self.monitor_thread = threading.Thread(target=self._monitor_log_file, daemon=True)
            self.monitor_thread.start()

    def _monitor_log_file(self):
        """Monitor log file for changes and display new lines."""
        filepath = self.monitor_path_var.get()
        last_size = 0
        
        try:
            while self.monitoring:
                try:
                    current_size = os.path.getsize(filepath)
                    if current_size > last_size:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            f.seek(last_size)
                            new_lines = f.readlines()
                            last_size = current_size
                        
                        self.monitor_text.config(state="normal")
                        for line in new_lines:
                            self.monitor_text.insert(tk.END, line, "new_line")
                        self.monitor_text.see(tk.END)
                        self.monitor_text.config(state="disabled")
                except IOError:
                    pass
                
                time.sleep(float(self.refresh_rate_var.get()))
        except Exception as e:
            self.monitor_status_var.set(f"Status: Error - {str(e)}")

def main():
    root = tk.Tk()
    app = LogAnalyzerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()