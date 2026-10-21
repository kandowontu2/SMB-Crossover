"""Read-only actual-bank/eight-byte Mega Man injury ownership observer."""
from pathlib import Path
import hashlib
import importlib.util
import json

R = Path(__file__).resolve().parents[2]
V = R / 'build/verification'
H = V / 'root49-du-megaman-injury-dx'
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not H.exists()
    parser = V / 'agent49g-samus-crouch-fix-proposal-b/image.py'
    assert sha(parser) == '54fef35b891a96d5d0e36ca6cdeec9ee90b990666395714bc32e80cd1cabb0fb'
    spec = importlib.util.spec_from_file_location('injury_dx_image', parser)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    rom = V / 'root49-body-victory-union-dq/source/build/smb-crossover-mmc3.nes'
    assert sha(rom) == '2af5234c1a15a96e85779db49ce10c724387ae9bfdadab6ef82ed19d961460b0'
    im = mod.Image(rom)
    hooks = {n: im.hook(n) for n in ('InjurePlayer', 'ForceInjury', 'KillPlayer')}
    H.mkdir()
    base = V / 'root49-by-megaman-route-dl/policy.lua'
    core = r'''
local frame,poll,selected,mode=0,0,0,0
local regs={}
emu.addMemoryCallback(function(_,v) selected=v&7;mode=(v>>6)&1 end,emu.callbackType.write,0x8000)
emu.addMemoryCallback(function(_,v) if selected>=6 then regs[selected]=v&63 end end,emu.callbackType.write,0x8001)
local function bank(pc)
 if pc>=0xe000 then return 63 end
 if pc>=0xc000 then return mode==0 and 62 or(regs[6]or-1)end
 if pc>=0xa000 then return regs[7]or-1 end
 return mode==0 and(regs[6]or-1)or 62
end
local function r(n,i) return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
local fields={'WorldNumber','LevelNumber','SelectedCharacter','CrossoverBehaviorVersion','Player_X_Position','Player_PageLoc','Player_Y_Position','Player_State','PlayerStatus','PlayerSize','MmSliding','MmRenderPose','InjuryTimer','ObjectOffset'}
local f=assert(io.open(ROSTER_CONFIG.out..'mm-injury-owner.csv','w'))
f:write('frame,poll,event,cycle,cpuX,'..table.concat(fields,',')..',playerBox,actors\n')
for name,h in pairs(INJURY_DX_HOOKS)do
 emu.addMemoryCallback(function()
  if bank(h.address)~=h.physical_bank then return end
  for i,b in ipairs(h.bytes)do assert(emu.read(h.address+i-1,emu.memType.nesDebug)==b,'Actual injury hook bytes')end
  local s=emu.getState();local row={frame+1,poll,name,s['cpu.cycleCount'],s['cpu.x']}
  for _,n in ipairs(fields)do row[#row+1]=r(n)end
  local box={};for i=0,3 do box[#box+1]=r('BoundingBox_UL_Corner',i)end
  row[#row+1]=table.concat(box,':')
  local actors={}
  for i=0,5 do
   local a={i,r('Enemy_Flag',i),r('Enemy_ID',i),r('Enemy_State',i),r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i),r('Enemy_Y_Position',i),r('MmEnemyHealthLo',i),r('MmEnemyHealthHi',i)}
   local ofs=4*(i+1);for j=0,3 do a[#a+1]=r('BoundingBox_UL_Corner',ofs+j)end
   actors[#actors+1]=table.concat(a,':')
  end
  row[#row+1]=table.concat(actors,';');f:write(table.concat(row,',')..'\n');f:flush()
 end,emu.callbackType.exec,h.address)
end
emu.addEventCallback(function() frame=frame+1 end,emu.eventType.endFrame)
emu.addEventCallback(function() poll=poll+1 end,emu.eventType.inputPolled)
return dofile(INJURY_DX_BASE)
'''
    (H / 'observer.lua').write_text(core)
    (H / 'policy.lua').write_text('INJURY_DX_HOOKS=' + mod.lua(hooks) + '\nINJURY_DX_BASE=' + mod.lua(base.as_posix()) + '\ndofile(' + mod.lua((H / 'observer.lua').as_posix()) + ')\n')
    # Preserve the controller return value; callbacks alone suffice for replay,
    # and this wrapper must also support later ordinary discovery continuations.
    p = H / 'policy.lua'
    p.write_text(p.read_text().replace('\ndofile(', '\nreturn dofile('))
    binding = dict(script_sha256=sha(__file__), ROM=im.metadata(), hooks=hooks,
                   parser_sha256=sha(parser), base_policy_sha256=sha(base),
                   observer_sha256=sha(H / 'observer.lua'), policy_sha256=sha(p),
                   emulated_writes=False, registers_written=False, state_loads=False)
    (H / 'binding.json').write_text(json.dumps(binding, indent=2) + '\n')
    print('PASS_BOUND_READ_ONLY_DQ_INJURY_OBSERVER', sha(H / 'binding.json'))


if __name__ == '__main__':
    main()
