"""Durable full-MM clear, rejected material Bill cost, and active roster handoff."""
from pathlib import Path
import datetime
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = V / 'root-current49-progress-al.json'
    assert not out.exists()
    previous = V / 'root-current49-progress-ak.json'
    assert sha(previous) == 'c6b489bed1e3783230872009f4c91bb0d592f24d73cfd5139353b1a1008390c3'
    d = json.loads(previous.read_text())
    main_path = R / 'build/checkpoints/roster-audit-v49-link-watch-el/manifest.json'
    assert sha(main_path) == '7cf7f1ebf96f21184e5b9b7d2eff5a832038862a1e057f19f7a00018fb0f92e4'
    main_state = json.loads(main_path.read_text())
    assert len(main_state['source_hashes']) == 441
    assert all(sha(R / n) == h for n, h in main_state['source_hashes'].items())
    assert not (R / 'src/bill_source_body.s').exists()
    for b in main_state['builds']:
        assert all(sha(R / a['path']) == a['sha256'] for a in b['artifacts'].values())
    pins = {
        previous: sha(previous),
        V / 'root49-ec-megaman-full-ez.json': '3a3d33cfa20271a102be3b66d72f8f7158485e3aa2559c1bf54c0d31c0ccf2f9',
        V / 'root49-full-route-inventory-fb.json': '541f92d7bb68078247252bd3e34fe11a463a35a4fa14c9804d7885887a3010f5',
        V / 'root49-bill-axis-union-fc.json': '187edb11f891ede790d642132f9795af5daaa1662e622af0c5be76ff00a0667c',
        V / 'root49-fire-star-review-ff.json': '3e3e265775e15b9b71dea797547b315cde07d873c375f01b533b6928f315c04c',
        V / 'root49-bill-axis-link-eu/report.json': 'b8d29b6afe7158ee11d1883aac6d103d247879a070c332fb2954365d43878100',
        V / 'agent49-bill-head-axis-g/freeze-u.json': '32db2a18b92534b0fab5f33394bd1ee059509ce8f119f74c575b8e7841242a7f',
        V / 'agent-lsr-victory-repair-eu-checks-a/freeze.json': 'b7e63e75a62920404e128a3173c1e90354e476a5732155010252e4507c0a62b2',
        V / 'specialist-ordinary-fire-combat-ec-a/handoff-combat-star-g.json': 'bbe17991a4f287ff4a0fc00d326e4251d4598df940197f8e033cccfc8e609922',
        V / 'root49-el-bass-transfer-fd/report.json': '46825a9456104363de9209f2f053599adefad3bf5555d3edecb37f9f7086b2b9',
    }
    for p, h in pins.items():
        assert sha(p) == h, p
        d['references'].append(dict(path=p.relative_to(R).as_posix(), sha256=h, bytes=p.stat().st_size))
    for tag, char, mapper in [('root49er-megaman-water', 1, 'mmc3'),
            ('root49ew-megaman-exit', 1, 'mmc3'), ('root49ex-megaman-fixed', 1, 'mmc3'),
            ('root49ey-megaman-m5-fixed', 1, 'mmc5'), ('root49fd-bass-fixed', 9, 'mmc3'),
            ('root49fe-bass-live', 9, 'mmc3')]:
        folder = R / 'build/roster-through-2-2' / f'{tag}-{char}-v0-{mapper}'
        m = json.loads((folder / 'manifest.json').read_text())
        d['route_results'][tag] = dict(result=m['result'],
            result_sha256=sha(folder / 'result.json'), manifest_sha256=sha(folder / 'manifest.json'),
            actual_ROM_sha256=sha(folder / f'smb-crossover-{mapper}.nes'),
            inputs_sha256=sha(folder / 'inputs.csv'), trace_sha256=sha(folder / 'trace.csv'),
            verified_through_2_2=m['verified_through_2_2'], full_frame_audit=m['full_frame_audit'])
    sys.path.insert(0, str(R / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(R)
    assert used < 55_000_000_000
    d.update(status='ACTIVE_EL_UNCHANGED_MM_EC_FULL_CLEAR_G2_COST_REJECTED_HOT_SUCCESSOR_PENDING',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), script_sha256=sha(__file__),
        MegaMan='EC EX independent fixed full25571/25570, all21 trace fields/tape byte-identical to EW; sixzero/actual2-3entry25547+25controlsX40to61. Full graphics/hardware audio audit, not video/perceptual review. M5 EY same-tape negative1725, first19fieldgameplay difference982vx2vs4; no source-defect inference. Final successor/Hard/M5/allarsenal/media remain open.',
        Bill='G2 frozen correctness9978old+12746new/5568profiles/4ordinary1780 controls; rootFC rehash1001 receipts and442rawsource. Ordinary/six-Goomba cost is material, so G2/EU not admitted. Separate hot-layout successor V is private; current farcall outputN/Z issue being repaired with2 new capture cells explicitly accounted, oldaliases/audio/config/baselines protected.',
        EU='PrivateG2+soleELhelper,4builds/baselinesCG; G2RAM/PLAYER exact, rarehelperonlyROMdelta. Actual616native+1000strictcompiled calls pass; correctness only, no performance admission.',
        coverage='Natural upgrade8coldECcases retained; combat8ECcases/38actualfireball defeat receipts/ground+air bothdirections,3M3responsive discoveries properly qualified; EasyMarioStar independently fixedbothmaps, real contacts/no shots/expiry735updates, qualified approximation of AS12000ms. RootFF rehash144 references. Fullarsenal/immunity/postexpiry/otherStarvariants/sourceart-waveform/finalrebind/media remain open.',
        active_specialists=['Separate Bill hot-path successor preserves frozen G2/EU, exact flags/layout/cost pending',
            'Simon explicit C ordinary late-water T;2940/Y111 coldL, previous S pipe-jump stall retained',
            'Pit explicit EL ordinary J clears1-4/live2-1; new350MB phase, no finalfixed/media yet'],
        root_live_handles=[dict(handle=61311, tag='root49-fg-bass-12-pipes-a', ROM='explicit immutable EJ=EL',
            scope='bounded ordinary-input opaque discovery from FE8880; any adopted branch requires independent power-on/all10240RAM proof')],
        inventory='FB indexes79 existing complete audited packets/24groups with exact originalROMs and3missing-artifact errors. Reuse candidates, not current-runtime transfer acceptance.',
        workspace_bytes=used, cap_bytes=55_000_000_000, retain_lossless_captures=True,
        accepted_release=False, goal_complete=False,
        QA_snapshot=dict(path='docs/qa/easy-hard-legacy-v49.md', sha256=sha(R / 'docs/qa/easy-hard-legacy-v49.md')))
    d['phase_budgets'].update(Bill=5_200_000_000, ordinary_Mario_combat=240_000_000,
        ordinary_Pit_EL=350_000_000, root_Bass_EL=300_000_000)
    out.write_text(json.dumps(d, indent=2) + '\n')
    print(d['status'], sha(out), used)


if __name__ == '__main__':
    main()
