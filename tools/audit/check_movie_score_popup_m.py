"""Observe actual score-anchor writes during an unmodified controller replay."""
from pathlib import Path
import argparse,json,sys,csv
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools'));import run_mesen
a=argparse.ArgumentParser();a.add_argument('--tag',required=True);a.add_argument('--rom',type=Path);a.add_argument('--frames',type=int,default=4500);a.add_argument('--character',type=int,default=3);a.add_argument('--variant',type=int,default=0);q=a.parse_args()
P=R/'build/roster-through-2-2'/f'claude-final-video-{q.character}-v{q.variant}-mmc3';O=R/'build/verification'/q.tag;assert not O.exists();O.mkdir()
rom=q.rom.resolve()if q.rom else P/'smb-crossover-mmc3.nes'
cfg=json.loads((P/'manifest.json').read_text())['config'];cfg.update(out=O.as_posix()+'/',limit=q.frames,record=False,segmented=False,replay=(P/'inputs.csv').as_posix(),policy=(P/'policy.lua').as_posix(),audit=(O/'audit.lua').as_posix())
lua=lambda v:'nil'if v is None else str(v).lower()if isinstance(v,bool)else json.dumps(v)
(O/'run.lua').write_text('ROSTER_CONFIG={\n'+''.join(f'{k}={lua(v)},\n'for k,v in cfg.items())+'}\ndofile('+json.dumps((P/'harness.lua').as_posix())+')\n',encoding='utf-8')
audit=r'''return function(cfg)
 local f=assert(io.open(cfg.out..'score-anchors.csv','w'));f:write('frame,char,world,level,slot,enemyId,worldX,camera,staleRelative,expected,actual,correct\n')
 local frame=0;local pending
 local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end
 emu.addMemoryCallback(function()
  if frame<500 then return end
  local x=emu.getState()['cpu.x'];assert(x>=0 and x<=6)
  local wx=r('Enemy_X_Position',x)+256*r('Enemy_PageLoc',x)
  local cam=r('ScreenLeft_X_Pos')+256*r('ScreenLeft_PageLoc')
  pending={frame+1,r('SelectedCharacter'),r('WorldNumber'),r('LevelNumber'),x,r('Enemy_ID',x),wx,cam,r('Enemy_Rel_XPos'),(wx-cam)%256}
 end,emu.callbackType.exec,assert(L.SetupFloateyNumber))
 emu.addMemoryCallback(function(a,v)
  if not pending then return end
  assert(a==L.FloateyNum_X_Pos+pending[5],'Score anchor belongs to the actual target slot')
  pending[#pending+1]=v;pending[#pending+1]=v==pending[10]and 1 or 0;f:write(table.concat(pending,',')..'\n');pending=nil
 end,emu.callbackType.write,L.FloateyNum_X_Pos,L.FloateyNum_X_Pos+6)
 return {frame=function(n)frame=n end,finish=function()f:close()end}
end
'''
(O/'audit.lua').write_text(audit,encoding='utf-8')
exitcode=run_mesen.run(O/'run.lua',rom,timeout=120,emulator_options=['--nes.ramPowerOnState=AllZeros','--nes.randomizeCpuPpuAlignment=false','--nes.randomizeMapperPowerOnState=false'])
with(O/'score-anchors.csv').open(newline='')as f:anchors=list(csv.DictReader(f))
report=dict(exit=exitcode,rom=str(rom),anchors=len(anchors),wrong=[z for z in anchors if z['correct']=='0'],result=json.loads((O/'result.json').read_text()),ordinary_controller_replay=True,memory_writes=False)
(O/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
