import re
from typing import List, Dict, Tuple, Any

number_re = re.compile(r'([+-]?(?:\d+\.\d*|\d*\.\d+|\d+)(?:[eE][+-]?\d+)?)')
# Handle both formats: GainTable "name" and "GainTable ""name"""
gain_header_re = re.compile(r'["\s]*GainTable\s*["\s]*([^"]+(?:""[^"]*)*[^"]*)')


def read_lines(path: str) -> List[str]:
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        return f.readlines()


def parse_calib(path: str) -> Tuple[Dict[str, List[Tuple[int, float, float]]], List[str]]:
    """Parse a .calib file.

    Returns (sections, lines)
    sections: dict mapping GainTable id -> list of tuples (line_idx, freq, amp)
    lines: full file lines as list
    """
    lines = read_lines(path)
    sections: Dict[str, List[Tuple[int, float, float]]] = {}
    current = None
    
    for i, line in enumerate(lines):
        # Check for GainTable header - handle multiple formats:
        # Format 1: "GainTable ""name""" (old format with leading quote)
        # Format 2: GainTable "name" (new format without leading quote)
        
        if 'GainTable' in line:
            # Try format 1: "GainTable ""name"""
            match = re.search(r'"GainTable\s+""([^"]+)""', line)
            if match:
                current = match.group(1).strip()
                sections.setdefault(current, [])
                continue
            
            # Try format 2: GainTable "name"
            match = re.search(r'GainTable\s+"([^"]+)"', line)
            if match:
                current = match.group(1).strip()
                sections.setdefault(current, [])
                continue
        
        if current is None:
            continue
        
        # Skip lines that are braces or metadata
        if line.strip() in ['{', '}']:
            continue
        
        # find first two numbers on the line
        nums = number_re.findall(line)
        if len(nums) >= 2:
            try:
                freq = float(nums[0])
                amp = float(nums[1])
            except ValueError:
                continue
            sections[current].append((i, freq, amp))
    
    return sections, lines


def format_amp_like(original: str, new_amp: float) -> str:
    """Format new_amp trying to mimic original formatting."""
    if 'e' in original or 'E' in original:
        return f"{new_amp:.6e}"
    if '.' in original:
        dec = len(original.split('.')[-1].rstrip())
        try:
            dec = max(0, dec)
            fmt = f"{{:.{dec}f}}"
            return fmt.format(new_amp)
        except Exception:
            return f"{new_amp:.6f}"
    # original was integer-like
    if abs(new_amp - int(new_amp)) < 1e-9:
        return str(int(new_amp))
    return f"{new_amp:.6f}"


def replace_amp_in_line(line: str, new_amp: float) -> str:
    """Replace the second numeric token in the line with new_amp formatted."""
    matches = list(number_re.finditer(line))
    if len(matches) < 2:
        return line
    amp_span = matches[1].span()
    orig_amp = matches[1].group(1)
    new_amp_str = format_amp_like(orig_amp, new_amp)
    new_line = line[:amp_span[0]] + new_amp_str + line[amp_span[1]:]
    return new_line


def apply_offset_to_section(lines: List[str], sections: Dict[str, List[Tuple[int, float, float]]], section_id: str, offset: float) -> List[str]:
    new_lines = list(lines)
    entries = sections.get(section_id, [])
    for idx, freq, amp in entries:
        new_amp = amp + offset
        new_lines[idx] = replace_amp_in_line(new_lines[idx], new_amp)
    return new_lines


def save_with_suffix(original_path: str, new_lines: List[str], suffix: str) -> str:
    import os
    base, ext = os.path.splitext(original_path)
    new_path = f"{base}.{suffix}{ext}"
    with open(new_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    return new_path
