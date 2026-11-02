"""Genuine turbo duty, adequate source windup and progressing cooldown route."""
from pathlib import Path
import json
from prepare_selected_native_packet_v1 import R,prepare,sha
from prepare_excitebike_dispatch_1101_v1 import O


def main():
    rom=O/'current4.nes';pin='cf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8'
    assert sha(rom)==pin
    assert json.loads((O/'heat-native2/capture/result.json').read_text())['passed']
    ref=O/'heat-native2/controller.lua';text=ref.read_text()
    def replace(old,new):
        nonlocal text
        assert text.count(old)==1,old
        text=text.replace(old,new)
    replace(" if heatSeen then return {right=true}end -- Genuine turbo release; no new jump/lean during cooling qualification.\n",'')
    replace("  if resumed and cooled and recoverySeen then finish(true,'Original overheat recovered to0 and throttle motion resumed');return end\n",'')
    replace('local b={right=true,b=true};','local b={right=true,b=cached.air==0 and cached.speed<700};')
    replace('if cached.crash~=0 or cached.recovery~=0 or cached.heat~=0 then jump=nil;return b end',
            'if cached.crash~=0 or cached.recovery~=0 or cached.heat~=0 then jump=nil;b.b=false;return b end')
    replace("  if jump.phase=='prelean' then", "  if jump.phase=='charge' then\n   b.b=true\n   if cached.speed>=608 then jump.phase='prelean';jump.epoch=epoch;b.up=true end\n  elseif jump.phase=='prelean' then")
    replace('local gap=not solid(x+52,y+32)','local gap=not solid(x+52,216)')
    replace("jump={phase='prelean',epoch=epoch,reason=gap and 'edge' or(obstacle and 'terrain' or'enemy')}",
            "jump={phase=cached.speed>=608 and 'prelean' or 'charge',epoch=epoch,reason=gap and 'edge' or(obstacle and 'terrain' or'enemy')}")
    replace('jumpSequences=jumpSequences+1;b.up=true','jumpSequences=jumpSequences+1;b.up=jump.phase==\'prelean\'')
    replace('local tallApproach,tallPassed=false,false','local tallApproach,tallPassed=false,false\nlocal thirdTop,fourthTop=false,false')
    replace('"helpers_added":false}', '"third_pipe_top_support":%s,"fourth_pipe_top_support":%s,"helpers_added":false}')
    replace("r('LevelNumber'),r('GameEngineSubroutine'))", "r('LevelNumber'),r('GameEngineSubroutine'),tostring(thirdTop),tostring(fourthTop))")
    marker='  maxX=math.max(maxX,x);maxCamera=math.max(maxCamera,camera());minY=math.min(minY,y)'
    replace(marker,marker+"\n  if y<=112 and r('Player_State')==0 and supported(x,y)then\n   if x+13>=736 and x+2<768 then thirdTop=true end\n   if x+13>=912 and x+2<944 then fourthTop=true end\n  end")
    prepare(O/'full11-v3',rom,text,[Path(__file__),ref,O/'current4-composition.json',O/'heat-native2/capture/result.json',O/'heat-native2/capture/heat.json'],
            expected=pin,timeout=240,allow_interactive=True,
            scope='Controller-only full1-1. OriginalB turbo only while grounded and speed<700; release during heat/recovery and air. Charge to genuine source608 before4prelean/A8/Up36, native floor-gap observation excludes mere platform drop. Meaningful originalcooldown/recovery progress extends stationary bound;9500globalframe bound, no-life-loss/active1-2 assertion retained. Explicit64px third/fourth top-support observations. FourPNGs/compacttrace/no writes/helpers/physics changes.')


if __name__=='__main__':main()
