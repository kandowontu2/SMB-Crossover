"""Observe actual source projectile state and native target positions."""
from pathlib import Path
from prepare_selected_native_packet_v1 import prepare,sha
import prepare_shinobi_camera_1101_v20 as P
import prepare_shinobi_owning_graft_1101_v1 as S
O=P.R/'build/shinobi-shot-trace-1101-v22'
def main(ref=None,run='native'):
 O.mkdir(exist_ok=True);ref=ref or P.O/'native-jump/controller.lua';c=ref.read_text()
 lab=S.labels(P.R/'build/shinobi-hurt-layout-1101-v5/component.lbl')
 observer="""local observations,bounds={},{}
emu.addMemoryCallback(function()
 if r('SelectedCharacter')~=36 or r('CurrentBank')~=3 or r('CurrentBankC')~=2 or #bounds>=40 then return end
 local s=emu.getState();if s['cpu.y']~=28 then return end
 local function b(i)return emu.read(L['BoundingBox_UL_Corner']+i,emu.memType.nesDebug)end
 local x=s['cpu.x'];bounds[#bounds+1]=string.format('[%d,%d,%d,%d,%d,%d,%d,%d,%d,%d]',frame,x,b(x),b(x+1),b(x+2),b(x+3),b(28),b(29),b(30),b(31))
end,emu.callbackType.exec,L['SprObjectCollisionCore'])
emu.addMemoryCallback(function()
 if r('SelectedCharacter')~=36 or r('CurrentBank')~=3 or r('CurrentBankC')~=2 or frame<500 or frame>1100 or #observations>=160 then return end
 local function v(a)return emu.read(a,emu.memType.nesDebug)end
 local s=emu.getState();local x=s['cpu.x']
 observations[#observations+1]=string.format('[%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d]',frame,x,v(0xc413+x),v(0xc300+x),v(0xc379+x),v(0xc384+x),v(0xc38f+x),v(0xc39a+x),r('ScreenLeft_X_Pos'),r('Enemy_X_Position'),r('Enemy_Y_Position'),r('Enemy_State'))
end,emu.callbackType.exec,PC)
""".replace('PC',str(lab['ShNativeShotContact']))
 c=c.replace('emu.addEventCallback(function()',observer+'emu.addEventCallback(function()',1)
 c=c.replace('f:close();done=true;',"f:close();local z=assert(io.open(OUTPUT..'shots.json','w'));z:write('{\"shots\":['..table.concat(observations,',')..'],\"bounds\":['..table.concat(bounds,',')..']}');z:close();done=true;")
 prepare(O/run,P.O/'candidate.nes',c,[Path(__file__),ref],expected=sha(P.O/'candidate.nes'),timeout=150,scope='Read-only actual source shot contact entries,160 compact samples maximum. Same controller; no state writes.')
if __name__=='__main__':main()
