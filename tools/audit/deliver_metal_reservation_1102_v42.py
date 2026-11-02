"""Publish the tested Metal successor directly, then prepare actual Downloads QA."""
import json
import re
from pathlib import Path
from prepare_selected_native_packet_v1 import R, prepare, sha
from nightly_patch_guard_v1 import check

O = R / 'build/metal-reservation-1102-v42'
ROM = O / 'candidate.nes'
DEST = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def main():
    digest = sha(ROM)
    assembly, cpu = read(O / 'assembly.json'), read(O / 'CPU.json')
    assert assembly['ROM_SHA256'] == cpu['ROM_SHA256'] == digest and cpu['passed']
    for q in [assembly, cpu]:
        for path, h in q['bindings'].items():
            assert sha(R / path) == h, path
    results = {}
    for name in ['native', 'route']:
        result = read(O / name / 'capture/result.json')
        binding = read(O / name / 'capture/binding.json')
        ready = read(O / name / 'ready.json')
        assert result['passed'] and binding['exit_code'] == 0 and binding['ROM_sha256'] == digest
        for path, h in ready['bindings'].items():
            assert sha(path) == h, path
        results[name] = result
    assert results['route']['reason'] == 'entered-1-2'
    assert results['route']['lives'] == results['route']['initial_lives'] == 2
    order = read(O / 'native/capture/ordering.json')
    assert order['misaligned'] == {} and order['counts']['reservation'] == 74
    previous = sha(DEST)
    assert previous == assembly['parent_ROM_SHA256']
    before = check(DEST)
    DEST.write_bytes(ROM.read_bytes())
    after = check(DEST)
    assert sha(DEST) == digest
    source = O / 'native/controller.lua'
    labels = {n: int(a, 16) for a, n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',
                                                 ROM.with_suffix('.lbl').read_text(), re.M)}
    prefix = ['L=L or {};B=B or {}'] + [f'L[{json.dumps(n)}]={a}' for n, a in sorted(labels.items())]
    text = '\n'.join(prefix) + '\n' + source.read_text(encoding='utf-8')
    prepare(O / 'downloads', ROM, text, [Path(__file__), DEST, source, O / 'assembly.json',
            O / 'CPU.json', O / 'native/capture/result.json', O / 'route/capture/result.json'],
            expected=digest, timeout=90, allow_interactive=True,
            scope='Actual Downloads ROM cold selection, idle/walk and OAM/header assertions. '
                  'Explicit symbols, same tested bytes, no sidecar patch or backup. '
                  'Full-stage qualification remains bound to the separate exact-hash route.')
    path = O / 'downloads/ready.json'
    ready = read(path)
    ready['ROM'] = str(DEST)
    path.write_text(json.dumps(ready, indent=2) + '\n', encoding='utf-8')
    receipt = dict(installed=True, ROM_sha256=digest, previous_sha256=previous, destination=str(DEST),
                   candidate=str(ROM.relative_to(R)), backup_created=False,
                   downloads_launch_verified=False, before=before, after=after,
                   native_scope='Stable zero header and aligned OAM rotation pass; full1-1 reaches active1-2 '
                                'in5587physicalframes, lives2to2, genuine native defeat. '
                                'Idle120/180 and walk27/40 updates unchanged; palette/HUD/audio remain open.',
                   helpers_added=False, complete=False)
    (O / 'delivery.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(installed=True, SHA256=digest, backups=False, Downloads_launch_pending=True)))


if __name__ == '__main__':
    main()
