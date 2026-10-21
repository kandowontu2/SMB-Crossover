"""Compile the Ryu J and Samus B fixes together without editing shared source."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
G = ROOT / 'build/checkpoints/roster-audit-v49-provisional-g'
J = ROOT / 'build/verification/root49h-coin-private-build-a'
B = ROOT / 'build/verification/root49g-samus-crouch-private-build-b'
PACKET = ROOT / 'build/verification/agent49g-samus-crouch-fix-proposal-b'
OWN = ROOT / 'build/verification/root49-integrated-private-build-k'
digest = lambda data: hashlib.sha256(data).hexdigest()
sha = lambda path: digest(path.read_bytes())


def labels(path):
    return {p[2]: int(p[1], 16) for line in path.read_text().splitlines() if (p := line.split()) and p[0] == 'al'}


def main():
    assert sha(PACKET / 'freeze.json') == 'a1c9668b18804d1791370112a8f04e5f7cbded08e2a6314ff8e1adcea9699c17'
    for row in json.loads((PACKET / 'freeze.json').read_text())['files'].values():
        assert sha(Path(row['path'])) == row['sha256']
    contract = json.loads((PACKET / 'contract.json').read_text())
    jr, br = [json.loads((p / 'report.json').read_text()) for p in (J, B)]
    assert jr['status'] == br['status'] == 'PASS-build-only-not-accepted'
    assert all(sha(J / 'source' / n) == h for n, h in jr['source406_hashes'].items())
    assert all(sha(B / 'source' / n) == h for n, h in br['source405_hashes'].items())
    sys.path.insert(0, str(ROOT / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(ROOT)
    assert used + 120_000_000 <= 30_000_000_000, used
    OWN.mkdir(exist_ok=False)
    fresh = OWN / 'source'
    fresh.mkdir()
    archive = J / 'source-coin-j.zip'
    assert sha(archive) == 'b7171ea8bab6bf2f85c02aac4dd0471c3b965958515e027287ed669e4742c02c'
    with zipfile.ZipFile(archive) as source:
        catalog = json.loads(source.read('archived-file-hashes.json'))
        assert len(catalog) == 406
        for name, expected in catalog.items():
            p = PurePosixPath(name)
            assert not p.is_absolute() and '..' not in p.parts and '\\' not in name
            data = source.read(name)
            assert digest(data) == expected
            dest = fresh / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
    with zipfile.ZipFile(G / 'source-v49.zip') as baseline:
        old_entry = baseline.read('src/entrypoint.s').decode().replace('\r\n', '\n')
        added_entry = Path(contract['materialization']['src/entrypoint.s']['path']).read_text()
        assert added_entry.startswith(old_entry)
        suffix = added_entry[len(old_entry):]
        assert suffix == '\n; New resident gap tails follow every pre-existing contributor.\n.if ::ENABLE_CROSSOVER\n.include "samus_crouch_collision.s"\n.endif\n'
        for name, row in contract['source_members'].items():
            assert digest(baseline.read(name)) == row['sha256']
    for name, row in contract['materialization'].items():
        data = Path(row['path']).read_bytes()
        assert digest(data) == row['sha256']
        if name == 'src/entrypoint.s':
            (fresh / name).write_bytes((fresh / name).read_bytes() + suffix.replace('\n', '\r\n').encode())
        else:
            if name in catalog:
                assert catalog[name] == contract['source_members'][name]['sha256']
            (fresh / name).write_bytes(data)
    expected = {name: sha(fresh / name) for name in set(catalog) | set(contract['materialization'])}
    assert len(expected) == 407
    out_archive = OWN / 'source-integrated-k.zip'
    with zipfile.ZipFile(out_archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as out:
        for name in sorted(expected):
            out.writestr(name, (fresh / name).read_bytes())
        out.writestr('archived-file-hashes.json', json.dumps(expected, indent=2) + '\n')
    shutil.copytree(ROOT / 'tools/Windows/cc65', fresh / 'tools/Windows/cc65')
    report = dict(status='building-integrated-private-proposal', goal_complete=False, source407_hashes=expected,
                  source_archive_sha256=sha(out_archive), parent_reports={p.name: sha(p / 'report.json') for p in (J, B)},
                  script_sha256=sha(Path(__file__)), workspace_before_bytes=used, cases=[],
                  scope='Ryu lower-grapple/coin-membership plus Samus active-crouch geometry. Audio optimization absent; fresh water-form ordering remains open. Not accepted and no traversal claim.')

    def save():
        (OWN / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    save()
    for mapper in ('mmc3', 'mmc5'):
        with (OWN / f'build-{mapper}.log').open('w', encoding='utf-8') as log:
            result = subprocess.run([sys.executable, 'tools/build.py', '--mapper', mapper], cwd=fresh, stdout=log, stderr=subprocess.STDOUT)
        rom = fresh / f'build/smb-crossover-{mapper}.nes'
        row = dict(mapper=mapper, exit=result.returncode, rom_sha256=sha(rom) if rom.is_file() else None)
        report['cases'].append(row)
        save()
        assert result.returncode == 0
        g, j, b, k = [(p / name).read_bytes() for p, name in [(G, rom.name), (J / 'source/build', rom.name), (B / 'source/build', rom.name), (fresh / 'build', rom.name)]]
        assert len(g) == len(j) == len(b) == len(k) == 786448
        j_delta = {i for i, pair in enumerate(zip(g, j)) if pair[0] != pair[1]}
        b_delta = {i for i, pair in enumerate(zip(g, b)) if pair[0] != pair[1]}
        assert len(j_delta) == 361 and len(b_delta) == 99 and not j_delta & b_delta
        predicted = bytearray(g)
        for i in j_delta:
            predicted[i] = j[i]
        for i in b_delta:
            predicted[i] = b[i]
        assert k == predicted, 'Whole integrated ROM must equal exact disjoint compiled changes'
        old_labels = labels((G / rom.name).with_suffix('.lbl'))
        new_labels = labels(rom.with_suffix('.lbl'))
        assert all(new_labels.get(n) == v for n, v in old_labels.items())
        row.update(dbg_sha256=sha(rom.with_suffix('.dbg')), lbl_sha256=sha(rom.with_suffix('.lbl')),
                   compiled_disjoint_union_exact=True, changed_ROM_bytes=460, all_G_labels_preserved=True,
                   SAMUS_bank_exact=g[16 + 10 * 8192:16 + 11 * 8192] == k[16 + 10 * 8192:16 + 11 * 8192])
        assert row['SAMUS_bank_exact']
        save()
    assert all(sha(fresh / n) == h for n, h in expected.items())
    report.update(status='PASS-integrated-build-only-not-accepted', source407_exact_after_build=True, workspace_after_bytes=workspace_bytes(ROOT))
    save()
    print(json.dumps({k: v for k, v in report.items() if k != 'source407_hashes'}), flush=True)


if __name__ == '__main__':
    main()
