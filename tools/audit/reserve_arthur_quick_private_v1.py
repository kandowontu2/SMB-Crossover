"""Bind the joint Arthur/Quick Man private host integration allocations."""
from pathlib import Path
import hashlib
import json

R = Path(__file__).resolve().parents[2]
DEST = R / 'docs/qa/checkpoints/2026-10-30/arthur-quick-private-allocation'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not DEST.exists()
    mp = R / 'build/arthur-host-plan-v2/merged-occupancy.json'
    assert sha(mp) == '3a2d4c695a30b2907662370b680e9c8f48ccb9a7378fad765424c54ef5a4e8cb'
    merged = json.loads(mp.read_text())
    qp = R / 'build/quickman-host-prep-v2/joint-request.json'
    assert sha(qp) == '10a0c9cf7c2b6d528ad1533e7d836bbdd85356df37ba304aedf929b769100975'
    quick = json.loads(qp.read_text())
    ap = R / 'build/arthur-host-prep-v5/fragment-layout.json'
    arthur = json.loads(ap.read_text())
    for owner, expected in [
        ('quickman-host-prep-v2', 'e4b0bf60cc357b93775f819b1852b27f43e482080fb776cd8a1800518e84d660'),
        ('arthur-host-prep-v5', '31a8c6bc9bb97519c5db7f237bd04d971f79be11fb2ed90f35918fa5f9498d1d'),
    ]:
        p = R / 'build' / owner / 'handoff.json'
        assert sha(p) == expected
        d = json.loads(p.read_text())
        bindings = d.get('bindings', {})
        if isinstance(bindings, list):
            raise AssertionError('Unexpected binding schema')
        for path, h in bindings.items():
            assert sha(path) == h, path
    gaps = [dict(bank=g['bank'], start=g['offset_start'], end=g['offset_end_exclusive'])
            for g in merged['remaining_PRG_gaps'] if g['bytes'] >= 128]
    assert sum(g['end'] - g['start'] for g in gaps) == 17841
    ar = [dict(bank=g['bank'], start=g['start'], end=g['end']) for g in arthur['requested_gaps']]
    assert all(g in gaps for g in ar)
    qm = [g for g in gaps if g not in ar]
    assert sum(g['end'] - g['start'] for g in ar) == 7717
    assert sum(g['end'] - g['start'] for g in qm) == 10124
    placements = quick['Quick_placements']
    for p in placements:
        assert any(g['bank'] == p['bank'] and g['start'] <= p['offset']
                   and p['offset'] + p['bytes'] <= g['end'] for g in qm), p
    assert sum(p['bytes'] for p in placements) == 9031
    # Check the newer roots too: an old occupancy receipt alone is insufficient.
    cases = merged['cases'] + [
        dict(owner='actual_parent_v5', path=str(R / 'build/character-host-union-v5/candidate.nes'),
             sha256=quick['parent_ROM_sha256']),
        dict(owner='union_v7', path=str(R / 'build/character-host-union-v7/candidate.nes'),
             sha256='ccb72233' ),
        dict(owner='Rogue_victory', path=str(R / 'build/rogue-dawn-victory-pose-v4/candidate.nes'),
             sha256='ba3033e17e12705ffa141d0908a01188e17779df717a6843fd12c638f1b0f5dc'),
    ]
    preimages = []
    for case in cases:
        p = Path(case['path']); h = sha(p)
        assert h.startswith(case['sha256']), p
        b = p.read_bytes()
        for g in gaps:
            data = b[16 + g['bank'] * 8192 + g['start']:16 + g['bank'] * 8192 + g['end']]
            assert data == b'\xff' * (g['end'] - g['start']), (p, g)
        preimages.append(dict(owner=case['owner'], path=str(p), sha256=h))
    proof = dict(
        status='PRIVATE_HOST_INTEGRATION_ALLOCATIONS_GRANTED_NOT_SHARED_ADMISSION',
        parent=quick['parent_ROM'], parent_sha256=quick['parent_ROM_sha256'],
        merged_occupancy_sha256=sha(mp), joint_request_sha256=sha(qp),
        verified_parent_preimages=preimages,
        Arthur=dict(PRG=ar, payload_bytes=6892, reserved_bytes=7717,
                    active_RAM=[dict(start='5C00', end_exclusive='5CB0', bytes=176)],
                    persistent_RAM=dict(start='5F90', end_exclusive='5F98', bytes=8),
                    ownership='Selected raw32 only; no foreign or global use'),
        Quick_Man=dict(PRG=qm, prepared_placements=placements,
                       payload_bytes=9031, reserved_bytes=10124,
                       spare_in_owned_intervals=1093,
                       active_RAM=dict(start='5C00', end_exclusive='5E30',
                                       excluded=['5CC3'], used_bytes=557,
                                       exact_layout='build/quickman-host-prep-v2/fragmented.cfg'),
                       persistent_RAM=dict(start='5F88', end_exclusive='5F90', bytes=8),
                       ownership='Selected raw9 and FmAlts bit5 only; exclude Bass/Roll'),
        RAM_policy=[
            'Active areas are temporal aliases, not globally free memory. Do not touch X5Cv3PriorHurt at5CC3.',
            'Persistent records have two per-player4-byte entries; preserve HP/progression and explicitly reset transient source state on life/area initialization.',
            'Parodius History owns these persistent aliases while raw18 is selected; no cross-character persistence promise.',
            'IcGlobalInit clears5F80..97 on new game; constructors run after generic initialization.',
            'R0/R1 at0003/0004 may be borrowed only with restore; world R6/R7 at0009/000A locally restored. No new ZP; never touch NMI0000..0002.',
        ],
        CHR='Existing247..250 Arthur and251..255 Quick grants remain; no additional CHR grant in this receipt.',
        implementation_scope='Build private actual-host candidates and implement real hooks, collision, scrolling, lifecycle, items, enemies, palettes, HUD and audio. No shared or Downloads installation from this allocation.',
        acceptance=['Exact parent source/link and immutable fixed-bank/SMC protection',
                    'Actual foreign Main/NMI and two-player/transition tests with guards',
                    'Source coordinate/foot anchor and native camera/clamp resynchronization',
                    'Bounded native gameplay and earned powerup qualification before menu readiness'],
        bindings={str(mp): sha(mp), str(qp): sha(qp), str(ap): sha(ap),
                  str(Path(__file__).resolve()): sha(__file__)},
    )
    DEST.mkdir(parents=True)
    output = DEST / 'root-review-and-reservations.json'
    output.write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(dict(path=str(output), sha256=sha(output), PRG_reserved=17841,
                          Arthur_headroom=825, Quick_headroom=1093)))


if __name__ == '__main__':
    main()
