"""Test comparison feature with real file."""
from src import compare, parser

path = r"c:\DATA\clients\Toyota\Active gain calibration of 'SG3000F Master' (2025-11-21 09h52).calib"

# Load the file to see available sections
sections, _ = parser.parse_calib(path)
print(f"[OK] Loaded {len(sections)} sections from real file")
print(f"[OK] Available sections: {', '.join(sorted(sections.keys())[:3])}...")

# Test comparing the file with itself (should show no difference)
section_id = sorted(sections.keys())[0]
result, messages = compare.compare_files(path, path, section_id)

if result:
    print(f"[OK] Comparison successful")
    print(f"[OK] {messages[0]}")
    print(f"[OK] Mean difference: {result['mean_diff']:.6f} dB (should be near 0)")
    print(f"[OK] Max difference: {result['max_diff']:.6f} dB (should be near 0)")
else:
    print(f"[ERROR] Comparison failed: {messages}")
