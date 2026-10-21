"""Freeze further ordinary ability and water-route progress without upgrading scope."""
from pathlib import Path
import datetime
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = V / 'root-current49-progress-ak.json'
    assert not out.exists()
    previous = V / 'root-current49-progress-aj.json'
    assert sha(previous) == 'c9ae0352d6ede159fad9001d6627098333dc632f75d60f2665b51a5630c090e1'
    d = json.loads(previous.read_text())
    manifest = R / 'build/checkpoints/roster-audit-v49-link-watch-el/manifest.json'
    assert sha(manifest) == '7cf7f1ebf96f21184e5b9b7d2eff5a832038862a1e057f19f7a00018fb0f92e4'
    el = json.loads(manifest.read_text())
    assert len(el['source_hashes']) == 441
    assert all(sha(R / n) == h for n, h in el['source_hashes'].items())
    assert not (R / 'src/bill_source_body.s').exists()
    for b in el['builds']:
        assert all(sha(R / a['path']) == a['sha256'] for a in b['artifacts'].values())
    pins = {
        previous: sha(previous),
        V / 'root49-ordinary-upgrade-review-eq.json': 'cf150564e27153f70ba937ef57c5c538c5864a6af514ae337ae198f1124cbb81',
        V / 'specialist-ordinary-upgrades-ec-a/handoff-both-h.json': '9530e4b65453ef0b588e9b8acbb8f37624216aeb7a9e67ced870245de152bdaf',
        V / 'specialist-ordinary-upgrades-ec-a/handoff-both-h-freeze.json': '57e5a300c747299dae66bf231532e92a239991ea792b675d34edfaaa071cbd38',
    }
    for p, h in pins.items():
        assert sha(p) == h, p
        d['references'].append(dict(path=p.relative_to(R).as_posix(), sha256=h, bytes=p.stat().st_size))
    eo = R / 'build/roster-through-2-2/root49eo-megaman-water-1-v0-mmc3'
    terminal = json.loads((eo / 'result.json').read_text())
    assert terminal['failure'] == 'death' and terminal['frames'] == 21081
    d['route_results']['root49eo-megaman-water'] = dict(result=terminal,
        result_sha256=sha(eo / 'result.json'), inputs_sha256=sha(eo / 'inputs.csv'),
        trace_sha256=sha(eo / 'trace.csv'), actual_ROM_sha256=sha(eo / 'smb-crossover-mmc3.nes'),
        passive_owned_injury_sha256=sha(eo / 'mm-injury-owner.csv'))
    ep = R / 'build/roster-through-2-2/search/root49-ep-megaman-22-water-a'
    m = json.loads((ep / 'manifest.json').read_text())
    assert m['branch_coldboot_verified'] and m['winning_reusable_root']['ram_bytes_identical'] == 10240
    assert sha(ep / 'winning-inputs.csv') == m['winning_inputs_sha256']
    d['references'].append(dict(path=(ep / 'manifest.json').relative_to(R).as_posix(),
        sha256=sha(ep / 'manifest.json'), bytes=(ep / 'manifest.json').stat().st_size))
    sys.path.insert(0, str(R / 'tools/playthroughs'))
    from roster_run import workspace_bytes
    used = workspace_bytes(R)
    assert used < 55_000_000_000
    d.update(status='ACTIVE_EL_UNCHANGED_EIGHT_NATURAL_UPGRADE_PROOFS_AND_COLD_WATER_PROGRESS',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), script_sha256=sha(__file__),
        coverage='Eight bounded EC Mario/Luigi Easy/Hard both-mapper natural growth/flower/fire startup replays pass,2250/2249 each,16 pickups with60frame freezes, real shots and hardware audio. EQ independently verifies95 receipt files and canonical traces/tapes. Full-arsenal, immunity/Star/source-art/waveform/finalEL media scope remains open.',
        MegaMan='EC EN clears five stages/2-2entry20885. EO corrected controller-only water hold then genuine Blooper0 collision at21081. EP independently cold-verifies21593/X800/Y112 and all10240RAM; ER is a fresh ordinary continuation, not yet fullclear.',
        Bill='G2 private source stable; specialist reports both mapper5192consumer +1152 mapping/cache/register reviews pass. G1 vine negative retained. Unchanged9978 inherited fixtures, matched cost, G2 ordinary and real-block/reset closure, freeze and finalEL union remain pending. Rejected F/N is absent from actual main.',
        active_specialists=['Private Bill G2 inherited source fixtures/cost/ordinary real-block closure',
            'Simon explicit C ordinary water P after cold F at20455/X1107/Y0',
            'New200MB bounded ordinary Mario/Luigi fireball enemy and Star lifecycle follow-up'],
        root_live_handles=[dict(handle=45750, tag='root49er-megaman-water', ROM='explicit frozen EC',
            scope='controller-only discovery-fast from independently cold-verified EP prefix; no final media')],
        workspace_bytes=used, goal_complete=False, accepted_release=False,
        QA_snapshot=dict(path='docs/qa/easy-hard-legacy-v49.md', sha256=sha(R / 'docs/qa/easy-hard-legacy-v49.md')))
    d['phase_budgets'].update(ordinary_Mario_upgrades=340_000_000, ordinary_Mario_combat=200_000_000)
    out.write_text(json.dumps(d, indent=2) + '\n')
    print(d['status'], sha(out), used)


if __name__ == '__main__':
    main()
