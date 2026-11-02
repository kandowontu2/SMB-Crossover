"""Separate frozen controls, real overheat/recovery, and full-stage packets."""
from pathlib import Path
import json
from prepare_selected_native_packet_v1 import R,prepare,sha
from prepare_excitebike_dispatch_1101_v1 import O


def observed(text):
    marker='local rawA,rawC=0,0'
    assert text.count(marker)==1
    text=text.replace(marker,marker+'''
local heatSeen,recoverySeen,cooled,resumed=false,false,false,false
local heatStartX,releaseX=nil,nil
local heatEvents,lastHeatState={},nil
''')
    marker="local function finish(passed,reason)\n"
    assert text.count(marker)==1
    text=text.replace(marker,marker+'''
 local q=assert(io.open(OUTPUT..'heat.json','w'))
 q:write(string.format('{"heat_seen":%s,"recovery5_seen":%s,"returned_recovery0":%s,"resumed_motion":%s,"heat_start_x":%d,"released_x":%d,"events":[%s]}',tostring(heatSeen),tostring(recoverySeen),tostring(cooled),tostring(resumed),heatStartX or -1,releaseX or -1,table.concat(heatEvents,',')));q:close()
''')
    marker=" cached={air=p(0xc0b0),crash=p(0xc098),recovery=p(0xc09c),speed=p(0xc090)+256*p(0xc094),angle=p(0xc0ac),heat=p(0xc3e0)}"
    assert text.count(marker)==1
    text=text.replace(marker,marker+'''
 if cached.heat~=0 then heatSeen=true;if not heatStartX then heatStartX=wx()end end
 if heatSeen and cached.recovery==5 then recoverySeen=true end
 if heatSeen and recoverySeen and cached.heat==0 and cached.recovery==0 then
  cooled=true;if not releaseX then releaseX=wx()end
  if cached.speed>=608 and wx()>=heatStartX+16 then resumed=true end
 end
 local key=string.format('%d/%d/%d',cached.heat,cached.recovery,p(0xc03c))
 if key~=lastHeatState and #heatEvents<120 then
  lastHeatState=key
  heatEvents[#heatEvents+1]=string.format('{"frame":%d,"updates":%d,"x":%d,"heat":%d,"recovery":%d,"timer":%d,"divider":%d,"throttle_gate":%d,"lane":%d,"lane_speed":%d,"speed":%d}',frame,updates,wx(),cached.heat,cached.recovery,p(0xc03c),p(0xc020),p(0xc374),p(0xc0b8),p(0xc0dc),cached.speed)
 end
''')
    return text


def main():
    rom=O/'current4.nes';q=json.loads((O/'current4-composition.json').read_text());assert q['passed']and sha(rom)==q['ROM_SHA256']
    refs=[Path(__file__),O/'current4-composition.json',O/'heat-CPU.json',O/'heat-ISR-CPU.json']
    prepare(O/'native5',rom,(O/'native4/controller.lua').read_text(),refs+[O/'native4/controller.lua'],
            expected=q['ROM_SHA256'],timeout=150,allow_interactive=True,
            scope='Exact native4 successful cold/menu/motor/reverse/original61px jump/landing and hardware CHR/palette/HUD/alignedOAM assertions on source-continuation successor. No controller changes or writes;3PNGs, installedd8 Arthur tail retained.')
    text=observed((O/'full11/controller.lua').read_text())
    prepare(O/'full11-v2',rom,text,refs+[O/'full11/controller.lua'],
            expected=q['ROM_SHA256'],timeout=240,allow_interactive=True,
            scope='Exact earlier full11 controller on restored original timer/cooling/postair phases, with extra passive heat/divider/lane/throttle-gate evidence. Same no-life-loss active1-2 assertion,4PNGs/24frameCSV/no helpers or writes. Earlier native negative retained.')
    marker="  if r('NumberofLives')~=initialLives then finish(false,'Lost life');return end"
    assert text.count(marker)==1
    # A targeted physical overheat/recovery result, separate from full-stage
    # qualification. Keep all original inputs until this stop condition.
    text=text.replace(marker,marker+"\n  if resumed and cooled and recoverySeen then finish(true,'Original overheat recovered to0 and throttle motion resumed');return end")
    prepare(O/'heat-native',rom,text,refs+[O/'full11/controller.lua'],
            expected=q['ROM_SHA256'],timeout=180,allow_interactive=True,
            scope='Targeted controller-only genuine original overheat32→recovery5→heat0/recovery0→speed>=608 and forward motion>=16px, same lives. Same full11 inputs until first completed heat cycle; passive source timers/lane/throttle-gate.4PNGs/no writes/helpers, no full1-1 claim.')


if __name__=='__main__':main()
