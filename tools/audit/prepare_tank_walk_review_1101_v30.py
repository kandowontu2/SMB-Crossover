"""Bounded current-build walk observer for body/overlay and all power states."""
from pathlib import Path
import prepare_mario_the_tank_native_1101_v1 as N
R=Path(__file__).resolve().parents[2]

def main():
 (R/'build/tank-walk-review-1101-v30').mkdir(exist_ok=True)
 original=N.prepare
 def prepare(output,rom,controller,refs,**kw):
  controller=controller.replace("shot('selected');",'').replace("shot('gameplay-entry');",'')
  controller=controller.replace("local frame,age,phase,done,cycles=0,0,'title',false,0", "local frame,age,phase,done,cycles=0,0,'title',false,0\nlocal rows={}")
  controller=controller.replace("elseif phase=='walk' and age>=36 then", """elseif phase=='walk' then
  if age==1 or age==25 or age==49 then
   local status=math.floor((age-1)/24)
   emu.write(L['PlayerStatus'],status,emu.memType.nesDebug)
   emu.write(L['PlayerSize'],status==0 and 1 or 0,emu.memType.nesDebug)
  end
  local bytes={}
  for i=0,31 do bytes[#bytes+1]=string.format('%02x',emu.read(L['Sprite_Data']+i,emu.memType.nesDebug))end
  local chr={}
  for i=0,11 do chr[#chr+1]=tostring(emu.read(L['CurrentCHRBank']+i,emu.memType.nesDebug))end
  rows[#rows+1]=string.format('{"age":%d,"status":%d,"pose":%d,"anim":%d,"frame":%d,"oam":"%s","chr":[%s]}',age,r('PlayerStatus'),r('ObjectMetasprite'),r('PlayerAnimCtrl'),r('FrameCounter'),table.concat(bytes),table.concat(chr,','))
  if age==20 or age==44 or age==68 then shot('walk-'..age)end
  if age>=72 then
   local log=assert(io.open(OUTPUT..'walk-trace.json','w'));log:write('['..table.concat(rows,',')..']');log:close()
""")
  controller=controller.replace("shot('walking');",'').replace(" if frame>900 then", " end\n if frame>900 then")
  original(R/'build/tank-walk-review-1101-v30/native',rom,controller,[*refs,Path(__file__)],expected=kw['expected'],timeout=90,scope='Current ROM native walk diagnostic; explicit small/big/powered fixtures, 72 compact OAM/pose records and three PNGs. Not natural powerup progression.')
 N.prepare=prepare;N.main()
if __name__=='__main__':main()
