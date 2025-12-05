"""Quick test of plot feature with real file."""
import sys
from src import parser, plot_viz

path = r"c:\DATA\clients\Toyota\Active gain calibration of 'SG3000F Master' (2025-11-21 09h52).calib"
try:
    sections, lines = parser.parse_calib(path)
    print(f"[OK] Loaded {len(sections)} sections")
    
    # Test plotting the first section with an offset
    first_section = sorted(sections.keys())[0]
    offset = 5.0
    print(f"[OK] Creating plot for '{first_section}' with offset {offset} dB...")
    plot_viz.plot_offset_comparison(sections, first_section, offset)
    print("[OK] Plot created successfully!")
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
