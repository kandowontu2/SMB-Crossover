"""Install the tested combined working build; preserve all prior artifacts."""
from pathlib import Path
import datetime, gzip, hashlib, importlib.util, json, shutil, zipfile

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-combined-cg'
Q = V / 'root49-easy-combined-bq'
C = R / 'build/checkpoints/roster-audit-v49-easy-hard-by'
U = R / 'build/checkpoints/roster-audit-v49-bill-laser-u/manifest.json'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not C.exists()
    pins = {
        U: '4e9e854ddcd78e5c4aa7231fcea81c95fe86d969eb3bab6129bef872a9ddd0d9',
        H / 'report.json': '519570a4a54bd9f588dec8ec621120bb223b7b4df0cd5c6738a34d3719165989',
        Q / 'report.json': '2736ac1e4238d237fce859e18ae29f7ef137ed4b2f386e3078c2a2438021e838',
        Q / 'native/checks-br/report.json': '852f20b705a98a9be45d1d36b01c58bb93d5dd50ea1f9970dd380ce39f46a1ae',
        Q / 'native/checks-bs/report.json': '49509c8e5e016d69a42bfccf1eeb73f4486bd264aa4dfbc5f4faec0897a627af',
        Q / 'native/checks-bt/report.json': 'ee77f76322f30bcdb53bea7cffa89c909e0840b26a0d00b6c961543f1fa00945',
        Q / 'native/checks-bv/report.json': 'b83992d4a1a3af6c304cb66f1b80e1a74b864c944397429df793f6ad025c61c4',
        Q / 'ordinary-pit-profile-bx/report.json': '9be80c77ee7ec2f905caaf099d3e4327e24d257cf7f402c8e453b0422227b8da',
        Q / 'ordinary-mario-cc/report.json': '5550dd20df009cca2ded73a23dc7c10faa7f65520ad77a8ece0bf56898ab2014',
        V / 'root49-bq-bill-rebind-ca/report.json': '1991c81e882fc1b71f2ed119fefb044b795b8d4538f5b1056a2bd3b847a1ee42',
        V / 'root49-bill-freeze-review-cb/report.json': 'e466d2a68d8c05867604a777c4c31f6f752821598c4343ccfc80dea79b177ee0',
        V / 'agent49-bill-advanced-parity-h/freeze-m.json': '74da58b596109108566d706f9083a288f0f360f12c1ea99c5b7ee4e6c15b2252',
        V / 'agent-lsr-ryu-corner-head-e/implementation-freeze.json': 'ac4095308afe1256e708254a2b68423795e889b916b4d89c24fba41b23402878',
    }
    for path, digest in pins.items():
        assert sha(path) == digest, path
    old = json.loads(U.read_text())
    before = old['source_hashes']
    assert len(before) == 412 and all(sha(R / n) == h for n, h in before.items())
    for build in old['builds']:
        assert all(sha(R / a['path']) == a['sha256'] for a in build['artifacts'].values())
    build = json.loads((H / 'report.json').read_text())
    assert build['status'] == 'PASS_CG_BASELINE_FIX_CROSSOVER_ROMS_EXACT_BQ'
    after = build['source_hashes']
    assert len(after) == 440 and not (set(before) - set(after))
    assert all(sha(H / 'source' / n) == h for n, h in after.items())
    assert all(row['passed'] for row in build['builds']) and len(build['builds']) == 4
    for path in [Q / 'native/checks-br/report.json', Q / 'native/checks-bs/report.json', Q / 'native/checks-bt/report.json',
                 Q / 'native/checks-bv/report.json', Q / 'ordinary-pit-profile-bx/report.json',
                 V / 'root49-bq-bill-rebind-ca/report.json']:
        result = json.loads(path.read_text())
        assert result['status'].startswith('PASS')
    mario = json.loads((Q / 'ordinary-mario-cc/report.json').read_text())
    assert len(mario['rows']) == 2 and all(x['passed'] and x['dry_receipts_exact_K']
        and not x['comparison_against_K']['differing_frames'] for x in mario['rows'])
    binary = Q / 'binary-review-bz.json'
    br = json.loads(binary.read_text())
    assert br['status'] == 'PASS' and all(x['all_source_scalar_bytes_exact'] == 32768 for x in br['maps'].values())
    changed = {n: dict(before=before.get(n), after=h, existing_before=sha(R / n) if (R / n).exists() else None)
               for n, h in after.items() if before.get(n) != h}
    # The added pre-existing files are generated reference inventories, kept in
    # the backup even though the old 412-file manifest did not catalog them.
    preexisting_additions = {n for n in after if n not in before and (R / n).exists()}
    assert preexisting_additions == {'docs/reference/expanded-atlas.json', 'docs/reference/lance-assets.json', 'docs/reference/roster-assets.json'}
    C.mkdir(parents=True)
    backup = C / 'before-changed-files.zip'
    with zipfile.ZipFile(backup, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for n in sorted(changed):
            if (R / n).exists():
                z.write(R / n, n)
    refs = list(pins) + [binary, Q / 'binary-adapter-bz.json']
    manifest = dict(status='INSTALLING_TESTED_WORKING_EASY_HARD_BY', utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    publisher_sha256=sha(__file__), before_source_hashes=before, source_changes=changed,
                    backup=dict(path=backup.relative_to(R).as_posix(), sha256=sha(backup)), builds=[],
                    evidence=[dict(path=p.relative_to(R).as_posix(), sha256=sha(p), bytes=p.stat().st_size) for p in refs],
                    behavior=['Source-backed Easy/Hard character movement, injury, pickup and underwater rules from the frozen K through AP ancestry.',
                              'Contra Laser/Flare source art, initial hit/end behavior, source-valid shot counting, cached viewport expiry and fair sprite-family scheduling.',
                              'Scoped Ryu normal-air ceiling correction without additional RAM or side-collision bypass.',
                              'Pit distinct-cell terrain lookup optimization, retaining measured block/reward/projectile/audio observables.',
                              'Baseline-only assembly guards repaired; both tested crossover ROMs remain exact BQ.'],
                    validation_scope='Both mapper builds;4200 Contra source component arenas;168 new Ryu+452 inherited collision cases;11040 Pit terrain cases;20 foreign/bomb groups including222 bombs/map;ordinary3000-frame Pit profiles;Mario Easy full through2-2 bothmaps zero deaths. All independent source/engine rounding qualifications remain in the referenced reports.',
                    outstanding='Full all13 roster routes, every alternate/upgrade, final integrated lossless recordings and frame review remain active. This is an interim working checkpoint.',
                    accepted_release=False, goal_complete=False)
    def save():
        (C / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    save()
    for n in sorted(changed):
        target = R / n
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(H / 'source' / n, target)
    for mapper in ['mmc3', 'mmc5']:
        source = H / 'source/build' / ('smb-crossover-' + mapper + '.nes')
        expected = next(x for x in build['builds'] if x['mapper'] == mapper and not x['baseline'])
        assert sha(source) == expected['ROM_sha256'] and expected['byte_exact_tested_BQ']
        artifacts = {}
        for ext in ['nes', 'lbl', 'map', 'dbg']:
            src, dst = source.with_suffix('.' + ext), R / 'build' / ('smb-crossover-' + mapper + '.' + ext)
            shutil.copyfile(src, dst)
            assert sha(src) == sha(dst)
            artifacts[ext] = dict(path=dst.relative_to(R).as_posix(), sha256=sha(dst), bytes=dst.stat().st_size)
            if ext == 'dbg':
                compressed = gzip.compress(dst.read_bytes(), mtime=0)
                (C / (dst.name + '.gz')).write_bytes(compressed)
                if dst.with_suffix('.dbg.gz').exists():
                    dst.with_suffix('.dbg.gz').write_bytes(compressed)
            else:
                shutil.copyfile(dst, C / dst.name)
        manifest['builds'].append(dict(mapper=mapper, artifacts=artifacts, byte_exact_native_tested_BQ=True))
        save()
    assert all(sha(R / n) == h for n, h in after.items())
    archive = C / 'source-v49-easy-hard-by.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for n in sorted(after):
            z.write(R / n, n)
    manifest.update(status='PASS_WORKING_EASY_HARD_BY_BOTH_MAPPERS', source_hashes=after,
                    source_archive=dict(path=archive.relative_to(R).as_posix(), sha256=sha(archive), bytes=archive.stat().st_size))
    save()
    print(manifest['status'], sha(C / 'manifest.json'), 'changed', len(changed), flush=True)


if __name__ == '__main__':
    main()
