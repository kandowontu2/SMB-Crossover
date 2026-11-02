"""Compare controller jump/fire before the currently observed right-edge lock."""
from pathlib import Path
import json
import prepare_arthur_auth_fast_1101_v2 as P
from prepare_selected_native_packet_v1 import prepare,sha
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location

def main():
 ref=P.O/'native/controller.lua';base=ref.read_text();b=scoped_load(P.BASE)
 for name,rom in [('actions',P.O/'candidate.nes'),('actions-baseline',P.BASE)]:
  text=base
  text=text.replace("if phase=='play' and age>=120 then p.right=true end", """if phase=='play' then
  p.right=age>=120 and age<210
  p.a=(age>=145 and age<157) or (age>=175 and age<187)
  p.b=(age>=135 and age<147) or (age>=195 and age<207) or (age>=255 and age<267)
 end""")
  text=text.replace("elseif phase=='play' and age>=240 then", "elseif phase=='play' and age>=360 then")
  text=text.replace('local startx','local startx\nlocal startLives\nlocal minY=255\nlocal shotCalls=0')
  text=text.replace("frame=frame+1;age=age+1;", "frame=frame+1;age=age+1;if phase=='play' then minY=math.min(minY,r('Player_Y_Position')) end;")
  text=text.replace("shot('idle-start');state('play')", "startLives=r('NumberofLives');shot('idle-start');state('play')")
  text=text.replace("local passed=x>startx and", "local passed=x>startx and minY<160 and r('NumberofLives')==startLives and")
  text=text.replace("f=assert(io.open(OUTPUT..'result.json','w'));", "local g=assert(io.open(OUTPUT..'actions.json','w'));g:write(string.format('{\"minimum_y\":%d,\"lives_start\":%d,\"lives_end\":%d}',minY,startLives,r('NumberofLives')));g:close();f=assert(io.open(OUTPUT..'result.json','w'));")
  if name=='actions-baseline':
   q=json.loads((P.O/'assembly.json').read_text());old=f'emu.addMemoryCallback(authReturn,emu.callbackType.exec,{q["auth_restore"]+8})'
   assert text.count(old)==1;text=text.replace(old,'emu.addMemoryCallback(authReturn,emu.callbackType.exec,51170)')
  prepare(P.O/name,rom,text,[Path(__file__),ref],expected=sha(rom),timeout=120,scope='Same controller before/after:90physicalframesright, two A presses and three B presses before screen-edge block. Passrequiresjump,no life loss,movement.2PNGs,no statewrites. Attack outcomesneedinspection.')
if __name__=='__main__':main()
