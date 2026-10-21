"""Require exact bytewise composition of independently tested parent ROMs."""
from pathlib import Path
import hashlib
import importlib.util
import json

R = Path(__file__).resolve().parents[2]
V = R/'build/verification'
D = V/'root49-combined-working-b'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
spec = importlib.util.spec_from_file_location('bound_image', V/'agent49k-samus-water-up-direction-component-a/image.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def segments(image):
    return {s['name']:{k:s[k] for k in ('start','size','ooffs') if k in s} for s in image.segs.values()}


def main():
    out = D/'composition-review.json'
    assert not out.exists()
    E = V/'root49-sophia-land-fix-a/source-e/build'
    S = V/'agent-lsr-sophia-feet-perf-a/source-b/build'
    A = V/'agent49-samus-bill-arsenal-a/source-f/build'
    rows = []
    for mapper in ('mmc3','mmc5'):
        for baseline in (False, True):
            name = f'smb-crossover-{mapper}'+('-baseline' if baseline else '')
            e,s,a,c = [m.Image(p/(name+'.nes')) for p in (E,S,A,D/'source/build')]
            assert len(e.raw)==len(s.raw)==len(a.raw)==len(c.raw)
            sd = {i for i,(x,y) in enumerate(zip(e.raw,s.raw)) if x!=y}
            ad = {i for i,(x,y) in enumerate(zip(e.raw,a.raw)) if x!=y}
            assert not sd&ad
            assert len(sd)==(0 if baseline else 469)
            assert len(ad)==(0 if baseline else 61)
            expected = bytearray(s.raw)
            for i in ad: expected[i]=a.raw[i]
            assert c.raw==bytes(expected), name
            assert c.ram==s.ram==a.ram==e.ram, name
            assert segments(c)==segments(s), name
            assert c.raw[:16]==e.raw[:16] and c.raw[16+512*1024:]==e.raw[16+512*1024:]
            log=D/f'build-{mapper}'+Path('-baseline.log' if baseline else '.log') if False else D/f'build-{mapper}{"-baseline" if baseline else ""}.log'
            assert 'Built ' in log.read_text() and 'Error:' not in log.read_text()
            rows.append(dict(name=name, metadata=c.metadata(),
                sophia_parent_changes=len(sd),samus_parent_changes=len(ad),
                disjoint_ROM_offsets=True, exact_union_of_tested_parent_bytes=True,
                complete_old_RAM_addresses_equal=True, all_segment_layout_equal_to_sophia_parent=True,
                header_and_CHR_exact=True, build_log_sha256=sha(log)))
    catalog=json.loads((D/'source-catalog.json').read_text())
    assert len(catalog)==455 and all(sha(D/'source'/n)==h for n,h in catalog.items())
    result=dict(status='PASS_FOUR_BUILDS_EXACT_DISJOINT_ROM_COMPOSITION_RAM_AND_LAYOUT',
        script_sha256=sha(__file__), preparation_sha256=sha(D/'preparation.json'),
        source_catalog_sha256=sha(D/'source-catalog.json'), builds=rows,
        native_or_fixture_tests_rerun_by_this_review=False,
        scope='Literal union of already tested Sophia optimization and Samus action bytes over immutable audio E. No new RAM/layout/audio/CHR changes. Whole candidate regression suite remains required.',
        main_changed=False,goal_complete=False,accepted_release=False)
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],roms={z['name']:z['metadata']['rom']['sha256'] for z in rows})))


if __name__=='__main__':main()
