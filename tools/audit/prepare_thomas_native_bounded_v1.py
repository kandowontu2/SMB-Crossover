"""Prepare a cold-input native Thomas route using the final linked pose records."""
from pathlib import Path
import argparse
import json
import sys

from prepare_selected_native_packet_v1 import R, prepare, sha
sys.path[:0] = [str(R / 'tools'), str(R / 'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location
from observe_chip_committed_write import lua


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--joint', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    ap.add_argument('--expected', required=True)
    ap.add_argument('--pipes', type=int, choices=[1, 4], default=4)
    args = ap.parse_args()
    joint = args.joint.resolve()
    assert sha(joint / 'candidate.nes') == args.expected
    b = scoped_load(joint / 'candidate.nes')
    raw = b['raw']
    meta = raw[1048592 + 432 * 1024:1048592 + 434 * 1024]
    art = raw[1048592 + 434 * 1024:1048592 + 442 * 1024]
    assert len(meta) == 2048 and len(art) == 8192
    def record(data, at):
        length = data[at]
        assert 0 < length <= 64 and length % 4 == 0
        result = [list(data[i:i + 4]) for i in range(at + 1, at + 1 + length, 4)]
        for row in result:
            for i in [2, 3]:
                if row[i] >= 128:
                    row[i] -= 256
        return result
    records = []
    for i in range(42):
        pointer = meta[1026 + i] | meta[1068 + i] << 8
        assert 0xd000 <= pointer < 0xd402
        records.append(record(meta, pointer - 0xd000))
    idle = record(raw, location(b, 'ThStanding'))
    assert idle == records[0]
    point = address(b, 'GameLoop') + int(b['syms']['GameLoop']['size']) - 1
    assert raw[location(b, 'GameLoop') + int(b['syms']['GameLoop']['size']) - 1] == 0x60
    payload = dict(sha256=args.expected, records=records, idle=idle, chr=list(art),
                   main_return=point, pipes=args.pipes)
    names = ['ThReady', 'ThPoseIndex', 'ThomasState', 'ThNaturalDrawDone',
             'ThMovement', 'ThomasC2AcceptedFrame', 'ThLiftTick']
    prefix = 'THOMAS_ARGS=' + lua(payload) + '\n'
    prefix += ''.join(f'L[{json.dumps(n)}]={address(b, n)}\n' for n in names)
    template = R / 'tools/reference/thomas_native_bounded_v1.lua'
    text = prefix + template.read_text(encoding='utf-8')
    sys.path.insert(0, str(R / 'build/smb2-final62-observer-lua-deps-v1'))
    from lupa.lua54 import LuaRuntime
    ok, error = LuaRuntime(unpack_returned_tuples=True).eval('function(s)local f,e=load(s);return f~=nil,e end')(text)
    assert ok, error
    prepare(args.output, joint / 'candidate.nes', text,
            [Path(__file__), template, joint / 'source-stage.json'],
            expected=args.expected, timeout=180,
            scope='Cold controller-only selection, lives, original attacks, native platforms and pipe crossings. No RAM writes or full1-1/audio/all-powerup claim.')


if __name__ == '__main__':
    main()
