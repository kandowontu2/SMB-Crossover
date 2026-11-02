"""Time the authentic jump later to clear the second enemy in a pair."""
from pathlib import Path
import argparse
from prepare_selected_native_packet_v1 import R, prepare, sha


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rom', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    a.output.mkdir(exist_ok=True)
    ref = R / 'build/arthur-full11-combat-1102-v12/native/controller.lua'
    text = ref.read_text()
    assert text.count('nearest>38') == 1
    text = text.replace('nearest>38', 'nearest>24', 1)
    prepare(a.output / 'native', a.rom, text, [Path(__file__), ref],
            expected=sha(a.rom), timeout=240, allow_interactive=True,
            scope='Same all4pipes/3gaps/actual1-2/no-life-loss controller, '
                  'but takeoff at24pixel observed enemy distance so the '
                  'authentic66pixel forward flight clears a compact pair. '
                  'Sparse actor log and no emulated writes, cheats, '
                  'physics changes or helper platforms. Earlier negatives retained.')


if __name__ == '__main__':
    main()
