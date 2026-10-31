"""Bind the verified four-frame Peach policy to a source-built successor."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R / 'tools/audit'), str(R / 'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location

P = R / 'build/current74-benj-peach-native-1031-v1/peach'
OLD = 'a12661c1ddad2e15a8ce0589e86b5510703fd390e6346a982b14a6be0b742e3c'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--joint', type=Path, required=True)
    parser.add_argument('--handoff', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    joint, handoff, output = [path.resolve() for path in [args.joint, args.handoff, args.output]]
    assert joint.is_relative_to(R / 'build') and output.is_relative_to(R / 'build')
    assert not output.exists()
    previous = json.loads((P / 'ready.json').read_text())
    source = json.loads(handoff.read_text())
    assert source['passed'] and source['candidate'] == sha(joint / 'candidate.nes')
    for receipt in [previous, source]:
        for path, digest in receipt['bindings'].items():
            assert sha(path) == digest, path
    assert previous['ROM_sha256'] == OLD
    new_hash = source['candidate']
    old, new = [scoped_load(path) for path in [Path(previous['ROM']), joint / 'candidate.nes']]
    for name, length in [('GameLoop', 128), ('BmFresh', 32),
                         ('BmMarioMovement', 32), ('BmNativeMovement', 32)]:
        a, b = location(old, name), location(new, name)
        assert address(old, name) == address(new, name) and a == b, name
        assert old['raw'][a:a+length] == new['raw'][b:b+length], name
    policy = (P / 'controller.lua').read_text()
    assert policy.count(OLD) == 1 and '["colors"]={22,48,39}' in policy
    output.mkdir(parents=True)
    (output / 'controller.lua').write_text(policy.replace(OLD, new_hash), encoding='utf-8', newline='\n')
    (output / 'run.py').write_text((P / 'run.py').read_text(), encoding='utf-8', newline='\n')
    files = [Path(__file__), P / 'ready.json', P / 'controller.lua', P / 'run.py', handoff,
             output / 'controller.lua', output / 'run.py', joint / 'candidate.nes',
             joint / 'candidate.dbg', joint / 'candidate.lbl', R / 'tools/run_mesen.py',
             R / 'tools/audit/capture_budget.py', Path('C:/mesen2/Mesen.exe')]
    receipt = dict(prepared=True, native=False, ROM=str(joint / 'candidate.nes'),
                   ROM_sha256=new_hash, source_handoff_sha256=sha(handoff),
                   host_timeout_seconds=60, run_cap_bytes=536870912, max_files=64, max_PNGs=4,
                   scope='Cold controller-only Peach selection/lives/opening movement on exact successor. No video, RAM writes, full-level or powerup claim.',
                   bindings={str(path.resolve()): sha(path) for path in files})
    (output / 'ready.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(prepared=True, native=False, ready=str(output / 'ready.json'),
                         ready_sha256=sha(output / 'ready.json'), ROM_sha256=new_hash)))


if __name__ == '__main__':
    main()
