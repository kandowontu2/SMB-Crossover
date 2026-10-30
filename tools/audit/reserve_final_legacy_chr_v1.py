"""Review frozen physical ownership before reserving the last legacy CHR pages."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[2]
O = R/'docs/qa/checkpoints/2026-10-30/final-legacy-chr-reservations'


def binding(path):
    path = Path(path).resolve()
    return dict(path=str(path), bytes=path.stat().st_size,
                sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def main():
    assert not O.exists(), 'Preserve the original reservation review'
    reports = [R/'build/arthur-host-plan-v1/resource-audit.json',
               R/'build/arthur-host-plan-v2/merged-occupancy.json',
               R/'build/arthur-host-plan-v2/handoff.json']
    reviewed = []
    for path in reports:
        data = json.loads(path.read_text())
        bindings = data['bindings']
        if isinstance(bindings, dict):
            bindings = [dict(path=p, sha256=h) for p,h in bindings.items()]
        for item in bindings:
            actual = binding(item['path'])
            assert actual['sha256'] == item['sha256'], item['path']
            if 'bytes' in item: assert actual['bytes'] == item['bytes']
        reviewed.append(dict(report=binding(path), verified_bindings=len(bindings)))
    merged = json.loads(reports[1].read_text())
    mask = (reports[1].parent/'CHR-occupied-pages.bin').read_bytes()
    assert len(mask) == 1024 and not any(mask[247:256])
    preimages = []
    for case in merged['cases']:
        path = Path(case['path'])
        actual = binding(path)
        assert actual['sha256'] == case['sha256']
        raw = path.read_bytes()
        unused = raw[16+1048576+247*1024:16+1048576+256*1024]
        assert len(unused) == 9216 and not any(unused)
        preimages.append(dict(ROM=actual, zero_bytes=len(unused),
                              sha256=hashlib.sha256(unused).hexdigest()))
    resource = json.loads(reports[0].read_text())
    assert len(resource['actual_compiled_publisher_reference_sites']) == 624
    assert max(max(t['physical_pages_reached']) for row in resource['CHR_candidate247_255']
               for t in row['legacy_physical_publishers'].values()) <= 246
    O.mkdir(parents=True)
    result = dict(passed=True, status='EXACT_CHR_ONLY_RESERVATIONS',
        reservations=[dict(owner='Arthur', first_page=247, end_page_exclusive=251,
                           bytes=4096, body_window=0, concurrent_projectile_window=6),
                      dict(owner='Quick Man', first_page=251, end_page_exclusive=256,
                           bytes=5120, body_and_projectiles_window=0)],
        source_review=reviewed, nine_candidate_zero_preimages=preimages,
        reviewed_producers='Legacy logical map and special/HUD tables end at physical246; '
            'all compiled direct physical producers use their allocated expanded quadrants. '
            'Eight numeric247..255 context hits are PRG bank sentinels/fill, not physical CHR publishers.',
        conditions=['These grants reserve physical CHR only; no PRG, ZP or RAM grant is implied.',
            'Each actual publisher must set the correct upper quadrant0 and be selected-owner gated.',
            'Arthur must preserve world sprite windows1..5 and7; Quick Man must preserve1..7.',
            'Exact source pixels/OAM/priority, both facings, native NMI publication and real menu/reentry '
            'must pass on the integrated candidate before shared installation.',
            'SMB2 keeps796..807 and all other existing/future leases remain unchanged.'],
        tools=[binding(__file__)])
    for path in reports:
        (O/path.name).write_bytes(path.read_bytes())
    (O/'root-review-and-reservations.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,report=binding(O/'root-review-and-reservations.json'),
                         candidates=len(preimages),reservations=result['reservations'])))


if __name__ == '__main__':
    main()
