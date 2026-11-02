"""Collect the first flower and use its original torch on a selected candidate."""
from pathlib import Path
import argparse
import prepare_arthur_natural_flower_1101_v6 as F
from prepare_selected_native_packet_v1 import R,prepare,sha

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--rom',type=Path,required=True)
 ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
 a.output.mkdir(exist_ok=True)
 ref,t=F.controller()
 t=t.replace('local pickupCalls={}','local pickupCalls={}\nlocal torchStart=nil\nlocal torchCalls=0',1)
 marker='local function finish(passed,reason)\n'
 t=t.replace(marker,marker+''' local u=assert(io.open(OUTPUT..'torch.json','w'))
 u:write(string.format('{"collected_at_play_frame":%d,"original_torch_handler_calls":%d}',torchStart or -1,torchCalls));u:close()
''',1)
 marker="local function travel()\n local x,y=wx(),r('Player_Y_Position')\n"
 t=t.replace(marker,marker+''' if torchStart then local n=age-torchStart;return {b=n<12 or(n>=60 and n<72)}end
''',1)
 old="then finish(r('NumberofLives')==startLives,'Natural flower reached original torch pickup');return end"
 assert t.count(old)==1
 t=t.replace(old,"then if not torchStart then torchStart=age;shot('collected')end end\n  if torchStart and age-torchStart>=120 then finish(r('NumberofLives')==startLives and torchCalls>0,'Natural flower and original B-driven torch');return end",1)
 marker="emu.addMemoryCallback(function()\n if phase=='play' then mainCalls=mainCalls+1 end"
 hook='''emu.addMemoryCallback(function()
 local bank=assert(L.ArNativeTorch)<0xc000 and r('CurrentBank')or r('CurrentBankC')
 if phase=='play' and torchStart and bank==(assert(B.ArNativeTorch)|128)then torchCalls=torchCalls+1 end
end,emu.callbackType.exec,assert(L.ArNativeTorch))
'''
 assert t.count(marker)==1;t=t.replace(marker,hook+marker)
 t=t.replace("passed and 'stage-1-2'", "passed and 'powerup-complete'",1)
 prepare(a.output/'flower',a.rom,t,[Path(__file__),Path(F.__file__),ref],expected=sha(a.rom),timeout=150,allow_interactive=True,scope='Native2 controller-only firstflower approach unchanged untilcollection: require actual release/maturity, sourcepickup6/torch68 and no life loss, then two Bpresses and original ArNativeTorch handler afterpickup. Readonly observers; no emulated memory writes. FourPNG/1600playframe bound. Otherpowerups/fullstage remain separate.')
 full=ref.read_text().replace('local jumpStart=nil','local jumpStart=nil\nlocal jumpSecond=true',1)
 old='jumpStart=age;jumps=jumps+1\n   jumpReason='
 new='''jumpStart=age;jumps=jumps+1
   local climb=(x>=2096 and x<2184) or (x>=2336 and x<2424)
   jumpSecond=not(climb and y>112)
   jumpReason='''
 assert full.count(old)==1;full=full.replace(old,new)
 full=full.replace('b.a=t<6 or(t>=18 and t<27)','b.a=t<6 or(jumpSecond and t>=18 and t<27)')
 old="if r('NumberofLives')~=startLives then finish(false,'Life lost');return end"
 full=full.replace(old,old+"\n  if r('GameEngineSubroutine')==11 then finish(false,'Entered death engine');return end")
 prepare(a.output/'full11',a.rom,full,[Path(__file__),ref],expected=sha(a.rom),timeout=240,allow_interactive=True,scope='Exact existing successful Arthur stairs controller: actual cold menu, allfourpipes/threegaps/stairs/flag and active1-2, no life loss and immediate deathengine rejection. No state/helper writes; fourPNG/12frameCSV/9500globalframe bound. Regression after wallrepair, separatefromnaturalfloweruse.')

if __name__=='__main__':main()
