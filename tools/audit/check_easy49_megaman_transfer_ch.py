"""Test the retained ordinary Mega Man controls on the installed BY image."""
from pathlib import Path
import hashlib, json, subprocess, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-by-megaman-route-ch'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    checkpoint = R / 'build/checkpoints/roster-audit-v49-easy-hard-by/manifest.json'
    assert sha(checkpoint) == 'fe005475a409894834268bdd203efde78df0275a124a5d13def3bb6816f098c7'
    published = json.loads(checkpoint.read_text())
    assert all(sha(R / n) == h for n, h in published['source_hashes'].items())
    replay = R / 'build/roster-through-2-2/agent49-s2-mm-s-1-v0-mmc3/inputs.csv'
    assert sha(replay) == 'b57baac3b6d6b4103ce965c6ec0bd3462f9aab417116858e276ee9eb299add76'
    H.mkdir(exist_ok=False)
    policy = H / 'guard.lua'
    policy.write_text('''-- Passive identity guard; every input comes from the retained CSV.
local cfg=assert(ROSTER_CONFIG)
local frame,seen=0,false
local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end
emu.addEventCallback(function()
 frame=frame+1
 if r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
  assert(r('SelectedCharacter')==1,'Actual Mega Man selected')
  assert(r('CrossoverBehaviorVersion')==0,'Actual Easy behavior')
  assert(r('PlayerOutlinesOff')==1,'Default player outlines off')
  if not seen then
   seen=true
   local f=assert(io.open(cfg.out..'identity.json','w'))
   f:write('{"character":1,"mode":0,"frame":'..frame..',"controller_only":true}\\n');f:close()
   print('ORDINARY MEGAMAN actual mode0 selected1 outlinesOff')
  end
 end
end,emu.eventType.endFrame)
return function(c)return{}end
''')
    mapper = 'mmc3'
    rom = R / 'build' / ('smb-crossover-' + mapper + '.nes')
    expected = next(x for x in published['builds'] if x['mapper'] == mapper)
    assert sha(rom) == expected['artifacts']['nes']['sha256']
    report = dict(status='RUNNING_BY_ORDINARY_MEGAMAN_TRANSFER', script_sha256=sha(__file__),
                  checkpoint_sha256=sha(checkpoint), inputs_sha256=sha(replay), policy_sha256=sha(policy),
                  mapper=mapper, ROM_sha256=sha(rom), controller_only=True, recorded=False,
                  qualification='Retained S2 input stream is a transfer candidate, not a motion oracle for the new Easy physics/injury rules. Negative timing/control outcomes remain retained for adaptation.',
                  accepted_release=False, goal_complete=False)
    def save():
        (H / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    tag = 'root49ch-megaman-fixed'
    log_path = H / 'host.log'
    with log_path.open('wb') as log:
        rc = subprocess.run([sys.executable, str(R / 'tools/playthroughs/roster_run.py'), '--character', '1',
            '--mapper', mapper, '--rom', str(rom), '--tag', tag, '--replay', str(replay), '--policy', str(policy),
            '--frames', '36000', '--timeout', '300', '--workspace-cap-gb', '50'], cwd=R,
            stdout=log, stderr=subprocess.STDOUT).returncode
    folder = R / 'build/roster-through-2-2' / (tag + '-1-v0-' + mapper)
    result = json.loads((folder / 'result.json').read_text()) if (folder / 'result.json').exists() else None
    manifest = json.loads((folder / 'manifest.json').read_text()) if (folder / 'manifest.json').exists() else None
    good = bool(rc == 0 and manifest and manifest['verified_through_2_2'] and manifest['full_frame_audit']
                and result and result['deaths'] == 0 and (folder / 'identity.json').exists())
    report.update(status='PASS_BY_ORDINARY_MEGAMAN_MMC3' if good else 'RETAINED_BY_MEGAMAN_TRANSFER_NEGATIVE',
                  exit=rc, passed=good, result=result, output=folder.relative_to(R).as_posix(),
                  manifest_sha256=sha(folder / 'manifest.json') if manifest else None,
                  host_log_sha256=sha(log_path), identity=json.loads((folder / 'identity.json').read_text()) if (folder / 'identity.json').exists() else None)
    assert all(sha(R / n) == h for n, h in published['source_hashes'].items())
    save()
    print(report['status'], sha(H / 'report.json'), result, flush=True)
    return 0 if good else 1


if __name__ == '__main__':
    raise SystemExit(main())
