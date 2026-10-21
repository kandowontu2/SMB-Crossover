"""Review frozen parents and materialize their disjoint source overlays."""
from pathlib import Path
import hashlib
import json
import shutil

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
D = V / 'root49-combined-working-b'
E = V / 'root49-sophia-land-fix-a'
S = V / 'agent-lsr-sophia-feet-perf-a'
A = V / 'agent49-samus-bill-arsenal-a'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def pinned(path, digest):
    assert sha(path) == digest, str(path)
    return json.loads(path.read_text())


def verify_files(base, catalog):
    for name, record in catalog.items():
        p = base / name
        if isinstance(record, str):
            assert sha(p) == record, name
        else:
            assert p.stat().st_size == record['bytes'] and sha(p) == record['sha256'], name


def main():
    assert not D.exists(), 'Never overwrite an evidence phase.'
    sf = pinned(S / 'implementation-freeze.json', '98bf3a6f5be4cf80d2ba9053d277abc5e110f1262779f79137e55fe4a031d04a')
    sr = pinned(S / 'final-review.json', '4922f2a2aff32259d62bd45369c29dbda24a7b892c64b90a19cfed44d5f0d6d2')
    sc = pinned(S / 'source-catalog-final.json', '6c64950a6acdf716bcb50542c4c931fc9167fb1319514ce944d0258ed953a68e')
    af = pinned(A / 'action-freeze-k/freeze.json', 'a87ffe5dcf8c8786cf3d0e6a045226bca646e2849b970753db4cfc47d4476d03')
    ac = pinned(A / 'source-catalog-f.json', 'e0869cde66979d5f67fd8c0404ed8a3ca30d09b01b624893afd3ebd259a954a6')
    receipts = pinned(A / 'action-freeze-k/receipt-catalog-l.json', '8272ec894ba2317dac91a3cd5785262ab863d5db67e6fe4a9b2bf2b681288804')
    supplement = pinned(A / 'action-freeze-k/supplement-l.json', '37a2dcc809ef4be0862afc15d700731c1679a0218be1c5e96a438b3dd8bdb4c0')
    ec = pinned(E / 'source-catalog-e.json', 'dd5b66788905424747656a145a03e123c0337c1b09026dce2baf12e1f7ae8f86')
    assert set(sc) == set(ac) == set(ec) and len(ec) == 455
    verify_files(S, sf['files'])
    verify_files(A, receipts)
    for base, cat in [(E/'source-e', ec), (S/'source-b', sc), (A/'source-f', ac)]:
        verify_files(base, cat)
    sd = {n for n in ec if sc[n] != ec[n]}
    ad = {n for n in ec if ac[n] != ec[n]}
    assert sd == {'src/characters.s', 'src/sophia_source_terrain.s'}
    assert ad == {'src/remaining_weapons.s'} and not sd & ad
    assert sr['native_cases'] == 364 and sr['native_failures'] == 0
    assert sr['strict_native_reexecutions'] == 354 and sr['actual_interrupt_reexecution_gaps'] == 10
    assert not sf['owned_live_jobs'] and not sf['main_installed'] and af['no_owned_jobs']
    source = D / 'source'
    for name in ec:
        parent = S/'source-b' if name in sd else A/'source-f' if name in ad else E/'source-e'
        target = source/name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(parent/name, target)
    generated = json.loads((E/'preparation.json').read_text())['generated11']
    for name, digest in generated.items():
        p = E/'source-e/build/generated'/name
        assert sha(p) == digest
        target = source/'build/generated'/name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, target)
    builder = (S/'build-b.py').read_text()
    anchor = next(z for z in builder.splitlines() if z.startswith('ROOT = Path('))
    builder = builder.replace(anchor, "ROOT = Path(__file__).resolve().parent / 'source'", 1)
    (D/'build.py').write_text(builder)
    catalog = {n:sha(source/n) for n in ec}
    (D/'source-catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')
    report = dict(status='PREPARED_DISJOINT_OVERLAYS_NOT_YET_BUILT_OR_INSTALLED',
        script_sha256=sha(__file__), source_catalog_sha256=sha(D/'source-catalog.json'),
        parent_catalog_sha256=sha(E/'source-catalog-e.json'), source_files=len(catalog),
        rehashed_sophia_receipts=len(sf['files']), rehashed_samus_receipts=len(receipts),
        parents={str(S/'implementation-freeze.json'):sha(S/'implementation-freeze.json'),
                 str(A/'action-freeze-k/freeze.json'):sha(A/'action-freeze-k/freeze.json'),
                 str(A/'action-freeze-k/supplement-l.json'):sha(A/'action-freeze-k/supplement-l.json')},
        changed_sources=sorted(sd|ad), disjoint_overlay_sources=True, generated11=generated,
        phase_cap_bytes=500000000, final_reserve_bytes=50000000, global_cap_bytes=70000000000,
        retained_limitations=sr['qualifications']+af['limitations'],
        main_changed=False, goal_complete=False, accepted_release=False)
    (D/'preparation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['status','source_files','rehashed_sophia_receipts','rehashed_samus_receipts','changed_sources']}))


if __name__ == '__main__':
    main()
