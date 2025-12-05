# AGC Comparison Tool & Offset

A comprehensive GUI tool for managing active gain calibration (.calib) files with two main features:
1. **Compare Files**: Compare two active gain calibration files side-by-side with statistics and visualization
2. **Apply Offset**: Modify amplitude values by a specified offset across selected frequencies

## Features

### Compare Files Tab (First Tab)
- **Load Two Files**: Select two active gain calibration files
- **Auto-detect Common Sections**: Identifies GainTable sections present in both files
- **Compare & Plot**: Visualizes both files on the same graph with difference highlighted
- **Show Stats**: Displays detailed statistics including:
  - Number of frequency points compared
  - Mean and max differences
  - Min/max amplitudes for each file

### Apply Offset Tab (Second Tab)
- **Load & Parse**: Read .calib files and extract GainTable sections
- **Select Section**: Choose a specific GainTable from dropdown
- **Set Offset**: Enter or select an offset value (additive) via combobox
- **Preview**: View the changes in text form before applying
- **Plot**: Visualize frequency vs. amplitude before and after offset (interactive graph)
- **Save**: Apply changes and save to a new file with timestamp
  
### General Features
- **Supports real calibration formats**: Tested with Toyota SG3000F Master calibration files
- **Interactive Plots**: Frequency vs. amplitude graphs with matplotlib

## Quick Start - Windows Executable

The easiest way to use the tool is with the pre-built executable:

```bash
# Run with any .calib file
dist\AGC_Comparison_Tool_Offset.exe

# Or run with a specific file (pre-loads it)
dist\AGC_Comparison_Tool_Offset.exe "path\to\your\file.calib"
```

**For Toyota SG3000F Master calibration file:**

```bash
# Run the batch launcher
launch_Toyota_SG3000F.bat

# Or PowerShell
powershell -ExecutionPolicy Bypass -File launch_Toyota_SG3000F.ps1
```

**Note:** Executable is now ~37 MB (includes matplotlib for plotting)

## File Format

The tool expects `.calib` files with sections like:

```
"GainTable ""TRP correction"""
{
        400000000       -24.78392635
        401000000       -24.73421959
        402000000       -24.57152821
        ...
}

"GainTable ""TIS correction"""
{
        100000000       -20.5
        200000000       -18.3
        ...
}
```

The first number on each data line is the frequency, the second is the amplitude.

## Usage from Source

### Run the GUI

```bash
python -m src.app
python -m src.app "path/to/file.calib"
```

### Run Tests

```bash
python tests/test_parser.py
```

## Installation for Development

No external dependencies are required beyond matplotlib. The tool uses only Python standard library modules for core functionality (tkinter is included with Python).

Install dependencies:

```bash
pip install -r requirements.txt
```

Or separately:

```bash
pip install matplotlib
```

If you want to rebuild the executable or run tests:

```bash
pip install pyinstaller pytest
```

### Rebuild the Executable

```bash
pyinstaller --onefile --windowed --name "CalibOffsetTool" src/app.py
```

## Example Workflow

### Compare Files Tab (First)
1. Click **Browse** for **File 1** and select first calibration file
2. Click **Browse** for **File 2** and select second calibration file
3. Click **Load Sections** to find common GainTable sections
4. Select a **Section** from the dropdown
5. Click **Compare & Plot** to visualize both files and their differences
6. Click **Show Stats** to see detailed comparison statistics

### Apply Offset Tab (Second)
1. Click **Browse** and select your `.calib` file (or use the launcher script)
2. Click **Load & Parse** to extract sections
3. Select a **GainTable** from the dropdown
4. Enter or select an **Offset** value (e.g., 5.0 to add 5 dB)
5. Click **Preview** to see the text changes (or skip to plot)
6. Click **Plot** to visualize the before/after in an interactive graph
7. Click **Apply & Save** to save the modified file

### Output
Modified files are saved with the format:
```
<original_name>.modified_<YYYYMMDD>_offset<value>.calib
```

## Project Structure

```
.
├── dist/
│   └── AGC_Comparison_Tool_Offset.exe    # Windows executable (~37 MB)
├── src/
│   ├── __init__.py
│   ├── parser.py               # File parsing and offset logic
│   ├── plot_viz.py             # Single-file offset visualization
│   ├── compare.py              # Two-file comparison logic
│   └── app.py                  # tkinter GUI with tabs
├── tests/
│   └── test_parser.py          # Unit tests
├── launch_Toyota_SG3000F.bat   # Batch launcher for Toyota file
├── launch_Toyota_SG3000F.ps1   # PowerShell launcher for Toyota file
├── sample.calib                # Example calibration file
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```
