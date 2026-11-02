"""Current 33-slot menu audit; retain the earlier frozen 32-slot producer."""
import sys
from pathlib import Path
from prepare_selected_native_packet_v1 import R, sha

def main():
    rom = R / 'build/bub-menu-candidate-1102-v2/combined-event.nes'
    assert sha(rom) == '613b3300b09e530ec920835b95df53f3115d865ed854e273809d4cafa52407ce'
    source = R / 'tools/audit/inventory_playable_menu_1101_v3.py'
    text = source.read_text()
    assert text.count('for slot in range(32):') == 1
    text = text.replace('for slot in range(32):', 'for slot in range(33):')
    text = text.replace('Sonic (Sonic3 reference)', 'Sonic (Master System reference)')
    sys.argv = [str(source), '--rom', str(rom), '--output', str(R / 'build/playable-menu-1102-v4')]
    exec(compile(text, str(source), 'exec'), {'__name__': '__main__', '__file__': str(source)})

if __name__ == '__main__':
    main()
