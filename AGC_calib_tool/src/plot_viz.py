"""Plotting module for calibration offset visualization."""
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict


def plot_offset_comparison(
    sections: Dict[str, List[Tuple[int, float, float]]],
    section_id: str,
    offset: float
) -> None:
    """Plot frequency vs amplitude before and after offset.
    
    Args:
        sections: Dict of section_id -> [(line_idx, freq, amp), ...]
        section_id: The GainTable section to plot
        offset: The offset value applied
    """
    if section_id not in sections or not sections[section_id]:
        return
    
    entries = sections[section_id]
    frequencies = [freq for _, freq, _ in entries]
    original_amps = [amp for _, _, amp in entries]
    new_amps = [amp + offset for _, _, amp in entries]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Convert frequencies to MHz for readability
    freq_mhz = [f / 1e6 for f in frequencies]
    
    ax.plot(freq_mhz, original_amps, 'b-', label=f'Original', linewidth=2, alpha=0.7)
    ax.plot(freq_mhz, new_amps, 'r-', label=f'After offset (+{offset} dB)', linewidth=2, alpha=0.7)
    
    ax.set_xlabel('Frequency (MHz)', fontsize=11)
    ax.set_ylabel('Amplitude (dB)', fontsize=11)
    ax.set_title(f'Calibration Offset Visualization: {section_id}', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
