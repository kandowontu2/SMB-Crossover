"""Keep stair climbing to one jump; reserve the double jump for the valley."""
from pathlib import Path
import prepare_arthur_camera_1101_v3 as P
from prepare_selected_native_packet_v1 import prepare,sha


def main():
 ref=P.P.R/'tools/reference/arthur_full11_native_1101_v3.lua';text=ref.read_text()
 text=text.replace('local jumpStart=nil','local jumpStart=nil\nlocal jumpSecond=true',1)
 old='jumpStart=age;jumps=jumps+1\n   jumpReason='
 new='''jumpStart=age;jumps=jumps+1
   local climb=(x>=2096 and x<2184) or (x>=2336 and x<2424)
   jumpSecond=not(climb and y>112)
   jumpReason='''
 assert text.count(old)==1;text=text.replace(old,new)
 text=text.replace('b.a=t<6 or(t>=18 and t<27)','b.a=t<6 or(jumpSecond and t>=18 and t<27)')
 old="if r('NumberofLives')~=startLives then finish(false,'Life lost');return end"
 text=text.replace(old,old+"\n  if r('GameEngineSubroutine')==11 then finish(false,'Entered death engine');return end")
 prepare(P.O/'full11-stairs',P.O/'candidate.nes',text,[Path(__file__),ref],expected=sha(P.O/'candidate.nes'),timeout=240,scope='Controller-only full1-1 successor:single32pxclimbjumps untilleftstairpeak, thenexisting64pxdoublejump forvalley. SameROM. Originalfailedfull11unchanged. Engine11failsimmediately; a separatepit-death packet investigates progression. No state/helper writes;4PNGs,12-frameCSV.')


if __name__=='__main__':main()
