"""Rebase Prince's qualified body and menu patches onto the installed nightly."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

from prepare_selected_native_packet_v1 import R, prepare, sha


CURRENT = '244734bbc2690b4e97e654cc72f8f153bedbe3fcc799f714e9508784e4f33af4'
LEGACY = '199d89a4a1c7747946154b5f6c5b079f90b9292aff0831a49cbb4303a130820a'
NIGHTLY = Path.home()/'Downloads/SMB-Crossover-Latest-WIP-MMC5.nes'
BODY = R/'build/prince-body-current-candidate-root-1103-v186'
HOP = R/'build/prince-source-hop-root-1103-v189/controller.lua'
FIRST_PIPE = R/'build/prince-first-pipe-1103-v193/native/controller.lua'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--landing', type=Path)
    parser.add_argument('--jump-gap', type=int, default=96)
    args = parser.parse_args()
    output = args.output.resolve()
    manifest = BODY/'candidate.json'
    proof = json.loads(manifest.read_text())
    previous = Path(proof['candidate'])
    assert proof['passed'] and proof['candidate_SHA256'] == sha(previous) == LEGACY
    original = NIGHTLY.read_bytes()
    assert hashlib.sha256(original).hexdigest() == CURRENT
    legacy = previous.read_bytes()
    raw = bytearray(original)
    modified = set()

    def patch(offset, before, after):
        assert len(before) == len(after) and raw[offset:offset+len(before)] == before, hex(offset)
        addresses = set(range(offset, offset+len(before)))
        assert not modified.intersection(addresses), hex(offset)
        raw[offset:offset+len(after)] = after
        modified.update(addresses)

    assert len(proof['patches']) == 54
    for row in proof['patches']:
        offset = row['file_offset']
        after = bytes.fromhex(row['new_hex'])
        assert legacy[offset:offset+len(after)] == after
        patch(offset, bytes.fromhex(row['old_hex']), after)

    refs = [Path(__file__), manifest]
    if args.landing:
        landing = json.loads(args.landing.read_text())
        assert landing['passed'] and landing['parent_SHA256'] == CURRENT
        for row in landing['patches']:
            patch(row['offset'], bytes.fromhex(row['preimage']), bytes.fromhex(row['replacement']))
        refs.append(args.landing)

    mini_begin = 1048592+962*1024
    mini_end = 1048592+969*1024
    assert raw[mini_begin:mini_end] == original[mini_begin:mini_end]
    assert all(old == new or i in modified for i, (old,new) in enumerate(zip(original,raw)))
    output.mkdir()
    rom = output/'prince-current.nes'
    rom.write_bytes(raw)
    for ext in ('.lbl','.dbg'):
        shutil.copyfile(previous.with_suffix(ext), rom.with_suffix(ext))
    pin = sha(rom)
    (output/'candidate.json').write_text(json.dumps(dict(
        candidate_SHA256=pin, parent_SHA256=CURRENT, old_prince_SHA256=LEGACY,
        body_frontend_spans=54, landing=bool(args.landing),
        changed_bytes=sum(old != new for old,new in zip(original,raw)),
        Mini_code_metadata_atlas_exact=True), indent=2)+'\n')
    for name, source in [('hop',HOP),('first-pipe',FIRST_PIPE)]:
        controller = source.read_text()
        assert controller.count(LEGACY) == 1
        if name == 'first-pipe' and args.jump_gap != 96:
            assert 60 <= args.jump_gap <= 180
            assert controller.count('enemy.gap<=96') == 1
            controller = controller.replace('enemy.gap<=96', f'enemy.gap<={args.jump_gap}')
        prepare(output/name, rom, controller.replace(LEGACY,pin), [*refs,source],
                expected=pin, timeout=150, allow_interactive=True,
                scope='Controller-only Prince '+name+' replay rebased to the current nightly.')


if __name__ == '__main__':
    main()
