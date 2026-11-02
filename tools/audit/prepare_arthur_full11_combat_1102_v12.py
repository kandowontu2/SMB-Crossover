"""Wait for the actual near enemy before jumping its whole compact group."""
from pathlib import Path
import argparse
from prepare_selected_native_packet_v1 import R, prepare, sha


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rom', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    a.output.mkdir(exist_ok=True)
    ref = R / 'build/arthur-full11-combat-1102-v11/native/controller.lua'
    text = ref.read_text()
    text = text.replace('local shootable=false', 'local shootable=false\n  local nearest=256', 1)
    marker = 'then shootable=true end'
    assert text.count(marker) == 1
    text = text.replace(marker, 'then shootable=true;nearest=math.min(nearest,dx) end', 1)
    marker = 'if age-combatStart<60 then b.right=false;return b end'
    assert text.count(marker) == 1
    text = text.replace(marker, 'if nearest>38 and age-combatStart<240 then b.right=false;return b end', 1)
    prepare(a.output / 'native', a.rom, text, [Path(__file__), ref],
            expected=sha(a.rom), timeout=240, allow_interactive=True,
            scope='Actual-menu full1-1 route with original second-press jump. '
                  'Wait/fire until an observed ground enemy is38pixels ahead '
                  '(240frame cap), then jump the compact enemy group. Same '
                  'all4pipes/3gaps/actual1-2/no-life-loss assertions and sparse '
                  'read-only actor log. No emulated writes, cheats, physics '
                  'changes or helper platforms. Earlier negatives retained.')


if __name__ == '__main__':
    main()
