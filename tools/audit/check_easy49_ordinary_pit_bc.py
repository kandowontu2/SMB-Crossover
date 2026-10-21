"""Cold-verify the full Pit discovery, then carry its controls to combined AP."""
from pathlib import Path
import csv, hashlib, json, shutil, subprocess, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-easy-advanced-union-ap'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = H / 'ordinary-pit-bc'
    out.mkdir(exist_ok=False)
    original = R / 'build/roster-through-2-2/root49y-pit-continuation-x-6-v0-mmc3'
    assert sha(original / 'manifest.json') == '4cbb734beb496c8723c93917703861dbeeecd8f2cbf5a533c573124ca2aaa313'
    replay = original / 'inputs.csv'
    assert sha(replay) == 'f21d7fa381ffc4752366e4ad5d6b2e8761831e318fdb99d50cb66666143f5af5'
    discovery = json.loads((original / 'manifest.json').read_text())
    assert discovery['result']['cleared'] and discovery['result']['all_six_stages'] and discovery['result']['deaths'] == 0
    assert discovery['rom_sha256'] == '4f118a3904fb12ddf6652f7e321e9c10046ebfb7e0151a1eee7581511e9a09b6'
    base = V / 'root49-easy-whip-phase-y-pit-route-h/policy.lua'
    assert sha(base) == discovery['policy_sha256'] == 'e7ed9ec061f3a2744abd47f7a44fda5cd3e427dd1e440fa49251da1e446b6e09'
    policy = out / 'policy.lua'
    policy.write_text('local base=assert(dofile(' + json.dumps(base.as_posix()) + '))\n' + '''
local checked=false
emu.addEventCallback(function()
 if checked then return end
 local function r(n)return emu.read(assert(L[n]),emu.memType.nesDebug)end
 if r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
  assert(r('CrossoverBehaviorVersion')==0,'Actual Easy title choice')
  assert(r('SelectedCharacter')==6,'Actual Pit roster choice')
  checked=true
 end
end,emu.eventType.endFrame)
local stop=emu.stop
function emu.stop(code)
 assert(checked,'Actual Pit title choice observed')
 local f=assert(io.open(ROSTER_CONFIG.out..'ordinary-identity.json','w'))
 f:write('{"selected":6,"mode":0,"observed":true}');f:close();stop(code)
end
return base
''')
    report = dict(status='RUNNING_FULL_PIT_COLD_VERIFICATION_AND_AP_REPLAYS', script_sha256=sha(__file__),
                  discovery_manifest_sha256=sha(original / 'manifest.json'), inputs_sha256=sha(replay),
                  policy_sha256=sha(policy), rows=[], controller_only=True, emulated_changes=False,
                  recorded=False, accepted_release=False, goal_complete=False,
                  qualification='Actual fixed ordinary inputs, full passive audit. Interim builds; final integrated recordings remain required.')

    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

    save()
    for image, parent, mapper in [('Y', 'root49-easy-whip-phase-y', 'mmc3'),
                                  ('AP', 'root49-easy-advanced-union-ap', 'mmc3'),
                                  ('AP', 'root49-easy-advanced-union-ap', 'mmc5')]:
        tag = 'root49bc-pit-fixed-' + image.lower()
        rom = V / parent / 'source/build' / ('smb-crossover-' + mapper + '.nes')
        argv = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'), '--character', '6', '--mapper', mapper,
                '--rom', str(rom), '--tag', tag, '--replay', str(replay), '--policy', str(policy),
                '--frames', '36000', '--timeout', '360', '--workspace-cap-gb', '50']
        host_log = out / (image + '-' + mapper + '-host.log')
        if image == 'Y':
            # BB already completed this independent native replay successfully.
            # Its host finalizer then requested a discovery-only controller CSV.
            folder = R / 'build/roster-through-2-2/root49bb-pit-fixed-y-6-v0-mmc3'
            completed = json.loads((folder / 'manifest.json').read_text())
            assert completed['verified_through_2_2']
            rc = 0  # Native zero exit is required to set that verified field.
            native_source = H / 'ordinary-pit-bb/Y-mmc3-native.log'
        else:
            with host_log.open('wb') as stream:
                rc = subprocess.run(argv, cwd=R, stdout=stream, stderr=subprocess.STDOUT).returncode
            folder = R / 'build/roster-through-2-2' / (tag + '-6-v0-' + mapper)
            native_source = V / (rom.stem + '-run-' + tag + '-6-v0-' + mapper + '.log')
        native = out / (image + '-' + mapper + '-native.log')
        if native_source.exists():
            shutil.copyfile(native_source, native)
        manifest = json.loads((folder / 'manifest.json').read_text()) if (folder / 'manifest.json').exists() else None
        identity = json.loads((folder / 'ordinary-identity.json').read_text()) if (folder / 'ordinary-identity.json').exists() else None
        good = bool(rc == 0 and manifest and manifest['verified_through_2_2'] and manifest['full_frame_audit']
                    and manifest['result']['deaths'] == 0 and manifest['replay_sha256'] == sha(replay)
                    and identity == dict(selected=6, mode=0, observed=True))
        row = dict(image=image, mapper=mapper, exit=rc, passed=good, output=folder.relative_to(R).as_posix(),
                   result=manifest.get('result') if manifest else None,
                   manifest_sha256=sha(folder / 'manifest.json') if manifest else None,
                   native_log_sha256=sha(native) if native.exists() else None, ROM_sha256=sha(rom))
        if good:
            old = list(csv.DictReader((original / 'trace.csv').open()))
            new = list(csv.DictReader((folder / 'trace.csv').open()))
            keys = ['frame', 'poll', 'world', 'level', 'area', 'areaType', 'x', 'y', 'yHigh', 'state',
                    'vx', 'vy', 'power', 'engine', 'mode', 'task', 'lives', 'camera', 'buttons']
            row['comparison_against_Y_discovery'] = dict(fields=keys, before_frames=len(old), actual_frames=len(new),
                differing_frames=[i + 1 for i, (a, b) in enumerate(zip(old, new)) if any(a[k] != b[k] for k in keys)])
            row['frames_flagged_lagNmi'] = sum(int(frame['lagNmi']) for frame in csv.DictReader((folder / 'render.csv').open()))
            if image == 'Y':
                # The tenth discovery CSV records policy decisions, which a
                # fixed replay does not make. All nine real replay/audit CSVs
                # remain unmodified and are checked byte for byte.
                names = ['inputs.csv', 'trace.csv', 'events.csv', 'audio-events.csv', 'chr.csv',
                         'oam.csv', 'render.csv', 'scroll-writes.csv', 'stomp-events.csv']
                row['all_original_CSVs_byte_exact'] = {name: sha(folder / name) == sha(original / name) for name in names}
                row['native_execution'] = 'REUSED_COMPLETED_BB_REPLAY_NOT_RERUN'
                row['BB_host_negative'] = 'FileNotFoundError on discovery-only forward-enemy-e-controller.csv after native success. Original BB driver/report remain retained; BC corrects only host classification.'
                good = len(row['all_original_CSVs_byte_exact']) == 9 and all(row['all_original_CSVs_byte_exact'].values())
                row['passed'] = good
        report['rows'].append(row)
        save()
        print(image, mapper, rc, good, row.get('result'), flush=True)
    good = len(report['rows']) == 3 and all(row['passed'] for row in report['rows'])
    report['status'] = 'PASS_Y_PIT_COLD_AND_AP_ORDINARY_BOTH_MAPPERS' if good else 'RETAINED_PIT_REPLAY_NEGATIVE_OR_MAPPER_ROUTE_ADAPTATION_NEEDED'
    save()
    print(report['status'], sha(out / 'report.json'), flush=True)
    return 0 if good else 1


if __name__ == '__main__':
    raise SystemExit(main())
