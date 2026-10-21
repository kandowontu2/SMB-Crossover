"""Build the frozen Samus water-query reorder in an isolated K checkout."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
K = ROOT / 'build/verification/root49-integrated-private-build-k'
PACKET = ROOT / 'build/verification/agent49k-samus-water-order-fix-proposal-a'
OWN = ROOT / 'build/verification/root49k-samus-water-private-build-l'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def labels(p):
    return {a[2]: int(a[1], 16) for line in p.read_text().splitlines()
            if (a := line.split()) and a[0] == 'al'}


def main():
    assert not OWN.exists()
    assert sha(PACKET / 'freeze.json') == 'e77fc6b46be977e2b6a6948fbfac279f9d3bf6f260c718bb3a461ec54117fa44'
    frozen = json.loads((PACKET / 'freeze.json').read_text())
    for n, r in frozen['files'].items():
        assert sha(PACKET / n) == r['sha256']
    contract = json.loads((PACKET / 'contract.json').read_text())
    sys.path.insert(0, str(ROOT / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(ROOT)
    assert used + 120_000_000 < 30_000_000_000
    archive = Path(contract['baseline_source_archive']['path'])
    assert sha(archive) == contract['baseline_source_archive']['sha256']
    OWN.mkdir()
    source = OWN / 'source'
    source.mkdir()
    with zipfile.ZipFile(archive) as z:
        catalog = json.loads(z.read('archived-file-hashes.json'))
        assert len(catalog) == 407
        for n, h in catalog.items():
            part = PurePosixPath(n)
            assert not part.is_absolute() and '..' not in part.parts and '\\' not in n
            data = z.read(n)
            assert hashlib.sha256(data).hexdigest() == h
            target = source / n
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    member = contract['source_members'][0]
    assert member['member'] == 'src/samus.s'
    assert sha(source / member['member']) == member['baseline']['sha256']
    replacement = Path(member['replacement']['path'])
    assert sha(replacement) == member['replacement']['sha256']
    (source / member['member']).write_bytes(replacement.read_bytes())
    catalog[member['member']] = sha(replacement)
    out_archive = OWN / 'source-water-l.zip'
    with zipfile.ZipFile(out_archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for n in sorted(catalog):
            z.writestr(n, (source / n).read_bytes())
        z.writestr('archived-file-hashes.json', json.dumps(catalog, indent=2) + '\n')
    shutil.copytree(ROOT / 'tools/Windows/cc65', source / 'tools/Windows/cc65')
    sys.path.insert(0, str(ROOT / 'build/verification/agent49k-samus-water-up-direction-component-a'))
    from image import Image
    report = dict(status='building-private-only', source407_hashes=catalog, source_archive_sha256=sha(out_archive),
                  proposal_sha256=sha(PACKET / 'freeze.json'), parent_report_sha256=sha(K / 'report.json'),
                  script_sha256=sha(Path(__file__)), workspace_before_bytes=used, cases=[], goal_complete=False)
    def save():
        (OWN / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    for mapper, number in [('mmc3', 4), ('mmc5', 5)]:
        with (OWN / f'build-{mapper}.log').open('w', encoding='utf-8') as log:
            done = subprocess.run([sys.executable, 'tools/build.py', '--mapper', mapper], cwd=source, stdout=log, stderr=subprocess.STDOUT)
        row = dict(mapper=mapper, exit=done.returncode)
        report['cases'].append(row)
        save()
        assert done.returncode == 0
        old = K / f'source/build/smb-crossover-{mapper}.nes'
        new = source / f'build/smb-crossover-{mapper}.nes'
        a, b = Image(old), Image(new)
        changes = [i for i, (x, y) in enumerate(zip(a.raw, b.raw)) if x != y]
        assert len(a.raw) == len(b.raw) == 786448
        assert changes and all(16 + 10 * 8192 <= i < 16 + 11 * 8192 for i in changes)
        assert all(labels(new.with_suffix('.lbl')).get(n) == v for n, v in labels(old.with_suffix('.lbl')).items())
        layout = contract['before_layout'][str(number)]
        for n, address in layout['expected_scoped_labels'].items():
            assert b.sym(n, 'SamusMovement')['val'] == address, (mapper, n)
        assert b.sym('DirectionReady', 'SamusMovement')['val'] == layout['expected_new_DirectionReady']
        old_segment = a.segs[a.sym('SamusMovement')['seg']]
        new_segment = b.segs[b.sym('SamusMovement')['seg']]
        assert (old_segment['start'], old_segment['size'], old_segment['ooffs']) == (new_segment['start'], new_segment['size'], new_segment['ooffs'])
        def read(im, start, end):
            seg = im.segs[im.sym('SamusMovement')['seg']]
            offset = seg['ooffs'] + start - seg['start']
            return im.raw[offset:offset + end - start]
        assert read(a, layout['movement_start'], layout['old_query_start']) == read(b, layout['movement_start'], layout['old_query_start'])
        assert list(read(b, layout['expected_new_Direction'], layout['expected_new_DirectionReady'])) == layout['old_query_bytes']
        suffix = layout['expected_unchanged_suffix']
        assert read(a, suffix['start'], suffix['end_exclusive']) == read(b, suffix['start'], suffix['end_exclusive'])
        row.update(ROM_sha256=sha(new), DBG_sha256=sha(new.with_suffix('.dbg')), LBL_sha256=sha(new.with_suffix('.lbl')),
                   changed_ROM_bytes=len(changes), changes_confined_to_SAMUS=True, all_global_labels_exact=True,
                   scoped_labels_match_contract=True, moved23bytes_exact=True, prefix_and_suffix_exact=True,
                   SAMUS_size=new_segment['size'], SAMUS_growth=0, SRAM_growth=0)
        save()
    assert all(sha(source / n) == h for n, h in catalog.items())
    report.update(status='PASS-build-and-layout-only-not-accepted', source407_exact_after=True, workspace_after_bytes=workspace_bytes(ROOT))
    save()
    print(json.dumps({k: v for k, v in report.items() if k != 'source407_hashes'}), flush=True)


if __name__ == '__main__':
    main()
