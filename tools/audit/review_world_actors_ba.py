"""Replay a retained movie without writes and inspect actual world/render owners."""
from pathlib import Path
import argparse, csv, hashlib, json, sys

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / 'tools'))
import run_mesen

p = argparse.ArgumentParser()
p.add_argument('--character', type=int, required=True)
p.add_argument('--variant', type=int, default=0)
p.add_argument('--frames', type=int, required=True)
p.add_argument('--tag', required=True)
a = p.parse_args()
P = R / 'build/roster-through-2-2' / f'claude-final-video-{a.character}-v{a.variant}-mmc3'
O = R / 'build/verification' / a.tag
assert not O.exists()
O.mkdir()
manifest = json.loads((P / 'manifest.json').read_text())
cfg = manifest['config'].copy()
cfg.update(limit=a.frames, out=O.as_posix() + '/', record=False, segmented=False,
           audit=(O / 'audit.lua').as_posix(), replay=(P / 'inputs.csv').as_posix(),
           policy=(P / 'policy.lua').as_posix())
lua = lambda v: 'nil' if v is None else str(v).lower() if isinstance(v, bool) else json.dumps(v)
(O / 'run.lua').write_text('ROSTER_CONFIG={\n' + ''.join(f'{k}={lua(v)},\n' for k, v in cfg.items()) +
    '}\ndofile(' + json.dumps((P / 'harness.lua').as_posix()) + ')\n', encoding='utf-8')
audit = r'''return function(cfg)
 local base=assert(dofile(ORIGINAL_AUDIT))(cfg)
 local frame,depth=0,0
 local files={}
 local function file(n,h)local f=assert(io.open(cfg.out..n..'.csv','w'));f:write(h..'\n');files[#files+1]=f;return f end
 local actors=file('actors','frame,world,level,areaType,camera,slot,id,flag,state,x,y,yHigh,metasprite,parts,spin,spinLow,spinSpeed')
 local draws=file('actor-draws','frame,world,level,object,metasprite,id,flag,state,x,y')
 local bars=file('firebar-oam','frame,world,level,camera,slot,id,flag,parts,positions,oamHex')
 local changes=file('actor-flags','frame,world,level,slot,oldFlag,newFlag,id,metasprite,x,y,pc,bank')
 local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
 local function x(i)return r('Enemy_X_Position',i)+256*r('Enemy_PageLoc',i)end
 local function camera()return r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')end
 local function play()return frame>=500 and r('OperMode')==1 and r('OperMode_Task')==3 end
 for _,pc in ipairs({L.NonMaskableInterrupt,L.IrqScrollSplit})do emu.addMemoryCallback(function()depth=depth+1 end,emu.callbackType.exec,assert(pc))end
 for _,pc in ipairs({L.NonMaskableInterrupt_RTI,L.IrqScrollSplit_RTI})do emu.addMemoryCallback(function()depth=depth-1;assert(depth>=0)end,emu.callbackType.exec,assert(pc))end
 emu.addMemoryCallback(function(addr,value)
  if not play()or depth~=0 then return end
  local i=addr-L.Enemy_Flag;local old=r('Enemy_Flag',i)
  if old==value then return end
  local s=emu.getState()
  changes:write(table.concat({frame+1,r('WorldNumber'),r('LevelNumber'),i,old,value,r('Enemy_ID',i),r('EnemyMetasprite',i),x(i),r('Enemy_Y_Position',i),s['cpu.pc'],r('CurrentBank')},',')..'\n')
 end,emu.callbackType.write,L.Enemy_Flag,L.Enemy_Flag+5)
 emu.addMemoryCallback(function()
  if not play()or depth~=0 or r('CurrentBank')%128~=B.DrawAllMetasprites then return end
  for i=0,5 do
   actors:write(table.concat({frame+1,r('WorldNumber'),r('LevelNumber'),r('AreaType'),camera(),i,r('Enemy_ID',i),r('Enemy_Flag',i),r('Enemy_State',i),x(i),r('Enemy_Y_Position',i),r('Enemy_Y_HighPos',i),r('EnemyMetasprite',i),r('FirebarPartCount',i),r('FirebarSpinState_High',i),r('FirebarSpinState_Low',i),r('FirebarSpinSpeed',i)},',')..'\n')
  end
 end,emu.callbackType.exec,L.DrawAllMetasprites)
 emu.addMemoryCallback(function()
  if not play()or depth~=0 or r('CurrentBank')%128~=B.DrawMetasprite then return end
  local s=emu.getState();local obj=s['cpu.y'];local id,flag,state,xx,yy=-1,-1,-1,-1,-1
  if obj>=1 and obj<=6 then local i=obj-1;id=r('Enemy_ID',i);flag=r('Enemy_Flag',i);state=r('Enemy_State',i);xx=x(i);yy=r('Enemy_Y_Position',i)end
  if s['cpu.x']==L.METASPRITE_BULLET_BILL or(id>=0x1b and id<0x23)then
   draws:write(table.concat({frame+1,r('WorldNumber'),r('LevelNumber'),obj,s['cpu.x'],id,flag,state,xx,yy},',')..'\n')
  end
 end,emu.callbackType.exec,L.DrawMetasprite)
 emu.addMemoryCallback(function()
  if not play()or depth~=0 or r('CurrentBank')%128~=B.DrawWorldFirebars then return end
  local bytes={};for j=0,255 do bytes[#bytes+1]=string.format('%02x',r('Sprite_Data',j))end
  local hex=table.concat(bytes)
  for i=0,5 do
   local id=r('Enemy_ID',i);local flag=r('Enemy_Flag',i)
   if id>=0x1b and id<0x23 and flag>0 and flag<128 then
    local positions={};local count=r('FirebarPartCount',i)
    if count<=12 then for j=0,count-1 do positions[#positions+1]=r('FirebarPartX',i*12+j)..':'..r('FirebarPartY',i*12+j)end end
    bars:write(table.concat({frame+1,r('WorldNumber'),r('LevelNumber'),camera(),i,id,flag,count,table.concat(positions,';'),hex},',')..'\n')
   end
  end
 end,emu.callbackType.exec,L.WorldFirebarsOamReady)
 return{failure=base.failure,frame=function(n)frame=n;base.frame(n)end,
  finish=function()base.finish();for _,f in ipairs(files)do f:close()end end}
end
'''.replace('ORIGINAL_AUDIT', json.dumps((P / 'audit.lua').as_posix()))
(O / 'audit.lua').write_text(audit, encoding='utf-8')
rom = P / 'smb-crossover-mmc3.nes'
assert hashlib.sha256(rom.read_bytes()).hexdigest() == manifest['rom_sha256']
code = run_mesen.run(O / 'run.lua', rom, timeout=200, emulator_options=[
    '--nes.ramPowerOnState=AllZeros', '--nes.randomizeCpuPpuAlignment=false',
    '--nes.randomizeMapperPowerOnState=false'])
result = json.loads((O / 'result.json').read_text()) if (O / 'result.json').exists() else None
literal = False
if result:
    original = (P / 'trace.csv').read_bytes().splitlines(keepends=True)
    literal = (O / 'trace.csv').read_bytes() == b''.join(original[:result['frames']+1])
    assert literal, 'Read-only replay must match the retained movie trace, including cycle counts'
summary = dict(exit=code, result=result, rom_sha256=manifest['rom_sha256'],
    trace_literal_to_original_prefix=literal, emulated_writes=False,
    input_sha256=hashlib.sha256((P / 'inputs.csv').read_bytes()).hexdigest(),
    scope='Read-only ordinary controller replay of retained movie. Actor and actual draw calls observed. No gameplay alteration or new A/V recording.', goal_complete=False)
(O / 'summary.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
print(json.dumps(summary, indent=2))
