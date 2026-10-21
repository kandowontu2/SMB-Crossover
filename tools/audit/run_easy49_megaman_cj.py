"""Ordinary Mega Man continuation from the independently verified CI branch."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-by-megaman-route-cj'
F = R / 'build/roster-through-2-2/search/root49-ci-megaman-11-pipe2-a'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    frozen = R / 'build/checkpoints/roster-audit-v49-easy-hard-by/manifest.json'
    assert sha(frozen) == 'fe005475a409894834268bdd203efde78df0275a124a5d13def3bb6816f098c7'
    build = json.loads(frozen.read_text())
    assert all(sha(R / n) == h for n, h in build['source_hashes'].items())
    branch = json.loads((F / 'manifest.json').read_text())
    verified = json.loads((F / 'coldboot-verified.json').read_text())
    assert branch['branch_coldboot_verified'] and verified['verified'] and verified['ram_bytes_identical'] == 10240
    prefix = F / 'winning-inputs.csv'
    assert sha(prefix) == branch['winning_inputs_sha256']
    assert branch['rom_sha256'] == '8c79f8f0e8f0c0a0d987d8d828aa2bcd377df89a5c4f4b4cf6c54984a3a947be'
    H.mkdir(exist_ok=False)
    base = H / 'base-policy.lua'
    shutil.copyfile(R / 'tools/playthroughs/megaman_bass_policy.lua', base)
    guard = H / 'guard.lua'
    shutil.copyfile(V / 'root49-by-megaman-route-ch/guard.lua', guard)
    policy = H / 'policy.lua'
    policy.write_text('local ignored=dofile(' + json.dumps(guard.as_posix()) + ')\n' +
        'local prior=assert(dofile(' + json.dumps(base.as_posix()) + '))\n' + '''
-- Ordinary buttons only. Shoot the two nearby Goombas from their right side.
local phase,age,quiet='combat',0,0
local f=assert(io.open(ROSTER_CONFIG.out..'mm-combat-control.csv','w'))
f:write('poll,x,y,power,phase,facing,shotTypes,enemies\\n')
return function(c)
 local b=prior(c)
 local enemies,live={},false
 for i=0,5 do
  local flag,id,st=c.r('Enemy_Flag',i),c.r('Enemy_ID',i),c.r('Enemy_State',i)
  local x=c.r('Enemy_X_Position',i)+256*c.r('Enemy_PageLoc',i)
  if flag>0 and flag<128 then
   enemies[#enemies+1]=table.concat({i,id,st,x,c.r('Enemy_Y_Position',i),c.r('MmEnemyHealthLo',i),c.r('MmEnemyHealthHi',i)},'/')
   if id==6 and st<2 and x>=700 and x<=870 then live=true end
  end
 end
 if c.world==0 and c.level==0 and c.x>=820 and c.x<920 and phase~='done' then
  age=age+1
  quiet=live and 0 or quiet+1
  if quiet>=20 then phase='done';print('MM ordinary early Goomba combat finished '..c.poll)
  else
   assert(age<600,'Bounded ordinary Goomba combat requires review')
   b={left=c.r('PlayerFacingDir')~=2,b=c.poll%8<4}
  end
 end
 local shots={}
 for i=0,3 do shots[#shots+1]=c.r('MmBulletType',i)end
 if c.poll%4==0 then
  f:write(table.concat({c.poll,c.x,c.y,c.status,phase,c.r('PlayerFacingDir'),table.concat(shots,'/'),table.concat(enemies,';')},',')..'\\n');f:flush()
 end
 return b
end
''')
    tag = 'root49cj-megaman-live'
    rom = R / 'build/smb-crossover-mmc3.nes'
    assert sha(rom) == branch['rom_sha256']
    argv = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'), '--character', '1', '--mapper', 'mmc3',
            '--rom', str(rom), '--tag', tag, '--prefix', str(prefix), '--policy', str(policy),
            '--frames', '36000', '--timeout', '300', '--workspace-cap-gb', '50']
    report = dict(status='RUNNING_BY_MEGAMAN_CJ_ORDINARY_DISCOVERY', script_sha256=sha(__file__),
                  checkpoint_sha256=sha(frozen), branch_manifest_sha256=sha(F / 'manifest.json'),
                  branch_verifier_sha256=sha(F / 'coldboot-verified.json'), prefix_sha256=sha(prefix),
                  policy_sha256=sha(policy), base_policy_sha256=sha(base), guard_sha256=sha(guard), argv=argv,
                  qualification='Controller discovery. CI branch independently cold-verified all10240RAM; current full continuation still needs an independent complete replay. No ordinary all-weapon/acquisition or all-enemy claim.',
                  recorded=False, controller_only=True, accepted_release=False, goal_complete=False)
    def save():
        (H / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    save()
    log_path = H / 'host.log'
    with log_path.open('wb') as log:
        rc = subprocess.run(argv, cwd=R, stdout=log, stderr=subprocess.STDOUT).returncode
    folder = R / 'build/roster-through-2-2' / (tag + '-1-v0-mmc3')
    result = json.loads((folder / 'result.json').read_text()) if (folder / 'result.json').exists() else None
    report.update(status='TERMINAL_BY_MEGAMAN_CJ_DISCOVERY', exit=rc, result=result,
                  output=folder.relative_to(R).as_posix(), host_log_sha256=sha(log_path))
    assert all(sha(R / n) == h for n, h in build['source_hashes'].items())
    save()
    print(report['status'], sha(H / 'report.json'), rc, result, flush=True)


if __name__ == '__main__':
    main()
