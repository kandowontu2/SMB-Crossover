"""Publish the seven-run verified WWF life-loss repair without a backup."""
import json
import re
from pathlib import Path
from prepare_selected_native_packet_v1 import R, prepare, sha
from nightly_patch_guard_v1 import check

O = R / 'build/wwf-death-1102-v2'
ROM = O / 'candidate.nes'
DEST = Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def main():
    digest = sha(ROM)
    cpu, assembly = read(O / 'CPU.json'), read(O / 'assembly.json')
    assert cpu['passed'] and assembly['ROM_SHA256'] == cpu['ROM_SHA256'] == digest
    for q in [cpu, assembly]:
        for p, h in q['bindings'].items():
            assert sha(R / p) == h, p
    results = {}
    for name in [*[f'contact-{i}' for i in range(6)], 'pit']:
        p = O / 'native-v3' / name
        q, binding, ready = read(p / 'capture/result.json'), read(p / 'capture/binding.json'), read(p / 'ready.json')
        assert q['passed'] and binding['exit_code'] == 0 and binding['ROM_sha256'] == digest
        assert q['initial_lives'] == 2 and q['final_lives'] == 1 and q['engine'] == 8
        for source, h in ready['bindings'].items():
            assert sha(source) == h, source
        results[name] = q
    assert sha(DEST) == assembly['parent_ROM_SHA256']
    before = check(DEST)
    DEST.write_bytes(ROM.read_bytes())
    after = check(DEST)
    assert after['ROM_sha256'] == digest
    source = O / 'native-v3/contact-0/controller.lua'
    labels = {n: int(a, 16) for a, n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$', ROM.with_suffix('.lbl').read_text(), re.M)}
    prefix = ['L=L or {};B=B or {}'] + [f'L[{json.dumps(n)}]={a}' for n, a in sorted(labels.items())]
    prepare(O / 'downloads', ROM, '\n'.join(prefix) + '\n' + source.read_text(encoding='utf-8'),
            [Path(__file__), DEST, source, O / 'assembly.json', O / 'CPU.json'],
            expected=digest, timeout=90, allow_interactive=True,
            scope='Actual Downloads launch, cold Hogan selection, real enemy-contact death, '
                  '168 native ticks, one life lost and active1-1 respawn. No backup/sidecar/state writes; one PNG.')
    p = O / 'downloads/ready.json'
    q = read(p)
    q['ROM'] = str(DEST)
    p.write_text(json.dumps(q, indent=2) + '\n', encoding='utf-8')
    receipt = dict(installed=True, ROM_sha256=digest, previous_sha256=assembly['parent_ROM_SHA256'],
                   destination=str(DEST), candidate=str(ROM.relative_to(R)), backup_created=False,
                   downloads_launch_verified=False, before=before, after=after,
                   native_scope='All6 WWF identities recover from genuine enemy-contact deaths to active1-1. '
                                'Hogan also recovers from a genuine first-pit death after crossing allfourpipes. '
                                'Existing168/150tick native sequence and one life loss. Only3 existing row bytes changed.',
                   helpers_added=False, complete=False)
    (O / 'delivery.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(installed=True, SHA256=digest, backup_created=False, Downloads_pending=True)))


if __name__ == '__main__':
    main()
