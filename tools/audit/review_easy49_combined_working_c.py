"""Check the literal 19-byte armor overlay in both final compiled images."""
from pathlib import Path
import hashlib
import importlib.util
import json

R=Path(__file__).resolve().parents[2]
V=R/'build/verification'
D=V/'root49-combined-working-c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('bound_image',V/'agent49k-samus-water-up-direction-component-a/image.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def segments(image):
    return {s['name']:{k:s[k] for k in ('start','size','ooffs') if k in s} for s in image.segs.values()}


def main():
    out=D/'composition-review.json';assert not out.exists()
    A=V/'agent49-samus-bill-arsenal-a'
    builds=[]
    for mapper in ('mmc3','mmc5'):
        for baseline in (False,True):
            name=f'smb-crossover-{mapper}'+('-baseline' if baseline else '')
            paths=[V/'root49-combined-working-b/source/build',A/'source-f/build',A/'source-p/build',D/'source/build']
            b,f,p,c=[m.Image(z/(name+'.nes')) for z in paths]
            delta={i for i,(x,y) in enumerate(zip(f.raw,p.raw)) if x!=y}
            assert len(delta)==(0 if baseline else 9)
            if not baseline:
                span=p.hook('Armored','MegaManWeapons')['rom_offset']
                assert delta <= set(range(span,span+19))
            assert all(b.raw[i]==f.raw[i] for i in delta)
            expected=bytearray(b.raw)
            for i in delta:expected[i]=p.raw[i]
            assert c.raw==bytes(expected),name
            assert c.ram==b.ram==f.ram==p.ram
            assert segments(c)==segments(b)
            log=D/f'build-{mapper}{"-baseline" if baseline else ""}.log'
            assert 'Built ' in log.read_text() and 'Error:' not in log.read_text()
            builds.append(dict(name=name,metadata=c.metadata(),changed_ROM_bytes=len(delta),admitted_region_bytes=0 if baseline else 19,
                changed_banks=sorted({(i-16)//8192 for i in delta}),
                exact_literal_tested_overlay=True,old_RAM_and_segment_layout_equal=True,
                build_log_sha256=sha(log)))
    catalog=json.loads((D/'source-catalog.json').read_text())
    assert len(catalog)==455 and all(sha(D/'source'/n)==h for n,h in catalog.items())
    result=dict(status='PASS_EXACT_COMBINED_19BYTE_MISSILE_OVERLAY_FOUR_BUILDS',
        script_sha256=sha(__file__),source_catalog_sha256=sha(D/'source-catalog.json'),
        preparation_sha256=sha(D/'preparation.json'),builds=builds,
        qualifications=['Full suite C executes predecessor B; literal19-byte armored-admission successor is covered separately by the compiled predicate and attained native missile/foreign controls.',
            'The armor predicate changes V, with explicit downstream liveness reasoning; no full-P ABI identity claim.',
            'Remaining Ice behavior, routes, all-arsenal fidelity and final recordings are unfinished.'],
        main_changed=False,goal_complete=False,accepted_release=False)
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],roms={x['name']:x['metadata']['rom']['sha256'] for x in builds})))


if __name__=='__main__':main()
