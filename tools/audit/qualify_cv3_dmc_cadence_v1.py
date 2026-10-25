"""Independently compare the held CV3 proposal with its exact accepted parent.

Runs one Mesen process at a time. Passing native guards does not waive a lost
draw or a changed frame schedule; both remain explicit qualification failures.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PARENT = '8ff245ae662059abbc77c5de517260032775b7ba881a5201b8b54686ccf08277'
CANDIDATE = 'e6baf465a4fb3981dc1d9f1bea64a129f1dbb8d2a8276f934a38eb9c00c0728c'
EXPECTED = {
    'cv3_dmc_complete_native_v1.py': '0e5303ed758e383f37e9f78dc4ff800266c5a523cb2a25df4ba9c503ff1e7870',
    'cv3_dmc_complete_native_v1.lua': '1644b53102c4b0f423f456f9102c89f7ef8be1a79c3dc1bb9b3f21a121b34302',
}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prepared', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    assert not out.is_relative_to(ROOT)
    assert sha(a.prepared/'baseline.nes') == PARENT
    assert sha(a.prepared/'candidate.nes') == CANDIDATE
    out.mkdir(parents=True, exist_ok=False)
    names = [*EXPECTED, 'z2_platform_native_qa.lua',
             'observe_chip_committed_write.py', 'run_mesen_isolated.py',
             'check_tmnt_render_oa.py', 'audit_lua_config_literals.py']
    hashes = {str(ROOT/'tools/audit'/n): sha(ROOT/'tools/audit'/n) for n in names}
    for n, expected in EXPECTED.items():
        assert hashes[str(ROOT/'tools/audit'/n)] == expected, n
    frozen = out/'frozen'
    frozen.mkdir()
    for n in names:
        shutil.copy2(ROOT/'tools/audit'/n, frozen/n)
    shutil.copy2(Path(__file__), frozen/Path(__file__).name)
    (out/'prelaunch-bindings.json').write_text(json.dumps(dict(
        baseline_ROM_sha256=PARENT, ROM_sha256=CANDIDATE,
        tools=hashes, qualifier_sha256=sha(Path(__file__)),
        scope='Prelaunch bindings; no run result or adoption.'), indent=2)+'\n', encoding='utf-8')
    receipts = {}
    comparisons = []
    for profile in ['basic', 'pressure']:
        runs = []
        for label, stem in [('baseline', 'baseline'), ('candidate', 'candidate')]:
            folder = out/(profile+'-'+label)
            cmd = [sys.executable, str(ROOT/'tools/audit/cv3_dmc_complete_native_v1.py'),
                   '--rom', str(a.prepared/(stem+'.nes')), '--output', str(folder),
                   '--character', '5', '--variant', '3', '--profile', profile, '--run']
            with (out/(profile+'-'+label+'-host.log')).open('w', encoding='utf-8') as log:
                subprocess.run(cmd, cwd=ROOT, check=True, stdout=log, stderr=subprocess.STDOUT)
            proof_path = folder/'native-proof.json'
            q = json.loads(proof_path.read_text(encoding='utf-8'))
            assert q['passed'] and q['ROM_sha256'] == (PARENT if label=='baseline' else CANDIDATE)
            for case in q['cases']:
                assert type(case['modeReadback']) is int
                assert case['modeReadback'] == case['q']['mode']
            receipts[str(proof_path)] = sha(proof_path)
            rows = list(csv.DictReader((folder/'cadence.csv').open()))
            runs.append((q, rows))
            print(json.dumps(dict(profile=profile, build=label, native_guards_pass=True)), flush=True)
        before, after = runs
        assert len(before[0]['cases']) == len(after[0]['cases'])
        cases = []
        for b, c in zip(before[0]['cases'], after[0]['cases']):
            assert b['name'] == c['name'] and b['modeReadback'] == c['modeReadback']
            cases.append(dict(name=b['name'], mode=b['modeReadback'],
                baseline_draws=b['draws'], candidate_draws=c['draws'],
                draw_delta=c['draws']-b['draws'],
                baseline_physical_frames=b['frames'], candidate_physical_frames=c['frames'],
                baseline_updates=b['durationUpdates'], candidate_updates=c['durationUpdates']))
        keys = [k for k in before[1][0] if k not in ['wall', 'cycle']]
        assert len(before[1]) == len(after[1])
        differences = [dict(row=i, baseline={k:b[k] for k in keys},
                            candidate={k:c[k] for k in keys})
                       for i, (b, c) in enumerate(zip(before[1], after[1]))
                       if any(b[k] != c[k] for k in keys)]
        (out/(profile+'-cadence-differences.json')).write_text(
            json.dumps(differences, indent=2)+'\n', encoding='utf-8')
        comparisons.append(dict(profile=profile, cases=cases,
            per_frame_rows=len(before[1]), differing_frame_rows=len(differences),
            cadence_rows_exact=not differences,
            no_draw_loss=all(c['draw_delta']>=0 for c in cases),
            physical_frames_and_updates_exact=all(
                c['baseline_physical_frames']==c['candidate_physical_frames'] and
                c['baseline_updates']==c['candidate_updates'] for c in cases)))
    assert all(sha(Path(path))==value for path,value in hashes.items())
    passed = all(c['cadence_rows_exact'] and c['no_draw_loss'] and
                 c['physical_frames_and_updates_exact'] for c in comparisons)
    result = dict(passed=passed, native_guards_passed=True, adopted=False,
        goal_complete=False, ROM_sha256=CANDIDATE, baseline_ROM_sha256=PARENT,
        comparisons=comparisons, receipts=receipts, tools=hashes,
        qualifier_sha256=sha(Path(__file__)),
        scope='Four fresh independent native Alucard runs, each actual numeric Easy/Hard mode. '
              'Controller primary/contact owners and explicitly staged six-Goomba cue-free pressure. '
              'Exact actual sample/DAC, bank/NMI/IRQ/SMC/SP/OAM/CHR guards are separate from '
              'draw/cadence acceptance. Any lost draw or changed frame row prevents qualification. '
              'No campaign, audible waveform, full-roster or universal lag claim.')
    (out/'proof.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if passed else 1)


if __name__ == '__main__':
    main()
