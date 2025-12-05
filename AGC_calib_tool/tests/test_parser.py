"""Test suite for the parser module."""
import os
import sys
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import parser


def test_parse_calib():
    """Test parsing a sample .calib file."""
    # Create a temporary .calib file
    content = """
GainTable "01"
100.0   -20.5
200.0   -18.3

GainTable "02"
300.0   -16.7
400.0   -15.2
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.calib', delete=False) as f:
        f.write(content)
        f.flush()
        path = f.name
    
    try:
        sections, lines = parser.parse_calib(path)
        assert "01" in sections
        assert "02" in sections
        assert len(sections["01"]) == 2
        assert len(sections["02"]) == 2
        # Check values
        _, freq, amp = sections["01"][0]
        assert abs(freq - 100.0) < 0.01
        assert abs(amp - (-20.5)) < 0.01
        print("✓ test_parse_calib passed")
    finally:
        os.unlink(path)


def test_apply_offset():
    """Test applying offset to amplitudes."""
    content = """
GainTable "01"
100.0   -20.5
200.0   -18.3
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.calib', delete=False) as f:
        f.write(content)
        f.flush()
        path = f.name
    
    try:
        sections, lines = parser.parse_calib(path)
        new_lines = parser.apply_offset_to_section(lines, sections, "01", 5.0)
        # Check that amplitudes increased by 5
        new_sections, _ = parser.parse_calib(path)
        # reparse from new_lines directly
        test_content = ''.join(new_lines)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.calib', delete=False) as f2:
            f2.write(test_content)
            f2.flush()
            path2 = f2.name
        new_sections, _ = parser.parse_calib(path2)
        os.unlink(path2)
        
        _, freq, new_amp = new_sections["01"][0]
        assert abs(new_amp - (-15.5)) < 0.01, f"Expected -15.5, got {new_amp}"
        print("✓ test_apply_offset passed")
    finally:
        os.unlink(path)


def test_save_with_suffix():
    """Test saving file with suffix."""
    content = """
GainTable "01"
100.0   -20.5
"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.calib', delete=False) as f:
        f.write(content)
        f.flush()
        path = f.name
    
    try:
        sections, lines = parser.parse_calib(path)
        new_path = parser.save_with_suffix(path, lines, "test_suffix")
        assert os.path.exists(new_path)
        assert "test_suffix" in new_path
        os.unlink(new_path)
        print("✓ test_save_with_suffix passed")
    finally:
        os.unlink(path)


if __name__ == '__main__':
    test_parse_calib()
    test_apply_offset()
    test_save_with_suffix()
    print("\nAll tests passed!")
