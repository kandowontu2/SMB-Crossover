"""Admit exposed coin bricks in Prince's existing physical support check."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
from unittest.mock import patch

from check_prince_wall_sweep_1110_v6 import assemble
import prince_cold_packet_1111 as Packet
import replay_prince_koopa_1111 as Replay


BASE_SOURCE = Packet.R / 'tools/reference/prince_logical_support_1110_v8.s'
START, END = 0xd6d1, 0xd756


def change_once(source, old, new):
    assert source.count(old) == 1, old
    return source.replace(old, new)


def support_workers():
    source = BASE_SOURCE.read_text(encoding='utf-8').split('.segment "SUPPORT"\n', 1)[1]
    source = source.split('.segment "PROJECTION"', 1)[0]
    imports = {'LogicalSupport': 0xbd82}
    old, _ = assemble(source, START, imports)
    # Both successful action compares leave carry set. A stays equal to the
    # current sole after CMP, so neither repeated setup is needed.
    source = change_once(source, ' lda $c618\n clc\n adc #1\n', ' lda $c618\n adc #0\n')
    source = change_once(source, ' cmp $c084\n bne Logical\n lda $c084\n',
                         ' cmp $c084\n bne Logical\n')
    # The read still requires genuine native solidity and a clear cell above.
    source = change_once(source, ' and #$fc\n cmp #$10\n bne Empty\n dec $b36b\n',
                         ' cmp #$58\n beq Exposed\n and #$fc\n cmp #$10\n bne Empty\n'
                         'Exposed:\n dec $b36b\n')
    new, labels = assemble(source, START, imports)
    assert len(old) == len(new) == END - START
    return old, new, labels


def replace_worker(image, old, new):
    left, right = START - 0xc800, END - 0xc800

    def mutate(runtime, metadata, state):
        assert metadata[left:right] == old
        metadata[left:right] = new
        return runtime, metadata, state

    return Packet.rebuild(image, mutate)


def proposal(parent):
    assert sha256(parent).hexdigest() == Replay.PIN
    old, new, _ = support_workers()
    return replace_worker(parent, old, new)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--koopa-mode', choices=('runway', 'ledge', 'step'), default='runway')
    args = parser.parse_args()
    output = args.output.resolve()
    assert output == Packet.R / 'build/prince-brick-fixed-1111' and not output.exists()
    image, layout = proposal(Replay.NIGHTLY.read_bytes())
    expected = sha256(image).hexdigest()
    print('PRINCE_BRICK_ROM ' + json.dumps(dict(ROM_SHA256=expected, **layout)), flush=True)
    output.mkdir()
    rom = output / 'candidate.nes'
    rom.write_bytes(image)
    with patch.object(sys, 'argv', [Replay.__file__, '--output', str(output), '--rom', str(rom),
                       '--expected', expected, '--cookie', layout['cookie'], '--koopa-mode', args.koopa_mode]):
        Replay.main()


if __name__ == '__main__':
    main()
