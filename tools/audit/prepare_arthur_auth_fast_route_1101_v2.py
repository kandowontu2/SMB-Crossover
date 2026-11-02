"""Bounded first-enemy/first-pipe controller regression for root's queue."""
from pathlib import Path
import prepare_arthur_auth_fast_1101_v2 as P
from prepare_selected_native_packet_v1 import prepare,sha

def main():
 ref=P.O/'native/controller.lua';text=ref.read_text()
 text=text.replace('local startx','local startx\nlocal minY=255\nlocal jumpStarted=false\nlocal jumpAge=0\nlocal startLives\nlocal function worldx()return r(\'Player_X_Position\')+256*r(\'Player_PageLoc\')end')
 # Insert controller state before callback definition so Lua closes over the
 # locals rather than resolving globals.
 start=text.index('local startx\n');end=text.index('emu.addEventCallback(function()',start)
 decl=text[start:end];text=text[:start]+text[end:]
 pos=text.index('emu.addEventCallback(function()');text=text[:pos]+decl+text[pos:]
 text=text.replace("if phase=='play' and age>=120 then p.right=true end", """if phase=='play' and age>=120 then
  p.right=true;p.b=true
  if not jumpStarted and worldx()>=385 then jumpStarted=true;jumpAge=age end
  if jumpStarted and age-jumpAge<16 then p.a=true end
 end""")
 text=text.replace("frame<=1000", "frame<=1400")
 text=text.replace("frame=frame+1;age=age+1;", "frame=frame+1;age=age+1;if phase=='play' then minY=math.min(minY,r('Player_Y_Position')) end;")
 text=text.replace("shot('idle-start');state('play')", "startLives=r('NumberofLives');shot('idle-start');state('play')")
 text=text.replace("elseif phase=='play' and age>=240 then", "elseif phase=='play' and (worldx()>520 or age>=780) then")
 text=text.replace("local passed=x>startx and", "local passed=x>520 and minY<160 and r('NumberofLives')==startLives and")
 text=text.replace("f=assert(io.open(OUTPUT..'result.json','w'));", "local g=assert(io.open(OUTPUT..'movement.json','w'));g:write(string.format('{\"minimum_y\":%d,\"lives_start\":%d,\"lives_end\":%d,\"first_pipe_cleared\":%s}',minY,startLives,r('NumberofLives'),tostring(x>520)));g:close();f=assert(io.open(OUTPUT..'result.json','w'));")
 prepare(P.O/'terrain',P.O/'candidate.nes',text,[Path(__file__),ref],expected=sha(P.O/'candidate.nes'),timeout=150,scope='Actual cold Arthur,held primary fire on approach, jump at worldX385 across first1-1pipe, stop beyond520 or780play frames. Pass requires pipe clear,jump,andno life loss.2PNGs,no state writes. Not full-stage.')
if __name__=='__main__':main()
