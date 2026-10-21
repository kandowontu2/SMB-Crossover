"""Install actual-native-tested DQ as an interim working checkpoint, with backup."""
from pathlib import Path
import datetime
import gzip
import hashlib
import json
import shutil
import sys
import zipfile

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-body-victory-union-dq'
C = R / 'build/checkpoints/roster-audit-v49-body-victory-du'
P = R / 'build/checkpoints/roster-audit-v49-easy-hard-by/manifest.json'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not C.exists()
    pins = {
        P: 'fe005475a409894834268bdd203efde78df0275a124a5d13def3bb6816f098c7',
        H / 'report.json': '40b361bb28db5f1e923c8079d1256bddfd622714ddd46ec44f9110f3039536a7',
        V / 'root49-union-admission-dv.json': 'df27f68df706f7b3a3fed7bb916a4b6e610152e2b201875830a456a2b8863ed7',
        V / 'root49-union-native-dr.json': '2a5410c864e02aae2a0670b7e77462a670c5209fa805b94a7185b9e9c6495abb',
        V / 'root49-victory-review-do.json': 'c859e1e53ce3bc3b443228ae5210b314727c8a7406419bb954f86c8df11a0568',
        V / 'agent49-bill-source-body-f/freeze-m.json': '36910e7b6568bf15c31d59d53326a03ac0ce2007a4f7aae9f437d950e31ccc70',
        V / 'agent49-bill-source-body-f/freeze-o.json': 'c0ee2a77e4bc72442588cc7618b96ce256d3f5aac725e9662c8e1cdef0d16049',
        V / 'agent49-bill-body-dq-rebind-r/freeze-r.json': 'e7d9338d3f8eb7ca3d452a4445d79a8ebc5c533a5e9469dcd64aad88d4ae7126',
        V / 'agent-lsr-victory-repair-c/implementation-freeze.json': '3a1d954e4f279fe850c3f5686d9ae03a90cc1d585438164070d2ca4cb68a4462',
        V / 'agent-lsr-victory-repair-c/budget-qualification.json': '70cb6685906eeef792a4e27013b7e53d2ec308ed78a130945a77b005b7a75582',
        V / 'agent-lsr-victory-repair-c/persistent-controls/freeze.json': '472157f88175f7af6459a174a96a3dcaec9725ff38ed5e15f865c7ef9f006bf1',
        V / 'agent-lsr-victory-repair-c/dq-native-a/freeze.json': 'fe359f570f0b4c7088e2cae7019903a59975fdb50a1d55ada959a7cce1279a4d',
    }
    for p, h in pins.items():
        assert sha(p) == h, p
    old = json.loads(P.read_text())
    before = old['source_hashes']
    assert len(before) == 440 and all(sha(R / n) == h for n, h in before.items())
    for row in old['builds']:
        assert all(sha(R / x['path']) == x['sha256'] for x in row['artifacts'].values())
    d = json.loads((H / 'report.json').read_text())
    admission = json.loads((V / 'root49-union-admission-dv.json').read_text())
    assert admission['status'] == 'PASS_ACTUAL_DQ_COMPONENT_ADMISSION_WORKING_CHECKPOINT_ONLY'
    assert admission['total_component_cases'] == 10230
    after = d['source_hashes']
    assert len(after) == 442 and not set(before) - set(after)
    assert all(sha(H / 'source' / n) == h for n, h in after.items())
    assert len(d['builds']) == 4 and all(x['exit'] == 0 for x in d['builds'])
    for row in d['builds']:
        stem = H / 'source/build' / ('smb-crossover-' + row['mapper'] + ('-baseline' if row['baseline'] else ''))
        assert all(sha(stem.with_suffix('.' + ext)) == h for ext, h in row['artifacts'].items())
        if row['baseline']:
            assert row['baseline_exact_CG']
        else:
            assert row['only_delta_from_N_rare_operands_and_exact_C_tails']
    changes = {n: dict(before=before.get(n), after=h, existing_before=sha(R / n) if (R / n).exists() else None)
               for n, h in after.items() if before.get(n) != h}
    assert len(changes) == 12
    assert set(after) - set(before) == {'src/bill_source_body.s', 'src/guest_victory_control.s'}
    assert all(not (R / n).exists() for n in set(after) - set(before)), 'Uncataloged new main file needs review'
    sys.path.insert(0, str(R / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(R)
    assert used + 150_000_000 < 55_000_000_000
    C.mkdir(parents=True)
    backup = C / 'before-changed-files.zip'
    with zipfile.ZipFile(backup, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for n in sorted(changes):
            if (R / n).exists():
                z.write(R / n, n)
    manifest = dict(status='INSTALLING_TESTED_WORKING_BODY_VICTORY_DU',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), publisher_sha256=sha(__file__),
        parent_manifest=dict(path=P.relative_to(R).as_posix(), sha256=sha(P)),
        before_source_hashes=before, source_changes=changes,
        backup=dict(path=backup.relative_to(R).as_posix(), sha256=sha(backup)),
        evidence=[dict(path=p.relative_to(R).as_posix(), sha256=sha(p), bytes=p.stat().st_size) for p in pins],
        builds=[], source_body_cases=9978, matched_profile_vectors=5568,
        victory_native_cases=132, native_fallback_cases=120,
        behavior=[
            'Contra source standing/jumping/prone body, head-cell sampling and water update epoch, with appended cache bytes and old RAM addresses preserved.',
            'Exact threshold body publication saves231..298 cycles versus the F correctness control; no whole-game lag percentage claimed.',
            'Rare guest castle automatic walk completes finite attack timers and pending Simon axe/Link beam events, removing the observed Simon castle stall.',
            'All ordinary victory-C code bytes are literal N; Mario/Luigi rare fallback adds10/14cycles and preserves complete CPU/RAM/write state.',
            'Both disabled-crossover baselines remain exact CG. Existing menu START/OPTIONS, Easy/Hard, default outlinesOff and character alternates are inherited.'],
        limitations=[
            'Source body predicates compare against native integer enemy proxies; source enemy fractions/bitmap firebars/terrain/platform behavior remain separately qualified. The two old Bill contacts are not claimed fixed.',
            'Source WATCH projectile pool updates, EasyLink separate animation framegraph and retained morph/wall art remain incomplete. Automatic walking during a remaining ground attack is an explicit NES adaptation.',
            'Native PLAYER append is30bytes, correcting the immutable C handwritten28byte budget. MMC3 PLAYER bank has3free bytes; MMC5 has19.',
            'N timing changes mean old BY full-route tapes need fresh integrated replay; historical BY clears are not relabeled DU clears.'],
        outstanding='All13 current-build ordinary routes, all alternates/upgrades, further lag work and final lossless recordings with frame review remain active.',
        workspace_cap_bytes=55_000_000_000, workspace_bytes_before=used,
        accepted_release=False, goal_complete=False)
    def save():
        (C / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    save()
    for n in sorted(changes):
        target = R / n
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(H / 'source' / n, target)
    for mapper in ('mmc3', 'mmc5'):
        expected = next(x for x in d['builds'] if x['mapper'] == mapper and not x['baseline'])
        stem = H / 'source/build' / ('smb-crossover-' + mapper)
        artifacts = {}
        for ext in ('nes', 'lbl', 'map', 'dbg'):
            src = stem.with_suffix('.' + ext)
            dst = R / 'build' / src.name
            assert sha(src) == expected['artifacts'][ext]
            shutil.copyfile(src, dst)
            assert sha(dst) == sha(src)
            artifacts[ext] = dict(path=dst.relative_to(R).as_posix(), sha256=sha(dst), bytes=dst.stat().st_size)
            if ext == 'dbg':
                compressed = gzip.compress(dst.read_bytes(), mtime=0)
                (C / (dst.name + '.gz')).write_bytes(compressed)
                if dst.with_suffix('.dbg.gz').exists():
                    dst.with_suffix('.dbg.gz').write_bytes(compressed)
            else:
                shutil.copyfile(dst, C / dst.name)
        manifest['builds'].append(dict(mapper=mapper, artifacts=artifacts, byte_exact_native_tested_DQ=True))
        save()
    assert all(sha(R / n) == h for n, h in after.items())
    archive = C / 'source-v49-body-victory-du.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for n in sorted(after):
            z.write(R / n, n)
    manifest.update(status='PASS_WORKING_BODY_VICTORY_DU_BOTH_MAPPERS', source_hashes=after,
        source_archive=dict(path=archive.relative_to(R).as_posix(), sha256=sha(archive), bytes=archive.stat().st_size),
        workspace_bytes_after=workspace_bytes(R))
    save()
    print(manifest['status'], sha(C / 'manifest.json'), 'changed', len(changes), flush=True)


if __name__ == '__main__':
    main()
