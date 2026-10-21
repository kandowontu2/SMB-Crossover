"""Replay accepted ordinary Mario controls on combined BQ, with a full audit."""
from pathlib import Path
import csv, hashlib, json, shutil, subprocess, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-combined-bq'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = H / 'ordinary-mario-cc'
    out.mkdir(exist_ok=False)
    handoff = V / 'specialist-mario-easy-hard-source-a/routes-k/mario-easy-full-route-handoff-a.json'
    assert sha(handoff) == '6010fa1b91afa81d08b2ab42f67b50c110db2968c1468b10f36c7ef8723810e9'
    accepted = json.loads(handoff.read_text())
    assert sha(H / 'report.json') == '2736ac1e4238d237fce859e18ae29f7ef137ed4b2f386e3078c2a2438021e838'
    build = json.loads((H / 'report.json').read_text())
    assert all(sha(H / 'source' / n) == h for n, h in build['source_hashes'].items())
    replay = R / accepted['fixed_inputs']
    assert sha(replay) == accepted['fixed_inputs_sha256']
    original = R / accepted['proofs'][0]['evidence']
    original_manifest = json.loads((original / 'manifest.json').read_text())
    policy = out / 'policy.lua'
    shutil.copyfile(original / 'policy.lua', policy)
    assert sha(policy) == original_manifest['policy_sha256']
    report = dict(status='RUNNING_BQ_FULL_ORDINARY_EASY_MARIO_BOTH_MAPPERS',
                  script_sha256=sha(__file__), build_sha256=sha(H / 'report.json'),
                  handoff_sha256=sha(handoff), inputs_sha256=sha(replay), policy_sha256=sha(policy), rows=[],
                  controller_only=True, emulated_changes=False, recorded=False, accepted_release=False, goal_complete=False,
                  qualifications=['Two native corner takeoffs from the accepted ordinary K route remain explicitly classified; no glitchless claim.',
                                  'This is a BQ interim candidate replay. Final integrated lossless recordings remain required.'])

    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    for mapper in ['mmc3', 'mmc5']:
        tag = 'root49cc-mario-fixed'
        rom = H / 'source/build' / ('smb-crossover-' + mapper + '.nes')
        argv = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'), '--character', '0', '--mapper', mapper,
                '--rom', str(rom), '--tag', tag, '--replay', str(replay), '--policy', str(policy),
                '--frames', '36000', '--timeout', '360', '--workspace-cap-gb', '50']
        host_log = out / (mapper + '-host.log')
        with host_log.open('wb') as stream:
            rc = subprocess.run(argv, cwd=R, stdout=stream, stderr=subprocess.STDOUT).returncode
        folder = R / 'build/roster-through-2-2' / (tag + '-0-v0-' + mapper)
        native_source = V / (rom.stem + '-run-' + tag + '-0-v0-' + mapper + '.log')
        native = out / (mapper + '-native.log')
        if native_source.exists():
            shutil.copyfile(native_source, native)
        manifest = json.loads((folder / 'manifest.json').read_text()) if (folder / 'manifest.json').exists() else None
        good = bool(rc == 0 and manifest and manifest['verified_through_2_2'] and manifest['full_frame_audit']
                    and manifest['result']['deaths'] == 0 and manifest['replay_sha256'] == sha(replay)
                    and native.exists() and 'ORDINARY MARIO title verified: mode=0 selected=0' in native.read_text())
        row = dict(mapper=mapper, exit=rc, passed=good, output=folder.relative_to(R).as_posix(),
                   result=manifest.get('result') if manifest else None,
                   manifest_sha256=sha(folder / 'manifest.json') if manifest else None,
                   native_log_sha256=sha(native) if native.exists() else None)
        if good:
            parent = next(p for p in accepted['proofs'] if p['mapper'] == mapper)
            old = list(csv.DictReader((R / parent['evidence'] / 'trace.csv').open()))
            new = list(csv.DictReader((folder / 'trace.csv').open()))
            keys = accepted['compared_movement_and_controller_fields']
            row['comparison_against_K'] = dict(fields=keys, before_frames=len(old), BQ_frames=len(new),
                differing_frames=[i + 1 for i, (a, b) in enumerate(zip(old, new)) if any(a[k] != b[k] for k in keys)])
            render = list(csv.DictReader((folder / 'render.csv').open()))
            row['frames_flagged_lagNmi'] = sum(int(frame['lagNmi']) for frame in render)
            row['dry_grounded_fresh_A_receipt_sha256'] = sha(folder / 'ordinary-fresh-grounded-a.csv')
            row['dry_receipts_exact_K'] = row['dry_grounded_fresh_A_receipt_sha256'] == parent['dry_fresh_grounded_a_receipt_sha256']
        report['rows'].append(row)
        save()
        print(mapper, rc, good, row.get('result'), row.get('comparison_against_K'), flush=True)
    assert all(sha(H / 'source' / n) == h for n, h in build['source_hashes'].items())
    good = len(report['rows']) == 2 and all(row['passed'] for row in report['rows'])
    report['status'] = 'PASS_BQ_ORDINARY_EASY_MARIO_BOTH_MAPPERS' if good else 'RETAINED_BQ_MARIO_REPLAY_NEGATIVE'
    save()
    print(report['status'], sha(out / 'report.json'), flush=True)
    return 0 if good else 1


if __name__ == '__main__':
    raise SystemExit(main())
