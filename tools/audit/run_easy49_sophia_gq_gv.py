"""Start an ordinary current-GQ Sophia route with read-only native ownership probes."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-gq-sophia-route-gv'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not H.exists()
    manifest = R / 'build/checkpoints/roster-audit-v49-link-ceiling-gq/manifest.json'
    assert sha(manifest) == 'b8d20e8cab676894da899801146554f310dc4c339453c7b0897cfe92833c623f'
    d = json.loads(manifest.read_text())
    assert len(d['source_hashes']) == 442
    assert all(sha(R / n) == value for n, value in d['source_hashes'].items())
    parser = V / 'agent49g-samus-crouch-fix-proposal-b/image.py'
    assert sha(parser) == '54fef35b891a96d5d0e36ca6cdeec9ee90b990666395714bc32e80cd1cabb0fb'
    spec = importlib.util.spec_from_file_location('sophia_gq_image', parser)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rom = V / 'agent-lsr-link-ceiling-c/source/build/smb-crossover-mmc3.nes'
    im = module.Image(rom)
    assert sha(rom) == d['builds'][0]['artifacts']['nes']['sha256']
    hooks = {name: im.hook(name) for name in ('GameLoop', 'ExpandedMovement',
        'EnemyToBGCollisionDet', 'PlayerEnemyCollision', 'FirebarCollision',
        'InjurePlayer', 'ForceInjury', 'KillPlayer')}
    base = R / 'tools/playthroughs/sophia_38d_policy.lua'
    source = base.read_text()
    assert not any(x in source for x in ('emu.write', 'loadSavestate', 'emu.setState'))
    H.mkdir()
    observer = H / 'observer.lua'
    observer.write_text('''local frame,poll,selector,mode=0,0,0,0
local regs={}
local function rd(a)return emu.read(a,emu.memType.nesDebug)end
local function r(n,i)return rd(assert(L[n],n)+(i or 0))end
emu.addMemoryCallback(function(_,v)selector=v&7;mode=(v>>6)&1 end,emu.callbackType.write,0x8000)
emu.addMemoryCallback(function(_,v)if selector>=6 then regs[selector]=v&63 end end,emu.callbackType.write,0x8001)
local function bank(pc)
 if pc>=0xe000 then return 63 elseif pc>=0xc000 then return mode==0 and62 or(regs[6]or-1)
 elseif pc>=0xa000 then return regs[7]or-1 elseif pc>=0x8000 then return mode==0 and(regs[6]or-1)or62 end
 return -1
end
local fields={'WorldNumber','LevelNumber','SelectedCharacter','CrossoverBehaviorVersion','Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State','PlayerStatus','PlayerSize','RgPower','RgPreviousButtons','InjuryTimer','ObjectOffset'}
local f=assert(io.open(ROSTER_CONFIG.out..'sophia-native-contacts.csv','w'))
f:write('frame,poll,event,cycle,cpuX,parentPC,parentBank,'..table.concat(fields,',')..',playerBox,actors\\n')
local identity=false
for name,h in pairs(SOPHIA_GQ_HOOKS)do
 emu.addMemoryCallback(function()
  if bank(h.address)~=h.physical_bank then return end
  for i,v in ipairs(h.bytes)do assert(rd(h.address+i-1)==v,'Actual current GQ native hook '..name)end
  if name=='GameLoop'or name=='ExpandedMovement'then
   if not identity and frame>=540 and r('OperMode')==1 and r('OperMode_Task')==3 and r('GameEngineSubroutine')==8 then
    assert(r('SelectedCharacter')==11 and r('CrossoverBehaviorVersion')==0 and r('PlayerOutlinesOff')==1,'Actual Sophia/Easy/outlines identity')
    identity=true;local q=assert(io.open(ROSTER_CONFIG.out..'sophia-identity.json','w'));q:write('{"observed":true,"frame":'..(frame+1)..',"character":11,"behavior":0,"outlinesOff":1}\\n');q:close()
   end
   return
  end
  if frame<540 then return end
  -- Ordinary body-collision entry is voluminous; record it only near a live body.
  if name=='EnemyToBGCollisionDet'then return end
  local s=emu.getState();local sp=s['cpu.sp'];local parent=(rd(0x100+((sp+1)&255))+256*rd(0x100+((sp+2)&255))+1)&65535
  local row={frame+1,poll,name,s['cpu.cycleCount'],s['cpu.x'],parent,bank(parent)}
  for _,n in ipairs(fields)do row[#row+1]=r(n)end
  local box={};for i=0,3 do box[#box+1]=r('BoundingBox_UL_Corner',i)end
  row[#row+1]=table.concat(box,':')
  local actors={}
  for i=0,5 do
   local a={i,r('Enemy_Flag',i),r('Enemy_ID',i),r('Enemy_State',i),r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),r('Enemy_Y_Position',i)}
   for j=0,3 do a[#a+1]=r('BoundingBox_UL_Corner',4*(i+1)+j)end
   actors[#actors+1]=table.concat(a,':')
  end
  row[#row+1]=table.concat(actors,';');f:write(table.concat(row,',')..'\\n');f:flush()
 end,emu.callbackType.exec,h.address)
end
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
emu.addEventCallback(function()poll=poll+1 end,emu.eventType.inputPolled)
return dofile(SOPHIA_GQ_BASE)
'''.replace('and62', 'and 62').replace('or62', 'or 62'))
    policy = H / 'policy.lua'
    policy.write_text('SOPHIA_GQ_HOOKS=' + module.lua(hooks) + '\nSOPHIA_GQ_BASE=' +
        module.lua(base.as_posix()) + '\nreturn dofile(' + module.lua(observer.as_posix()) + ')\n')
    command = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'),
        '--character', '11', '--mapper', 'mmc3', '--rom', str(rom),
        '--tag', 'root49gv-sophia-live', '--policy', str(policy), '--frames', '36000',
        '--timeout', '900', '--discovery-fast', '--workspace-cap-gb', '60']
    preparation = dict(status='PREPARED_ORDINARY_GQ_SOPHIA_CONTROLLER_DISCOVERY',
        script_sha256=sha(__file__), ROM=im.metadata(), hooks=hooks,
        base_policy=dict(path=base.relative_to(R).as_posix(), sha256=sha(base)),
        observer_sha256=sha(observer), policy_sha256=sha(policy),
        source442_and8_artifacts_expected_checkpoint_sha256=sha(manifest),
        phase_ceiling_bytes=500_000_000, workspace_ceiling_bytes=60_000_000_000,
        controller_only=True, emulated_writes=False, state_loads=False,
        command=command, accepted_release=False, goal_complete=False)
    (H / 'binding.json').write_text(json.dumps(preparation, indent=2) + '\n')
    rc = subprocess.run(command, cwd=R).returncode
    (H / 'host-result.json').write_text(json.dumps(dict(exit=rc), indent=2) + '\n')
    raise SystemExit(rc)


if __name__ == '__main__':
    main()
