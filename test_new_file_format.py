"""Test parser with new file format."""
from src import parser

path = r"c:\Users\sgaymay\Downloads\Active gain calibration of 'SG3000F Master' (2025-12-04 15h01).calib"

try:
    sections, lines = parser.parse_calib(path)
    print(f"[OK] Loaded {len(sections)} sections")
    for name in sorted(sections.keys())[:5]:
        count = len(sections[name])
        print(f"  {name}: {count} entries")
    if not sections:
        print("[WARN] No sections parsed!")
        # Show first 50 lines to debug
        print("\nFirst 50 lines:")
        for i, line in enumerate(lines[:50]):
            if 'GainTable' in line:
                print(f"Line {i}: {repr(line)}")
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
