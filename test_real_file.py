import sys
from src import parser

path = r"c:\DATA\clients\Toyota\Active gain calibration of 'SG3000F Master' (2025-11-21 09h52).calib"
try:
    sections, lines = parser.parse_calib(path)
    print(f"Total sections: {len(sections)}")
    for name in sorted(sections.keys()):
        count = len(sections[name])
        print(f"  {name}: {count} entries")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
