# Log Analyzer - Wave Studio Application Log Tool

A powerful Windows desktop application for analyzing `application.log` files from Wave Studio with real-time monitoring, advanced filtering, and command timing analysis.

## Features

### 1. **Log Viewer Tab**
- Load `application.log*` files from Wave Studio
- View complete log content with file size and line count
- **Multiple filter types:**
  - **Keyword Search**: Simple text matching (case-sensitive option)
  - **Errors**: Automatically highlights error, exception, failed, critical messages
  - **Warnings**: Automatically highlights warning and deprecated messages
  - **Commands**: Highlights command, execute, invoke operations
  - **Timing**: Highlights timing-related entries
  - **Custom Regex**: Use custom regular expressions for advanced filtering
- Real-time highlighting of matched text
- Case-sensitive/insensitive search toggle
- Auto-refresh filtering as you type

### 2. **Command Timing Tab**
- Analyze time spent between commands
- Extract timestamps from log entries
- Display command occurrence analysis
- Configure custom command pattern (regex)
- Export timing analysis results to text file
- Shows:
  - Total log lines and entries with timestamps
  - Number of commands found
  - Time intervals between consecutive entries
  - List of all detected commands

### 3. **Real-Time Monitor Tab**
- Live monitoring of log file changes
- Auto-refresh with configurable interval (0.5-10 seconds)
- Watch log file path from Wave Studio installation
- Start/stop monitoring with single button
- Visual indication of new lines added
- Status indicator showing monitoring state
- Perfect for monitoring active application sessions

## Installation & Usage

### Prerequisites
- Python 3.7+
- tkinter (usually included with Python)

### Running from Source

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the log analyzer:
   ```bash
   python log_analyzer_main.py
   ```

   Or use the batch file:
   ```
   launch_log_analyzer.bat
   ```

### Building Standalone Executable

1. Ensure PyInstaller is installed:
   ```bash
   pip install pyinstaller
   ```

2. Build the executable:
   ```powershell
   .\build_log_analyzer.ps1
   ```

   Or manually:
   ```bash
   pyinstaller LogAnalyzer.spec --noconfirm
   ```

3. The executable will be located at:
   ```
   dist/LogAnalyzer/LogAnalyzer.exe
   ```

## How to Use

### Filtering Logs

1. **Open Log Viewer tab**
2. Click "Load Log File" and select an `application.log*` file from `C:\ProgramData\MVG\Wave Studio`
3. Choose a **Filter Type** from dropdown:
   - For quick searches, select "Keyword Search" and type your term
   - For predefined patterns, select "Errors", "Warnings", "Commands", or "Timing"
   - For advanced filtering, select "Custom Regex" and enter regex pattern
4. Matching lines appear with yellow highlights
5. Use "Clear" button to show all lines again

### Analyzing Command Timing

1. **Open Command Timing tab**
2. (Optional) Modify the "Command Pattern" regex if needed
3. Click "Analyze Timings" to extract and analyze timing data
4. View results showing timestamps and command occurrences
5. Click "Export Results" to save analysis to a text file

### Real-Time Monitoring

1. **Open Real-Time Monitor tab**
2. Enter the path to the log file (or browse to select)
3. Set desired refresh rate (in seconds)
4. Click "Start Monitoring"
5. New lines appear with green highlight as they're written to the log
6. Click "Stop Monitoring" to end monitoring

## Filter Type Suggestions

| Filter Type | Use Case | Pattern |
|---|---|---|
| Keyword Search | Find specific text | Plain text match |
| Errors | Troubleshoot failures | `(?i)(error\|failed\|exception\|critical)` |
| Warnings | Check deprecations | `(?i)(warning\|warn\|deprecated)` |
| Commands | Track operations | `(?i)(command\|cmd\|execute\|invoke)` |
| Timing | Performance analysis | `(?i)(time\|duration\|elapsed\|ms\|sec)` |
| Custom Regex | Advanced filtering | Your regex pattern |

## File Locations

- **Default log directory**: `C:\workspace\WS_Logs_Analyzer`
- **Log files pattern**: `application.log*` (e.g., `application.log`, `application.log.1`)

## Keyboard Shortcuts

- **Clear Filter**: Click the "Clear" button
- **Search**: Type in the search field (auto-updates)
- **Case Sensitive**: Toggle checkbox to enable case-sensitive search

## Troubleshooting

### "Invalid file path" error
- Ensure the log file path exists and is readable
- Check that Wave Studio has permissions to write to the log directory

### Regex errors
- Check your regex pattern in the status message
- Common regex metacharacters: `.` `*` `+` `?` `[` `]` `|` `(` `)`

### Monitoring not updating
- Check the refresh rate isn't too high
- Verify the log file is being actively written to
- Try increasing the refresh interval if experiencing performance issues

### Executable won't run
- Ensure Python 3.7+ is installed on the target machine
- Run from command line to see error messages
- Check that all dependencies are available

## Architecture

```
LogAnalyzer/
├── log_analyzer_main.py      # Entry point for executable
├── src/
│   └── log_analyzer.py       # Main application class with 3 tabs
├── LogAnalyzer.spec          # PyInstaller configuration
├── build_log_analyzer.ps1    # Build script
└── launch_log_analyzer.bat   # Quick launch script
```

## Advanced Usage

### Custom Command Pattern
You can define custom regex patterns in the Command Timing tab. Examples:
- `(?i)MSG:` - Find message lines
- `ERROR:\s*\d+` - Find error codes
- `\[\d{2}:\d{2}:\d{2}\]` - Extract timed entries

### Combining Filters
Run analysis multiple times with different patterns to cross-reference data.

## Performance Tips

- For large log files (>100MB), use filters to reduce displayed lines
- Adjust real-time monitoring refresh rate based on system performance
- Close other applications when monitoring for better responsiveness

## Support & Feedback

For issues or feature requests, check the application logs and error messages for debugging information.

---

**Version**: 1.0  
**Platform**: Windows  
**Python**: 3.7+
