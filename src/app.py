import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from src import parser
from src import plot_viz
from src import compare


class CalibApp:
    def __init__(self, root, initial_file=None):
        self.root = root
        root.title('AGC Comparison Tool & Offset')
        root.geometry('900x700')

        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        # Tab 1: File Comparison (FIRST)
        self.compare_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.compare_frame, text='Compare Files')
        self._setup_compare_tab()

        # Tab 2: Offset Application
        self.offset_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.offset_frame, text='Apply Offset')
        self._setup_offset_tab(initial_file)

        # Ensure the Compare Files tab is selected first on startup
        try:
            self.notebook.select(0)
        except Exception:
            pass

    def _setup_offset_tab(self, initial_file):
        """Setup the offset application tab."""
        frm = ttk.Frame(self.offset_frame, padding=10)
        frm.pack(fill='both', expand=True)

        # File selector
        self.file_var = tk.StringVar()
        if initial_file:
            self.file_var.set(initial_file)
        file_row = ttk.Frame(frm)
        file_row.pack(fill='x', pady=(0, 8))
        ttk.Label(file_row, text='File:', width=10).pack(side='left')
        self.file_entry = ttk.Entry(file_row, textvariable=self.file_var, width=70)
        self.file_entry.pack(side='left', padx=(0, 5))
        ttk.Button(file_row, text='Browse', command=self.browse_file).pack(side='left')

        # Section dropdown
        sec_row = ttk.Frame(frm)
        sec_row.pack(fill='x', pady=(0, 8))
        ttk.Label(sec_row, text='Section:', width=10).pack(side='left')
        self.section_var = tk.StringVar()
        self.section_combo = ttk.Combobox(sec_row, textvariable=self.section_var, state='readonly', width=40)
        self.section_combo.pack(side='left', padx=(0, 10))

        # Offset input
        ttk.Label(sec_row, text='Offset (dB):', width=12).pack(side='left')
        self.offset_var = tk.StringVar()
        self.offset_combo = ttk.Combobox(sec_row, textvariable=self.offset_var, values=[-10, -5, -1, -0.5, 0, 0.5, 1, 5, 10], width=10)
        self.offset_combo.pack(side='left')

        # Buttons
        btn_row = ttk.Frame(frm)
        btn_row.pack(fill='x', pady=(0, 8))
        ttk.Button(btn_row, text='Load & Parse', command=self.load_parse).pack(side='left', padx=(0, 6))
        ttk.Button(btn_row, text='Preview', command=self.preview).pack(side='left', padx=(0, 6))
        ttk.Button(btn_row, text='Plot', command=self.plot_result).pack(side='left', padx=(0, 6))
        ttk.Button(btn_row, text='Apply & Save', command=self.apply_and_save).pack(side='left')

        # Preview text
        self.preview_txt = tk.Text(frm, width=100, height=25)
        self.preview_txt.pack(fill='both', expand=True)

        # internal state
        self.sections = {}
        self.lines = []
        self.loaded_path = None

    def _setup_compare_tab(self):
        """Setup the file comparison tab."""
        frm = ttk.Frame(self.compare_frame, padding=10)
        frm.pack(fill='both', expand=True)

        # File 1
        f1_row = ttk.Frame(frm)
        f1_row.pack(fill='x', pady=(0, 8))
        ttk.Label(f1_row, text='File 1:', width=10).pack(side='left')
        self.file1_var = tk.StringVar()
        self.file1_entry = ttk.Entry(f1_row, textvariable=self.file1_var, width=70)
        self.file1_entry.pack(side='left', padx=(0, 5))
        ttk.Button(f1_row, text='Browse', command=lambda: self._browse_compare_file(1)).pack(side='left')

        # File 2
        f2_row = ttk.Frame(frm)
        f2_row.pack(fill='x', pady=(0, 8))
        ttk.Label(f2_row, text='File 2:', width=10).pack(side='left')
        self.file2_var = tk.StringVar()
        self.file2_entry = ttk.Entry(f2_row, textvariable=self.file2_var, width=70)
        self.file2_entry.pack(side='left', padx=(0, 5))
        ttk.Button(f2_row, text='Browse', command=lambda: self._browse_compare_file(2)).pack(side='left')

        # Section selector
        sec_row = ttk.Frame(frm)
        sec_row.pack(fill='x', pady=(0, 8))
        ttk.Label(sec_row, text='Section:', width=10).pack(side='left')
        self.compare_section_var = tk.StringVar()
        self.compare_section_combo = ttk.Combobox(sec_row, textvariable=self.compare_section_var, state='readonly', width=40)
        self.compare_section_combo.pack(side='left', padx=(0, 10))
        ttk.Button(sec_row, text='Load Sections', command=self.load_compare_sections).pack(side='left')

        # Buttons
        btn_row = ttk.Frame(frm)
        btn_row.pack(fill='x', pady=(0, 8))
        ttk.Button(btn_row, text='Compare & Plot', command=self.compare_and_plot).pack(side='left', padx=(0, 6))
        ttk.Button(btn_row, text='Show Stats', command=self.show_compare_stats).pack(side='left')

        # Stats/results text
        self.compare_txt = tk.Text(frm, width=100, height=25)
        self.compare_txt.pack(fill='both', expand=True)

        # internal state
        self.compare_result = None

    # ===== Offset Tab Methods =====
    def browse_file(self):
        path = filedialog.askopenfilename(title='Open .calib file', filetypes=[('Calib files', '*.calib'), ('All files', '*.*')])
        if path:
            self.file_var.set(path)

    def load_parse(self):
        path = self.file_var.get()
        if not path:
            messagebox.showwarning('No file', 'Please choose a .calib file first')
            return
        try:
            self.sections, self.lines = parser.parse_calib(path)
            self.loaded_path = path
        except Exception as e:
            messagebox.showerror('Error', f'Failed to parse file: {e}')
            return
        keys = sorted(self.sections.keys())
        self.section_combo['values'] = keys
        if keys:
            self.section_combo.current(0)
        messagebox.showinfo('Parsed', f'Found {len(keys)} GainTable section(s)')

    def preview(self):
        if not self.lines:
            messagebox.showwarning('Not loaded', 'Load a file first')
            return
        sec = self.section_var.get()
        if not sec:
            messagebox.showwarning('No section', 'Select a GainTable section')
            return
        try:
            offset = float(self.offset_var.get())
        except Exception:
            messagebox.showwarning('Invalid offset', 'Enter a numeric offset')
            return
        new_lines = parser.apply_offset_to_section(self.lines, self.sections, sec, offset)
        entries = self.sections.get(sec, [])
        if not entries:
            self.preview_txt.delete('1.0', tk.END)
            self.preview_txt.insert(tk.END, 'No numeric lines found in this section.')
            return
        first_idx = entries[0][0]
        start = max(0, first_idx - 5)
        end = min(len(new_lines), entries[-1][0] + 6)
        preview_text = ''.join(new_lines[start:end])
        self.preview_txt.delete('1.0', tk.END)
        self.preview_txt.insert(tk.END, preview_text)

    def plot_result(self):
        if not self.sections:
            messagebox.showwarning('Not loaded', 'Load a file first')
            return
        sec = self.section_var.get()
        if not sec:
            messagebox.showwarning('No section', 'Select a GainTable section')
            return
        try:
            offset = float(self.offset_var.get())
        except Exception:
            messagebox.showwarning('Invalid offset', 'Enter a numeric offset')
            return
        try:
            plot_viz.plot_offset_comparison(self.sections, sec, offset)
        except Exception as e:
            messagebox.showerror('Plot error', f'Failed to create plot: {e}')

    def apply_and_save(self):
        if not self.lines or not self.loaded_path:
            messagebox.showwarning('Not loaded', 'Load a file first')
            return
        sec = self.section_var.get()
        if not sec:
            messagebox.showwarning('No section', 'Select a GainTable section')
            return
        try:
            offset = float(self.offset_var.get())
        except Exception:
            messagebox.showwarning('Invalid offset', 'Enter a numeric offset')
            return
        new_lines = parser.apply_offset_to_section(self.lines, self.sections, sec, offset)
        suffix = f"modified_{datetime.now().strftime('%Y%m%d')}_offset{offset}"
        try:
            new_path = parser.save_with_suffix(self.loaded_path, new_lines, suffix)
        except Exception as e:
            messagebox.showerror('Save error', f'Failed to save file: {e}')
            return
        messagebox.showinfo('Saved', f'File saved to: {new_path}')

    # ===== Compare Tab Methods =====
    def _browse_compare_file(self, file_num):
        path = filedialog.askopenfilename(title=f'Open .calib file {file_num}', filetypes=[('Calib files', '*.calib'), ('All files', '*.*')])
        if path:
            if file_num == 1:
                self.file1_var.set(path)
            else:
                self.file2_var.set(path)

    def load_compare_sections(self):
        path1 = self.file1_var.get()
        path2 = self.file2_var.get()
        if not path1 or not path2:
            messagebox.showwarning('Missing files', 'Please select both files first')
            return
        try:
            sections1, _ = parser.parse_calib(path1)
            sections2, _ = parser.parse_calib(path2)
            # Get common sections
            common = sorted(set(sections1.keys()) & set(sections2.keys()))
            if not common:
                messagebox.showwarning('No common sections', 'The files have no sections in common')
                return
            self.compare_section_combo['values'] = common
            if common:
                self.compare_section_combo.current(0)
            messagebox.showinfo('Loaded', f'Found {len(common)} common GainTable section(s)')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to load sections: {e}')

    def compare_and_plot(self):
        path1 = self.file1_var.get()
        path2 = self.file2_var.get()
        section_id = self.compare_section_var.get()
        
        if not path1 or not path2:
            messagebox.showwarning('Missing files', 'Please select both files')
            return
        if not section_id:
            messagebox.showwarning('No section', 'Please select a section')
            return
        
        try:
            self.compare_result, messages = compare.compare_files(path1, path2, section_id)
            if self.compare_result is None:
                messagebox.showwarning('Comparison failed', '\n'.join(messages))
                return
            messagebox.showinfo('Comparison', '\n'.join(messages))
            compare.plot_comparison(self.compare_result)
        except Exception as e:
            messagebox.showerror('Error', f'Failed to compare: {e}')

    def show_compare_stats(self):
        if not self.compare_result:
            messagebox.showwarning('No comparison', 'Run comparison first')
            return
        
        result = self.compare_result
        stats_text = f"""
File 1: {result['file1_name']}
File 2: {result['file2_name']}
Section: {self.compare_section_var.get()}
---
Number of frequency points compared: {result['num_points']}
Mean difference (File2 - File1): {result['mean_diff']:.4f} dB
Max absolute difference: {result['max_diff']:.4f} dB
Min amplitude (File 1): {min(result['amplitudes_file1']):.4f} dB
Max amplitude (File 1): {max(result['amplitudes_file1']):.4f} dB
Min amplitude (File 2): {min(result['amplitudes_file2']):.4f} dB
Max amplitude (File 2): {max(result['amplitudes_file2']):.4f} dB
"""
        self.compare_txt.delete('1.0', tk.END)
        self.compare_txt.insert(tk.END, stats_text)


def main():
    import sys
    root = tk.Tk()
    initial_file = sys.argv[1] if len(sys.argv) > 1 else None
    app = CalibApp(root, initial_file)
    root.mainloop()


if __name__ == '__main__':
    main()
