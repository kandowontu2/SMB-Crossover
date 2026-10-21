"""Independently cold-replay the ordinary successful first two Pit stages on Y."""
from pathlib import Path
import csv, hashlib, json, subprocess, sys
R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-whip-phase-y-pit-prefix-d'
Y = V / 'root49-easy-whip-phase-y'
C = R / 'build/roster-through-2-2/root49y-pit-discovery-c-6-v0-mmc3'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rows(path):
    with path.open() as f:
        return list(csv.DictReader(f))


def main():
    assert not H.exists()
    manifest = json.loads((C / 'manifest.json').read_text())
    assert manifest['controller_only'] and not manifest['memory_or_register_writes']
    assert manifest['result']['stage_entries']['0-2'] == 9256
    assert manifest['result']['failure'] == 'death' and manifest['result']['frames'] == 10089
    H.mkdir()
    policy = H / 'neutral.lua';policy.write_text('return function()return{}end\n')
    tag = 'root49y-pit-prefix-d'
    rom = Y / 'source/build/smb-crossover-mmc3.nes'
    argv = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'), '--character', '6', '--mapper', 'mmc3',
            '--rom', str(rom), '--tag', tag, '--replay', str(C / 'inputs.csv'), '--policy', str(policy),
            '--frames', '9600', '--timeout', '180', '--workspace-cap-gb', '50']
    log = H / 'native.log'
    with log.open('wb') as f:
        rc = subprocess.run(argv, cwd=R, stdout=f, stderr=subprocess.STDOUT).returncode
    D = R / 'build/roster-through-2-2' / (tag + '-6-v0-mmc3')
    result = json.loads((D / 'result.json').read_text()) if (D / 'result.json').exists() else None
    report = dict(status='REVIEWING_PARTIAL_ORDINARY_PIT_COLD_REPLAY', exit=rc, result=result,
                  script_sha256=sha(__file__), source_manifest_sha256=sha(C / 'manifest.json'),
                  full_input_sha256=sha(C / 'inputs.csv'), ROM_sha256=sha(rom), log_sha256=sha(log),
                  full_end_2_2_claim=False, record=False, goal_complete=False, csv_comparisons=[])

    def save():
        (H / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    assert rc == 1 and result['failure'] == 'frame limit' and result['frames'] == 9600 and result['deaths'] == 0
    assert result['stage_entries'] == {k: v for k, v in manifest['result']['stage_entries'].items() if v <= 9600}
    for name in ['inputs', 'trace', 'events', 'render', 'oam', 'chr', 'audio-events', 'scroll-writes', 'stomp-events']:
        a, b = rows(C / (name + '.csv')), rows(D / (name + '.csv'))
        assert b == a[:len(b)], name
        report['csv_comparisons'].append(dict(name=name, rows=len(b), exact_discovery_prefix=True,
                                              sha256=sha(D / (name + '.csv'))))
        save()
    trace = rows(D / 'trace.csv')
    active = [r for r in trace if r['world'] == '0' and r['level'] == '2' and r['engine'] == '8']
    assert len(active) > 25 and int(active[-1]['x']) > int(active[0]['x']) + 5
    report['active_1_3_frames'] = len(active)
    report['status'] = 'PASS_FRESH_FIXED_ORDINARY_PIT_1_1_1_2_AND_LIVE_1_3_PREFIX_ON_Y_MMC3'
    report['qualification'] = 'First two stages only, all nine passive CSV prefixes exact; intentional frame-limit stop before the later discovery death. No full six-stage or final recording claim.'
    save();print(report['status'], sha(H / 'report.json'), flush=True)


if __name__ == '__main__':
    main()
