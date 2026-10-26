"""Prepare an uninstalled, artwork-preserving body-order trial from frozen50b5."""
from pathlib import Path
import argparse
import difflib
import hashlib
import json
import shutil
import subprocess
import sys
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location

ROOT = Path(__file__).resolve().parents[2]
SHA = '50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

INSERT = '''                # Prioritize the native colored core under the eight-sprite
                # limit. Source records emit in reverse; all opaque planes are
                # disjoint, so unlimited pixel colors and CHR remain exact.
                def opaque_count(part):
                    tile=part[0]
                    data=pool[(tile//2) if not(tile&1) else 32+(tile-0x81)//2]
                    return sum((data[row]|data[row+8]).bit_count()
                               for row in list(range(8))+list(range(16,24)))
                for frame in bodies:
                    hardware=list(reversed(records[frame]))
                    hardware.sort(key=lambda part:(part[1]&3!=0,-opaque_count(part)))
                    records[frame]=list(reversed(hardware))
'''


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--compiler', type=Path, required=True)
    p.add_argument('--verify-existing', action='store_true', help='Finish read-only verification after the retained symbol-check harness error')
    a = p.parse_args()
    assert not a.output.resolve().is_relative_to(ROOT)
    assert sha(a.base / 'baseline-rebuild-v2/candidate.nes') == SHA
    source = a.output / 'source'
    if not a.verify_existing:
        a.output.mkdir(parents=True, exist_ok=False)
        shutil.copytree(a.base / 'baseline-source-v2', source)
    else:
        assert (a.output / 'preparation-tool-before-symbol-check-repair.py').is_file()
        assert (a.output / 'candidate.nes').is_file()
    baseline_source = a.base / 'baseline-source-v2'
    before_files = {q.relative_to(baseline_source).as_posix(): sha(q) for q in baseline_source.rglob('*') if q.is_file()}
    generator = source / 'tools/reference/prepare_parodius_art.py'
    if not a.verify_existing:
        raw = generator.read_bytes()
        anchor = b'                records.update(pickup_records)'
        assert raw.count(anchor) == 1 and b'\r\n' not in raw
        generator.write_bytes(raw.replace(anchor, INSERT.encode() + anchor))
        result = subprocess.run([sys.executable, '-B', str(generator)], capture_output=True, text=True)
        (a.output / 'regenerate.log').write_text(result.stdout + result.stderr)
        assert result.returncode == 0, result.stderr
    changed = {n: sha(source / n) for n, v in before_files.items() if sha(source / n) != v}
    assert set(changed) == {'tools/reference/prepare_parodius_art.py', 'src/parodius_art.inc',
                            'reference/parodius-nes/art/packed/manifest.json'}, changed
    old_manifest = json.loads((a.base / 'baseline-source-v2/reference/parodius-nes/art/packed/manifest.json').read_text())
    new_manifest = json.loads((source / 'reference/parodius-nes/art/packed/manifest.json').read_text())
    records = []
    for old_pool, new_pool in zip(old_manifest['pools'], new_manifest['pools'], strict=True):
        old_rest, new_rest = dict(old_pool), dict(new_pool)
        old_records, new_records = old_rest.pop('records'), new_rest.pop('records')
        assert old_rest == new_rest
        for f, old_parts in old_records.items():
            new_parts = new_records[f]
            assert sorted(old_parts) == sorted(new_parts)
            if int(f) not in old_pool['body_frames']:
                assert old_parts == new_parts
            if old_parts != new_parts:
                records.append(dict(pool=old_pool['index'], frame=int(f), parts=len(old_parts)))
    rom = a.output / 'candidate.nes'
    cmd = [sys.executable, '-B', str(source / 'tools/build_mmc5_expanded.py'),
           '--workspace', str(source), '--source-overlay', str(source),
           '--compiler', str(a.compiler), '--output', str(rom)]
    if not a.verify_existing:
        result = subprocess.run(cmd, capture_output=True, text=True)
        (a.output / 'build-host.log').write_text(result.stdout + result.stderr)
        assert result.returncode == 0, result.stdout + result.stderr
    old = scoped_load(a.base / 'baseline-rebuild-v2/candidate.nes')
    new = scoped_load(rom)
    for name in old['syms']:
        assert address(old, name) == address(new, name), name
        symbol = old['syms'][name]
        if 'seg' in symbol and 'ooffs' in old['segs'][symbol['seg']]:
            assert location(old, name) == location(new, name), name
    before = old['raw']; after = new['raw']
    assert len(before) == len(after) and before[1048592:] == after[1048592:]
    aliases = json.loads((a.base / 'record-aliases.json').read_text())['all_records']
    allowed = set()
    for key, refs in aliases.items():
        if not any(row['body'] for row in refs):
            continue
        assert all(row['body'] for row in refs), ('body/nonbody alias', key)
        bank, ptr = map(int, key.split(':'))
        start = 16 + bank * 8192 + ptr % 8192
        size = before[start]
        assert size == after[start] and size % 4 == 0
        old_parts = [tuple(before[i:i+4]) for i in range(start+1, start+size+1, 4)]
        new_parts = [tuple(after[i:i+4]) for i in range(start+1, start+size+1, 4)]
        assert sorted(old_parts) == sorted(new_parts)
        allowed.update(range(start+1, start+size+1))
    delta = [i for i, (x, y) in enumerate(zip(before, after)) if x != y]
    assert set(delta) <= allowed
    patch = []
    for name in changed:
        patch += difflib.unified_diff((a.base / 'baseline-source-v2' / name).read_text().splitlines(True),
                                     (source / name).read_text().splitlines(True),
                                     fromfile='a/'+name, tofile='b/'+name)
    (a.output / 'review.patch').write_text(''.join(patch))
    proof = dict(prepared=True, adopted=False, native_run=False, goal_complete=False,
                 baseline_ROM_sha256=SHA, candidate_ROM_sha256=sha(rom), changed_source=changed,
                 tool_sha256=sha(Path(__file__)), compiler_sha256=sha(a.compiler),
                 existing_symbols_exact=len(old['syms']), all_old_addresses_exact=True,
                 CHR_exact=True, body_only_record_permutations=True,
                 no_body_nonbody_alias=True, changed_body_records=records,
                 changed_ROM_bytes=len(delta), changed_banks=sorted({(i-16)//8192 for i in delta}),
                 verification_harness_repair='The first verifier incorrectly requested ROM offsets for absolute constants/RAM symbols; original tool and successful build retained. All symbol addresses and all file-backed symbol offsets are now checked separately.',
                 scope='Source-only body-order candidate. Complete pixel/color, native fair '
                       'visibility, edge clipping and cadence qualification remain required.')
    (a.output / 'proof.json').write_text(json.dumps(proof, indent=2)+'\n')
    print(json.dumps({k: v for k, v in proof.items() if k != 'changed_body_records'}))


if __name__ == '__main__':
    main()
