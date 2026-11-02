"""Extend the proven opening controller to a bounded full-stage discovery."""
from pathlib import Path
import prepare_metal_storm_shots_1101_v35 as P
from prepare_selected_native_packet_v1 import prepare,sha
O=P.P.R/'build/metal-storm-route-1101-v37'

def main():
 O.mkdir(exist_ok=True)
 ref=P.P.R/'build/metal-storm-pipes-1101-v36/native-normal/controller.lua';t=ref.read_text()
 t=t.replace("local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end", "local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end")
 t=t.replace('local jt=0','local jt=0\nlocal cooldown=0')
 before='  ticks=ticks+1'
 extra="""  if pipe>4 and r('GameEngineSubroutine')==8 then
   local x,y=worldx(),r('Player_Y_Position')
   local function solid(wx,wy)
    if wy<32 or wy>=240 then return false end
    local v=r('Block_Buffer_1',(wx//256)%2*208+((wy-32)//16)*16+(wx%256)//16)
    return v~=0 and v~=0x23 and v~=0x26 and v~=0xc2
   end
   local danger=false
   local firing=false
   for i=0,5 do
    if r('Enemy_Flag',i)>0 and r('Enemy_Flag',i)<128 and r('Enemy_ID',i)<21 and (r('Enemy_State',i)&32)==0 then
     local dx=r('Enemy_PageLoc',i)*256+r('Enemy_X_Position',i)-x
     if dx>0 and dx<45 and math.abs(r('Enemy_Y_Position',i)-y)<50 then danger=true end
     if dx>=45 and dx<110 and math.abs(r('Enemy_Y_Position',i)-y)<36 then firing=true end
    end
   end
   if firing and r('Player_State')==0 and not jumping then pad.right=false end
   if cooldown>0 then cooldown=cooldown-1 end
   if not jumping and cooldown==0 and r('Player_State')==0 and
      (not solid(x+24,216) or solid(x+32,y+24) or danger) then jumping=true;jt=0 end
   if jumping then
    pad.a=jt<40;jt=jt+1
    if jt>20 and r('Player_State')==0 then jumping=false;cooldown=8;pad.a=false end
   end
  end
"""
 assert t.count(before)==1;t=t.replace(before,extra+before)
 condition="worldx()>=1000 and r('Player_Y_HighPos')==1 and r('Player_State')==0 and pipe==5"
 t=t.replace(condition,"r('WorldNumber')==0 and r('LevelNumber')==1 and r('GameEngineSubroutine')==8 and r('OperMode_Task')==3")
 t=t.replace("finish('four-pipe-progress')","finish('entered-1-2')")
 t=t.replace('age>=2300','age>=6000').replace('frame>3000','frame>6800')
 t=t.replace('age%20==0','age%40==0')
 prepare(O/'native-v3',P.O/'candidate.nes',t,[Path(__file__),ref],expected=sha(P.O/'candidate.nes'),timeout=150,scope='Controller-only full1-1 discovery using ordinary jumps and stopping to fire at nearby enemies. Pass requires active1-2 gameplay after flagpole/castle transition without losing life. No RAM writes.')
if __name__=='__main__':main()
