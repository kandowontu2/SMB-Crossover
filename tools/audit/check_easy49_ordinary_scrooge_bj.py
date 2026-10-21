"""Transfer frozen S2 Scrooge controls to BE without changing emulated state."""
from pathlib import Path
import csv, hashlib, json, shutil, subprocess, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-pit-empty-be'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = H / 'ordinary-scrooge-bj'
    out.mkdir(exist_ok=False)
    assert sha(H / 'report.json') == 'bb45ec3ead04515ad6eb56a8164ca39590d0f2ec72e29f64f69a67f4da6e55bd'
    assert sha(H / 'freeze-bi.json') == '2442526554d3ac401a542d77998c5569681eb6929bbb6c0ea992a96159833078'
    build = json.loads((H / 'report.json').read_text())
    assert all(sha(H / 'source' / n) == h for n, h in build['source_hashes'].items())
    policy = out / 'policy.lua'
    policy.write_text('''-- Passive title-state receipt; fixed replay supplies all input.
local checked=false
emu.addEventCallback(function()
 if checked then return end
 local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
 if r('OperMode')~=1 or r('OperMode_Task')~=3 or r('GameEngineSubroutine')~=8 then return end
 assert(r('SelectedCharacter')==12 and r('CrossoverBehaviorVersion')==0,
        'Scrooge fixed replay must launch actual Easy/Scrooge')
 assert(r('PlayerOutlinesOff')==1,'Default shadows off')
 checked=true
 emu.log('ORDINARY SCROOGE title verified: mode=0 selected=12 shadows=0')
end,emu.eventType.endFrame)
local stop=emu.stop
function emu.stop(code)
 assert(checked,'Actual Scrooge title choice observed')
 stop(code)
end
return function()return {}end
''')
    report = dict(status='RUNNING_BE_ORDINARY_EASY_SCROOGE_BOTH_MAPPERS',
                  script_sha256=sha(__file__), build_sha256=sha(H / 'report.json'),
                  freeze_sha256=sha(H / 'freeze-bi.json'), policy_sha256=sha(policy), rows=[],
                  controller_only=True, emulated_changes=False, recorded=False,
                  accepted_release=False, goal_complete=False,
                  qualification='Foreign-character route transfer to private BE; final combined routes, media and all abilities remain required.')
    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    for mapper, parent_tag, expected_input in [
        ('mmc3', 'specialist49s2-scrooge-final-a', '3c1fbdf3ac12abb5878e5409859be89f26bb1a979011a0e1ab28da56e28541a4'),
        ('mmc5', 'specialist49s2-scrooge-m5-final-a', 'f864d22f699752975bc4b0068f6bb52e6764ccca26eb9b123128d21d5d1e5ada')]:
        original = R / 'build/roster-through-2-2' / (parent_tag + '-12-v0-' + mapper)
        parent = json.loads((original / 'manifest.json').read_text())
        replay = original / 'inputs.csv'
        assert sha(replay) == expected_input == parent['inputs_sha256']
        assert parent['verified_through_2_2'] and parent['result']['deaths'] == 0
        rom = H / 'source/build' / ('smb-crossover-' + mapper + '.nes')
        tag = 'root49bj-scrooge-fixed'
        argv = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'), '--character', '12',
                '--mapper', mapper, '--rom', str(rom), '--tag', tag, '--replay', str(replay),
                '--policy', str(policy), '--frames', '36000', '--timeout', '360', '--workspace-cap-gb', '50']
        with (out / (mapper + '-host.log')).open('wb') as stream:
            rc = subprocess.run(argv, cwd=R, stdout=stream, stderr=subprocess.STDOUT).returncode
        folder = R / 'build/roster-through-2-2' / (tag + '-12-v0-' + mapper)
        native_source = V / (rom.stem + '-run-' + tag + '-12-v0-' + mapper + '.log')
        native = out / (mapper + '-native.log')
        if native_source.exists():
            shutil.copyfile(native_source, native)
        path = folder / 'manifest.json'
        manifest = json.loads(path.read_text()) if path.exists() else None
        good = bool(rc == 0 and manifest and manifest['verified_through_2_2'] and manifest['full_frame_audit']
                    and manifest['result']['deaths'] == 0 and manifest['replay_sha256'] == expected_input
                    and native.exists() and 'ORDINARY SCROOGE title verified: mode=0 selected=12 shadows=0' in native.read_text())
        row = dict(mapper=mapper, exit=rc, passed=good, output=folder.relative_to(R).as_posix(),
                   rom_sha256=sha(rom), original_manifest_sha256=sha(original / 'manifest.json'),
                   inputs_sha256=expected_input, manifest_sha256=sha(path) if path.exists() else None,
                   native_log_sha256=sha(native) if native.exists() else None,
                   result=manifest.get('result') if manifest else None)
        if (folder / 'trace.csv').exists():
            old = list(csv.DictReader((original / 'trace.csv').open()))
            new = list(csv.DictReader((folder / 'trace.csv').open()))
            keys = ['world', 'level', 'area', 'x', 'y', 'state', 'power', 'buttons']
            assert all(k in old[0] and k in new[0] for k in keys), list(old[0])
            differences = [i + 1 for i, (a, b) in enumerate(zip(old, new)) if any(a[k] != b[k] for k in keys)]
            row['S2_trace_comparison'] = dict(fields=keys, original_frames=len(old), new_frames=len(new),
                                             differing_frame_count=len(differences), first_difference=differences[0] if differences else None)
        report['rows'].append(row)
        save()
        print(mapper, rc, good, row['result'], flush=True)
    assert all(sha(H / 'source' / n) == h for n, h in build['source_hashes'].items())
    good = len(report['rows']) == 2 and all(row['passed'] for row in report['rows'])
    report['status'] = 'PASS_BE_ORDINARY_EASY_SCROOGE_BOTH_MAPPERS' if good else 'RETAINED_BE_SCROOGE_REPLAY_NEGATIVE'
    save()
    print(report['status'], sha(out / 'report.json'), flush=True)
    return 0 if good else 1


if __name__ == '__main__':
    raise SystemExit(main())
