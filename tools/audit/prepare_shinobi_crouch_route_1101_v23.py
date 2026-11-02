"""Use original low shuriken stance for short SMB enemies during traversal."""
from pathlib import Path
from prepare_selected_native_packet_v1 import prepare,sha
import prepare_shinobi_camera_1101_v20 as P
O=P.R/'build/shinobi-crouch-route-1101-v23'
def main():
 O.mkdir(exist_ok=True);ref=P.R/'build/shinobi-pipes-1101-v19/native/controller.lua';t=ref.read_text()
 t=t.replace('pad.b=(ticks%16)<8','pad.b=false')
 t=t.replace('local function r(n)return emu.read(assert(L[n],n),emu.memType.nesDebug)end','local function r(n,i)return emu.read(assert(L[n],n)+(i or 0),emu.memType.nesDebug)end')
 extra="""  if not jumping and r('Player_State')==0 then
   for i=0,5 do
    if r('Enemy_Flag',i)>0 and r('Enemy_Flag',i)<128 and r('Enemy_ID',i)<21 and (r('Enemy_State',i)&32)==0 then
     local dx=r('Enemy_PageLoc',i)*256+r('Enemy_X_Position',i)-worldx()
     if dx>20 and dx<130 and math.abs(r('Enemy_Y_Position',i)-r('Player_Y_Position'))<36 then
      pad.right=false;pad.down=true;pad.b=(ticks%24)<12
     end
    end
   end
  end
"""
 t=t.replace('  ticks=ticks+1',extra+'  ticks=ticks+1')
 prepare(O/'native',P.O/'candidate.nes',t,[Path(__file__),ref],expected=sha(P.O/'candidate.nes'),timeout=150,scope='Controller-only opening route stops and crouch-fires at short enemies. Original standing shot isY182, above Goomba; crouch shot isY196. No artificial shot/hitbox changes.')
if __name__=='__main__':main()
