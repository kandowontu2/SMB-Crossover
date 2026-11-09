"""Prepare a controller-only replay of the second Goku pipe on exact f205."""

import argparse
import json
from pathlib import Path

from prepare_helper_camera_routes_1110_v1 import once
from prepare_selected_native_packet_v1 import R, prepare, sha


BASE = R / 'build/helper-camera-render-composite-1110'
EXPECTED = 'f2050c1964b53b4bd3dc2e5f24c2ed688d47ad79a8aef6bb2cfd55e28b3e7e42'
POLICY = R / 'tools/reference/goku_pipe_retry_1110.lua'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    prior = BASE / 'goku'
    ready = prior / 'ready.json'
    bindings = json.loads(ready.read_text())
    rom = BASE / 'candidate.nes'
    assert Path(bindings['ROM']) == rom
    assert bindings['ROM_sha256'] == sha(rom) == EXPECTED
    for path, expected in bindings['bindings'].items():
        assert sha(path) == expected, path

    # Bind the exact SavedJoypadBits edge detector and its previous-input store.
    data = rom.read_bytes()
    at = 16 + 86 * 8192 + (0xb33b & 8191)
    assert data[at:at + 19].hex() == 'a5dc4dd95f25dcaabd07b58d165ca5dc8dd95f'
    source = R / 'src/dragon_power_state.inc'
    for declaration in ('DpPrevious=$5fd9', 'DpAction=$5c00', 'DpJumping=$5c0b'):
        assert declaration in source.read_text()

    text = (prior / 'controller.lua').read_text()
    text = once(text, 'local function finish(passed,why)',
                POLICY.read_text() + '\nlocal function finish(passed,why)')
    text = once(text, 'done=true;inputFile:close()',
                'done=true;inputFile:close();writePipeRetry()')
    text = once(text, '  b=choose(c)',
                "  b=choose(c)\n  local retry,failed=secondPipeRetry(c)\n"
                "  if failed then finish(false,'Second pipe retry deadline');return end\n"
                "  if retry then b=retry end")
    prepare(args.output, rom, text, [Path(__file__), POLICY, source, ready,
                                     *(Path(p) for p in bindings['bindings'])],
            expected=EXPECTED, timeout=240, allow_interactive=True,
            scope=bindings['scope'] + ' Second-pipe A release and press wait for the genuine'
                                      ' Dragon Power input latch. Read-only controller and one'
                                      ' bounded retry receipt. Original helper and hardware assertions.')


if __name__ == '__main__':
    main()
