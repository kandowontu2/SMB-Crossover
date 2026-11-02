"""Continue verified Karnov traversal using low shots against grounded enemies."""
from pathlib import Path
from prepare_selected_native_packet_v1 import R,prepare,sha
O=R/'build/karnov-crouch-route-1102-v1'
def main():
    source=R/'build/wwf-helper-stable-1102-v2/native-karnov-regression/controller.lua'
    text=source.read_text()
    old="local won=x>=1140 and r('Player_State')==0 and r('GameEngineSubroutine')==8 and r('NumberofLives')==lives"
    assert text.count(old)==1
    text=text.replace(old,"local won=r('LevelNumber')==1 and r('WorldNumber')==0 and r('GameEngineSubroutine')==8")
    text=text.replace('"regression_crossing_complete":%s','"stage_complete":%s')
    marker=' emu.setInput(pad,0)';assert text.count(marker)==1
    insert="""
 if phase=='game' and r('GameEngineSubroutine')==8 and r('Player_State')==0 then
  local wx=r('Player_PageLoc')*256+r('Player_X_Position')
  for i=0,5 do
   local flag=emu.read(L.Enemy_Flag+i,emu.memType.nesDebug)
   local id=emu.read(L.Enemy_ID+i,emu.memType.nesDebug)
   local state=emu.read(L.Enemy_State+i,emu.memType.nesDebug)
   local ex=emu.read(L.Enemy_PageLoc+i,emu.memType.nesDebug)*256+emu.read(L.Enemy_X_Position+i,emu.memType.nesDebug)
   local ey=emu.read(L.Enemy_Y_Position+i,emu.memType.nesDebug)
   if flag>0 and flag<128 and id<21 and state&32==0 and ex>wx and ex-wx<100 and math.abs(ey-r('Player_Y_Position'))<48 then
    pad.right=false;pad.a=false;pad.down=true;pad.b=gameFrames%12<6;jumpAge=0;release=8;break
   end
  end
 end
"""
    import propose_wwf_generic_helper_1102_v1 as P
    import json
    b=P.scoped_load(P.BASE)
    text='\n'.join(f'L[{json.dumps(n)}]={P.address(b,n)}' for n in ['Enemy_Flag','Enemy_ID','Enemy_State','Enemy_PageLoc','Enemy_X_Position'])+'\n'+text
    text=text.replace(marker,insert+marker)
    O.mkdir(exist_ok=True)
    rom=R/'build/wwf-helper-stable-1102-v2/candidate2.nes'
    prepare(O/'native',rom,text,[Path(__file__),source],expected=sha(rom),timeout=240,allow_interactive=True,
        scope='Actual controller-only Karnov full1-1 attempt; existing native pipe lifts and original crouch shots. Historical standing shots passed above Goombas. Two PNG maximum, no ROM or RAM mutation; actual active1-2/no life loss required.')
if __name__=='__main__':main()
