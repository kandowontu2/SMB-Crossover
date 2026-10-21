"""Passive accepted-jump/support receipts on the independently verified EL Bass tape."""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import sys

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    out = V / 'root49-el-bass-support-go'
    parent = R / 'build/roster-through-2-2/root49gl-bass-fixed-9-v0-mmc3'
    assert json.loads((parent / 'manifest.json').read_text())['verified_through_2_2']
    parser = V / 'agent49g-samus-crouch-fix-proposal-b/image.py'
    assert sha(parser) == '54fef35b891a96d5d0e36ca6cdeec9ee90b990666395714bc32e80cd1cabb0fb'
    spec = importlib.util.spec_from_file_location('bass_support_image', parser)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rom = V / 'root49-link-watch-ej/source/build/smb-crossover-mmc3.nes'
    assert sha(rom) == '2872f04b870ad72cb54b22a67a10333995151a501282c6535f3adfbe0ae32060'
    im = module.Image(rom)
    hooks = {'Launch': im.hook('Launch', 'ExpandedMovement'),
        'LandPlyr': im.hook('LandPlyr'), 'StopPlayerMove': im.hook('StopPlayerMove')}

    def data(name, size):
        s = im.sym(name)
        seg = im.segs[s['seg']]
        off = seg['ooffs'] + s['val'] - seg['start']
        return list(im.raw[off:off+size])

    adders = data('BlockBufferAdderData', 11)
    xadd = data('BlockBuffer_X_Adder', 90)
    yadd = data('BlockBuffer_Y_Adder', 90)
    feet = {n: dict(x=[xadd[adders[n]+1], xadd[adders[n]+2]],
        y=[yadd[adders[n]+1], yadd[adders[n]+2]]) for n in (3, 8)}
    assert all(v == dict(x=[2, 13], y=[32, 32]) for v in feet.values())
    out.mkdir(exist_ok=False)
    core = out / 'core.lua'
    core.write_text(r'''local C=assert(BASS_SUPPORT)
local frame,poll=0,0
local f=assert(io.open(ROSTER_CONFIG.out..'support-events.jsonl','w'))
local function r(n,i)if not L[n]then return -1 end;return emu.read(L[n]+(i or 0),emu.memType.nesDebug)end
local function tile(x,y)
 if y<32 or y>=240 then return 0 end
 return r('Block_Buffer_1',(x//256)%2*208+((y-32)//16)*16+(x%256)//16)
end
local function emit(name)
 if frame<540 or r('SelectedCharacter')~=9 or r('GameEngineSubroutine')~=8 then return end
 local x,y=r('Player_X_Position')+256*r('Player_PageLoc'),r('Player_Y_Position')
 local z={event=name,frame=frame+1,poll=poll,x=x,y=y,yHigh=r('Player_Y_HighPos'),
  state=r('Player_State'),yf=r('MmYFraction')+256*r('MmYFraction',1),
  world=r('WorldNumber'),level=r('LevelNumber'),fresh=r('XgFresh'),
  raw=r('SavedJoypadBits'),jumpUsed=r('XgJumpUsed'),dash=r('XgDash'),
  springAnimation=r('JumpspringAnimCtrl'),springGround=r('JumpspringOnGroundFlag'),
  feetY=y+32,tile2=tile(x+2,y+32),tile13=tile(x+13,y+32),
  R0=r('R0'),R1=r('R1'),R4=r('R4'),R6=r('R6'),R7=r('R7')}
 local a={}
 for k,v in pairs(z)do a[#a+1]=string.format('%q',k)..':'..(type(v)=='string'and string.format('%q',v)or tostring(v))end
 table.sort(a)
 local actors={}
 for i=0,5 do
  local t={i,r('Enemy_Flag',i),r('Enemy_ID',i),r('Enemy_State',i),
   r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),r('Enemy_Y_Position',i),
   r('PlatformCollisionFlag',i)}
  actors[#actors+1]='['..table.concat(t,',')..']'
 end
 a[#a+1]='"actors":['..table.concat(actors,',')..']'
 f:write('{'..table.concat(a,',')..'}'..string.char(10));f:flush()
end
for name,h in pairs(C.hooks)do
 emu.addMemoryCallback(function()
  local p=emu.convertAddress(h.address)
  if not p or p.memType~=emu.memType.nesPrgRom or p.address//8192~=h.physical_bank then return end
  for i,v in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==v,'Actual support hook8 '..name)end
  emit(name)
 end,emu.callbackType.exec,h.address)
end
emu.addEventCallback(function()frame=frame+1 end,emu.eventType.endFrame)
emu.addEventCallback(function()poll=poll+1 end,emu.eventType.inputPolled)
return dofile(C.guard)
''')
    guard = V / 'root49-el-bass-transfer-fd/guard.lua'
    policy = out / 'policy.lua'
    cfg = dict(hooks=hooks, guard=guard.as_posix())
    policy.write_text('BASS_SUPPORT='+module.lua(cfg)+'\nreturn dofile('+module.lua(core.as_posix())+')\n')
    command = [sys.executable, str(R / 'tools/playthroughs/roster_run.py'), '--character', '9',
        '--mapper', 'mmc3', '--rom', str(rom), '--tag', 'root49go-bass-support',
        '--policy', str(policy), '--prefix', str(parent / 'inputs.csv'),
        '--frames', '36000', '--timeout', '900', '--discovery-fast', '--workspace-cap-gb', '60']
    report = dict(script_sha256=sha(__file__), ROM=im.metadata(),
        source_full_manifest_sha256=sha(parent / 'manifest.json'),
        complete_fixed_prefix_sha256=sha(parent / 'inputs.csv'), hooks=hooks,
        actual_Bass_foot_adders=feet, actual_adder_table_values=adders,
        compiled_ExpandedCollisionAdder=im.hook('ExpandedCollisionAdder'),
        compiled_collision_source_sha256=sha(R / 'src/collision.s'),
        core_sha256=sha(core), guard_sha256=sha(guard), policy_sha256=sha(policy),
        command=command, emulated_writes=False, state_loads=False,
        classification_pending=True, runtime_changes=False, goal_complete=False)
    (out / 'binding.json').write_text(json.dumps(report, indent=2)+'\n')
    rc = subprocess.run(command, cwd=R).returncode
    (out / 'host-result.json').write_text(json.dumps(dict(exit=rc), indent=2)+'\n')
    raise SystemExit(rc)


if __name__ == '__main__':
    main()
