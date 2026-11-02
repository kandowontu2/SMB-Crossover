from pathlib import Path
import prepare_metal_storm_shots_1101_v35 as P
from prepare_selected_native_packet_v1 import prepare,sha

def main():
 ref=P.P.R/'tools/reference/metal_storm_natural_armor_1101_v26.lua';t=ref.read_text()
 a=t.index("  local x=worldx()");z=t.index('  ticks=ticks+1',a)
 t=t[:a]+"  pad.right=true;pad.b=(ticks%16)<8\n  if worldx()>=275 and route==0 then route=1;ticks=0 end\n  if route==1 then pad.a=ticks<20;pad.down=ticks>=20 and ticks<70\n   if ticks>=70 then route=2 end\n  end\n"+t[z:]
 t=t.replace("local trace,spawned,matured,got={},false,false,false", "local trace,spawned,matured,got={},false,false,false\nlocal killed=false")
 t=t.replace('local passed=got and spawned and matured and r(\'NumberofLives\')==initialLives', "local passed=killed and worldx()>=400 and r('NumberofLives')==initialLives")
 old='  for slot=0,5 do\n'
 t=t.replace(old,old+"   if emu.read(L.Enemy_Flag+slot,emu.memType.nesDebug)~=0 and emu.read(L.Enemy_ID+slot,emu.memType.nesDebug)==6 and (emu.read(L.Enemy_State+slot,emu.memType.nesDebug)&32)~=0 then\n    if not killed then killed=true;shot('enemy-defeated') end\n   end\n")
 t=t.replace("if r('PlayerStatus')==1 then got=true;finish('armor-collected')", "if killed and worldx()>=400 then finish('shot-kill-and-progress')")
 prepare(P.O/'native-shot-tail',P.O/'candidate.nes',t,[Path(__file__),ref],expected=sha(P.O/'candidate.nes'),timeout=90,scope='Cold menu selection and controller-only jump/downward-shot first Goomba, then reach worldX400 without life loss. Actual row34 object weapon tail. No RAM writes. Not full1-1.')
if __name__=='__main__':main()
