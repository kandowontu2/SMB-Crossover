"""Rerun five sequential native audio suites and compare the exact composition."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
from cv3_primary_sfx_compare_v1 import cadence, writes

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepared', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    assert not out.is_relative_to(ROOT)
    out.mkdir(exist_ok=False)
    prepared = args.prepared.resolve()
    build = json.loads((prepared / 'build-proof.json').read_text())
    assert build['passed'] and sha(prepared / 'candidate.nes') == build['ROM_sha256']
    capture = D / 'cv3-primary-sfx-v1/source-cpu-v2'
    packets = {}
    for name, rom, options in [
        ('baseline-full', 'baseline.nes', ['--observe']),
        ('candidate-full', 'candidate.nes', []),
        ('candidate-controls', 'candidate.nes', ['--controls']),
        ('baseline-bill', 'baseline.nes', ['--character', '3']),
        ('candidate-bill', 'candidate.nes', ['--character', '3'])]:
        command = [sys.executable, str(ROOT / 'tools/audit/cv3_primary_sfx_native_v1.py'),
                   '--rom', str(prepared / rom), '--capture', str(capture),
                   '--output', str(out / name)] + options
        with (out / (name + '-host.log')).open('w') as log:
            subprocess.run(command, check=True, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        packet = json.loads((out / name / 'native-proof.json').read_text())
        assert packet['passed'] and packet['ROM_sha256'] == sha(prepared / rom)
        packets[name] = packet
        print(json.dumps(dict(suite=name, passed=True, cases=len(packet['cases']))), flush=True)
    old, new = packets['baseline-full'], packets['candidate-full']
    matches = []
    for before, after in zip(old['cases'], new['cases']):
        assert before['name'] == after['name'] and before['durationUpdates'] == after['durationUpdates']
        if before['q']['kind'] == 'pressure':
            continue
        assert writes(before, False) == writes(after, False), before['name']
        if before['q']['kind'] == 'legacy':
            assert writes(before) == writes(after)
        matches.append(dict(case=before['name'], non_noise_writes_exact=len(writes(after, False)),
                            legacy_full_writes_exact=len(writes(after)) if before['q']['kind'] == 'legacy' else None))
    def count(rows):
        return dict(wall_frames=len(rows), zero_update_frames=sum(r['updates'] == 0 for r in rows),
                    draws=sum(r['draws'] for r in rows), updates=sum(r['updates'] for r in rows))
    before, after = [cadence(out / name) for name in ['baseline-full', 'candidate-full']]
    b, a = count(before), count(after)
    assert a['zero_update_frames'] <= b['zero_update_frames'] and a['draws'] >= b['draws']
    bp, ap = [count([r for r in rows if r['case'] == 15]) for rows in [before, after]]
    assert ap['draws'] >= bp['draws']
    bills = [packets[name] for name in ['baseline-bill', 'candidate-bill']]
    for before, after in zip(*[p['cases'] for p in bills]):
        def hardware(case):
            return [(r['age'], r['register'], r['value']) for r in case['apu'] if r['register'] not in [0x4014, 0x4016]]
        assert before['name'] == after['name']
        assert hardware(before) == hardware(after) and before['audioCycles'] == after['audioCycles']
    bc, ac = [count(cadence(out / name)) for name in ['baseline-bill', 'candidate-bill']]
    assert bc == ac
    cpu_path = prepared / 'cpu-v1/proof.json'
    cpu = json.loads(cpu_path.read_text())
    assert cpu['passed'] and cpu['ROM_sha256'] == build['ROM_sha256']
    native_count = sum(len(packets[name]['cases']) for name in ['candidate-full', 'candidate-controls', 'candidate-bill'])
    assert native_count == 22
    proof = dict(passed=True, adopted=False, goal_complete=False, ROM_sha256=build['ROM_sha256'],
                 parent_ROM_sha256=build['parent_ROM_sha256'], candidate_native_cases=native_count,
                 ordinary_CPU_cases=cpu['ordinary_full_AudioUpdate_cases'], restore_CPU_cases=cpu['restore_cases'],
                 matched_native_before=b, matched_native_after=a, pressure_before=bp, pressure_after=ap,
                 matched_nonpressure_music=matches,
                 non_noise_writes_exact=sum(r['non_noise_writes_exact'] for r in matches),
                 Bill_cadence_exact=ac, Bill_APU_and_audio_cycles_exact=True,
                 baseline_missing_source_cue_cases=[c['name'] for c in old['cases'] if c.get('sourceExact') is False],
                 source_receipts={str(p): sha(p) for p in [prepared / 'build-proof.json', cpu_path] +
                                  [out / name / 'native-proof.json' for name in packets]},
                 tool_sha256=sha(Path(__file__)),
                 scope='Exact current-build composition, staged native original noise schedules, ownership/interrupt/PPU guards and matched cadence. Original source register flush order/frame quantization remains adapted; no identical waveform, full-roster or campaign claim.')
    (out / 'proof.json').write_text(json.dumps(proof, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in proof.items() if k not in ['source_receipts', 'matched_nonpressure_music']}, indent=2))


if __name__ == '__main__':
    main()
