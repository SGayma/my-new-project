"""File comparison utilities for calibration files."""
from typing import Dict, List, Tuple
from src import parser


def compare_files(
    path1: str,
    path2: str,
    section_id: str
) -> Tuple[Dict[str, any], List[str]]:
    """Compare two calibration files in a specific section.
    
    Args:
        path1: Path to first .calib file
        path2: Path to second .calib file
        section_id: The GainTable section to compare
    
    Returns:
        Tuple of (comparison_dict, messages)
        comparison_dict contains:
        - frequencies: list of frequencies (Hz)
        - amplitudes_file1: list of amplitudes from file 1
        - amplitudes_file2: list of amplitudes from file 2
        - difference: list of differences (file2 - file1)
        - file1_name: basename of file 1
        - file2_name: basename of file 2
    """
    import os
    
    sections1, _ = parser.parse_calib(path1)
    sections2, _ = parser.parse_calib(path2)
    
    messages = []
    
    if section_id not in sections1:
        messages.append(f"Section '{section_id}' not found in file 1")
        return None, messages
    if section_id not in sections2:
        messages.append(f"Section '{section_id}' not found in file 2")
        return None, messages
    
    entries1 = sections1[section_id]
    entries2 = sections2[section_id]
    
    if not entries1 or not entries2:
        messages.append("One or both sections have no data entries")
        return None, messages
    
    # Sort by frequency
    entries1 = sorted(entries1, key=lambda x: x[1])
    entries2 = sorted(entries2, key=lambda x: x[1])
    
    # Match frequencies
    freqs1 = {freq: amp for _, freq, amp in entries1}
    freqs2 = {freq: amp for _, freq, amp in entries2}
    
    # Find common frequencies
    common_freqs = sorted(set(freqs1.keys()) & set(freqs2.keys()))
    
    if not common_freqs:
        messages.append("No common frequencies between files")
        return None, messages
    
    amps1 = [freqs1[f] for f in common_freqs]
    amps2 = [freqs2[f] for f in common_freqs]
    diff = [a2 - a1 for a1, a2 in zip(amps1, amps2)]
    
    result = {
        'frequencies': common_freqs,
        'amplitudes_file1': amps1,
        'amplitudes_file2': amps2,
        'difference': diff,
        'file1_name': os.path.basename(path1),
        'file2_name': os.path.basename(path2),
        'num_points': len(common_freqs),
        'mean_diff': sum(diff) / len(diff),
        'max_diff': max(abs(d) for d in diff),
    }
    
    messages.append(f"Compared {len(common_freqs)} frequency points")
    
    return result, messages


def plot_comparison(comparison_dict: Dict) -> None:
    """Plot comparison of two files.
    
    Args:
        comparison_dict: Result from compare_files()
    """
    import matplotlib.pyplot as plt
    
    if not comparison_dict:
        return
    
    freqs_mhz = [f / 1e6 for f in comparison_dict['frequencies']]
    amps1 = comparison_dict['amplitudes_file1']
    amps2 = comparison_dict['amplitudes_file2']
    diff = comparison_dict['difference']
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 9))
    
    # Top plot: amplitudes overlay
    ax1.plot(freqs_mhz, amps1, 'b-', label=comparison_dict['file1_name'], linewidth=2, alpha=0.7)
    ax1.plot(freqs_mhz, amps2, 'r-', label=comparison_dict['file2_name'], linewidth=2, alpha=0.7)
    ax1.set_ylabel('Amplitude (dB)', fontsize=11)
    ax1.set_title(f'Calibration File Comparison - Amplitude', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # Bottom plot: difference
    ax2.plot(freqs_mhz, diff, 'g-', linewidth=2, alpha=0.8)
    ax2.axhline(y=0, color='k', linestyle='--', alpha=0.3)
    ax2.fill_between(freqs_mhz, 0, diff, alpha=0.2, color='green')
    ax2.set_xlabel('Frequency (MHz)', fontsize=11)
    ax2.set_ylabel('Difference (dB)', fontsize=11)
    ax2.set_title(f'Difference ({comparison_dict["file2_name"]} - {comparison_dict["file1_name"]})', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
