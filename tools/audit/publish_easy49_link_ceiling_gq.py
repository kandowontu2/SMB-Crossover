"""Admit the frozen scoped Link ceiling response over exact EL, retaining all predecessors."""
from pathlib import Path
import datetime
import gzip
import hashlib
import json
import shutil
import zipfile

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'agent-lsr-link-ceiling-c'
C = R / 'build/checkpoints/roster-audit-v49-link-ceiling-gq'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not C.exists()
    parent = R / 'build/checkpoints/roster-audit-v49-link-watch-el/manifest.json'
    assert sha(parent) == '7cf7f1ebf96f21184e5b9b7d2eff5a832038862a1e057f19f7a00018fb0f92e4'
    old = json.loads(parent.read_text())
    assert all(sha(R / n) == h for n, h in old['source_hashes'].items())
    for b in old['builds']:
        assert all(sha(R / a['path']) == a['sha256'] for a in b['artifacts'].values())
    freeze = H / 'implementation-freeze-b.json'
    assert sha(freeze) == '7a57f22696681f5aa134365ddd231b0fddb64bd09c289f706cabab6c8e74dda6'
    frozen = json.loads(freeze.read_text())
    for n, h in frozen['files'].items():
        assert sha(H / n) == h, n
    review = H / 'final-review.json'
    assert sha(review) == '3bd67ac13afc0c1f8e7fda7b0d9db447138c67f6831a5121924bb269f0b38e3b'
    d = json.loads(review.read_text())
    after = d['source_catalog']
    assert len(after) == d['source_catalog_count'] == 442
    assert all(sha(H / 'source' / n) == h for n, h in after.items())
    changes = {n: dict(before=old['source_hashes'].get(n), after=h)
        for n, h in after.items() if old['source_hashes'].get(n) != h}
    assert changes == d['changes']
    assert set(changes) == {'smb1base.cfg', 'src/collision.s', 'src/entrypoint.s',
        'src/megaman_environment.s', 'src/easy_link_head_response.s'}
    assert not (R / 'src/bill_source_body.s').exists()
    assert after['src/guest_victory_control.s'] == old['source_hashes']['src/guest_victory_control.s']
    strict = json.loads((H / 'strict-review-g.json').read_text())
    assert strict['status'] == 'PASS_SCOPED_NATIVE_AND_COMPILED_LAYOUT_ABI'
    assert d['strict']['actual_native_calls'] == 136
    assert d['strict']['Hard_foreign_compiled'] == 2400 and d['strict']['API_cases'] == 80
    assert sum(z['cases'] for z in strict['foreign_cpu']) == 2400
    assert all(z['all8status_bits_literal'] and z['all10240RAM_and_every_write'] for z in strict['foreign_cpu'])
    for n in d['primary_native_cases']:
        assert n['result']['cases'] == 34 and n['setup_failures'] == 0
        assert n['result']['failures'] == (0 if n['version'] == 'candidate' else 80)
    for b in d['builds']:
        for a in b['artifacts'].values():
            assert sha(R / a['path']) == a['sha256']
        if b['baseline']:
            expected = {'mmc3': '0511c6844d0e9fa61f4b4fbc34e6f9c67d8247d3ca964ebbb0c9c2718cdc5146',
                'mmc5': '34858561f4825dcc96cdd5fd46872f9230890c93af95351720c8536155f5cbbd'}[b['mapper']]
            assert b['artifacts']['nes']['sha256'] == expected
    proof = json.loads((H / 'source-envelope-proof.json').read_text())
    for k in ('source_files', 'native_sources'):
        assert all(sha(R / n) == h for n, h in proof[k].items())
    # Independent endpoint arithmetic, including correction of the prose typo.
    max_left = 65535 + 95573 + 81920
    min_right = 966656 - 95573
    assert 8*65536-max_left == 281260 and min_right-8*65536 == 346795
    assert max_left/65536 == 3.70831298828125
    qualifications = json.loads((H / 'qualification.json').read_text())
    admission = dict(status='PASS_ROOT_SCOPED_LINK_CEILING_RESPONSE_REVIEW',
        script_sha256=sha(__file__), freeze_sha256=sha(freeze), receipt_files_rehashed=len(frozen['files']),
        source_files_rehashed=442, source_changes=changes, native_candidate_cases=68,
        actual_native_calls_reexecuted=136, Hard_foreign_compiled=2400, API_boundaries=80,
        source_horizontal_margins_Q16=[281260, 346795],
        source_proof_prose_correction='max(f-v+1.25) is3.70831298828125; the frozen proof sentence2.458... omits1.25. Both exact recorded margins are correct; no runtime change.',
        qualification=qualifications, root_did_not_rerun_specialist_native_or_compiled_tests=True,
        performance_scope='Zero noncontact-path instructions; rare Hard/foreign head response+20/+19cycles; scoped Easy positive about1260..1328cycles.',
        accepted_release=False, goal_complete=False)
    admission_path = V / 'root49-link-ceiling-admission-gq.json'
    assert not admission_path.exists()
    admission_path.write_text(json.dumps(admission, indent=2)+'\n')
    C.mkdir(parents=True)
    backup = C / 'before-changed-files.zip'
    with zipfile.ZipFile(backup, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for n, h in changes.items():
            if h['before'] is not None:
                z.write(R / n, n)
    manifest = dict(status='INSTALLING_WORKING_LINK_CEILING_GQ',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), publisher_sha256=sha(__file__),
        parent_checkpoint=dict(path=parent.relative_to(R).as_posix(), sha256=sha(parent)),
        source_changes=changes, before_source_hashes=old['source_hashes'],
        backup=dict(path=backup.relative_to(R).as_posix(), sha256=sha(backup)),
        admission=dict(path=admission_path.relative_to(R).as_posix(), sha256=sha(admission_path)),
        qualification=qualifications, builds=[], accepted_release=False, goal_complete=False,
        outstanding='Bill hot successor, current integrated full roster/arsenal, lag optimization and final retained media remain active.')

    def save():
        (C / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')

    save()
    for n in changes:
        shutil.copyfile(H / 'source' / n, R / n)
    for mapper in ('mmc3', 'mmc5'):
        b = next(x for x in d['builds'] if x['mapper'] == mapper and not x['baseline'])
        artifacts = {}
        for ext, a in b['artifacts'].items():
            source = R / a['path']
            target = R / 'build' / source.name
            shutil.copyfile(source, target)
            assert sha(target) == a['sha256']
            artifacts[ext] = dict(path=target.relative_to(R).as_posix(), sha256=sha(target), bytes=target.stat().st_size)
            if ext == 'dbg':
                compressed = gzip.compress(target.read_bytes(), mtime=0)
                (C / (target.name+'.gz')).write_bytes(compressed)
                if target.with_suffix('.dbg.gz').exists():
                    target.with_suffix('.dbg.gz').write_bytes(compressed)
            else:
                shutil.copyfile(target, C / target.name)
        manifest['builds'].append(dict(mapper=mapper, artifacts=artifacts, byte_exact_native_tested_private_C=True))
        save()
    assert all(sha(R / n) == h for n, h in after.items())
    archive = C / 'source-v49-link-ceiling-gq.zip'
    shutil.copyfile(R / d['source_archive']['path'], archive)
    assert sha(archive) == d['source_archive']['sha256']
    manifest.update(status='PASS_WORKING_LINK_CEILING_GQ_BOTH_MAPPERS', source_hashes=after,
        source_archive=dict(path=archive.relative_to(R).as_posix(), sha256=sha(archive), bytes=archive.stat().st_size))
    save()
    print(manifest['status'], sha(C / 'manifest.json'))


if __name__ == '__main__':
    main()
