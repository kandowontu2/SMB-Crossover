"""Preserve the native negative; passively diagnose accepted input and PPU."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_selected_native_packet_v1 import prepare,sha
from prepare_excitebike_dispatch_1101_v1 import labels
O=R/'build/excitebike-pose-1101-v3'


def main():
    old=O/'native';negative=json.loads((old/'capture/result.json').read_text())
    assert not negative['passed']and negative['frames']==1848
    assert sha(O/'current.nes')=='70621f954e65d0bc582fd6177a0a2f5eb50f3af3d51e39531a6fb81cd2800b85'
    text=(old/'controller.lua').read_text()
    assert text.count('pad.a=part==7 and steps<1')==1
    text=text.replace('pad.a=part==7 and steps<1','pad.a=part==7 and steps<8')
    lab=labels(O/'host.lbl')
    marker="local function wx()return r('Player_PageLoc')*256+r('Player_X_Position')end"
    addition=r'''
local rawA,rawC,upper=0,0,0
local chr={};local sourceCalls,launches,colorCalls=0,0,0
local inputs={};local hardware={};local dmas=0
emu.addMemoryCallback(function(_,v)rawA=v end,emu.callbackType.write,0x5115)
emu.addMemoryCallback(function(_,v)rawC=v end,emu.callbackType.write,0x5116)
emu.addMemoryCallback(function(_,v)upper=(v&3)*256 end,emu.callbackType.write,0x5130)
emu.addMemoryCallback(function(at,v)chr[at-0x5120]=v+upper end,emu.callbackType.write,0x5120,0x512b)
local function private(at)return emu.read(at,emu.memType.nesDebug)end
emu.addMemoryCallback(function()
 if rawA~=3 or rawC~=2 or r('SelectedCharacter')~=37 then return end
 sourceCalls=sourceCalls+1
 if phase=='play'and part>=6 and #inputs<100 then
  inputs[#inputs+1]=string.format('{"frame":%d,"phase":"%s","steps":%d,"epoch":%d,"pad":%d,"pad1":%d,"AB":%d,"previous_source_pad":%d,"last_source_epoch":%d,"have_epoch":%d,"source_clock":%d,"air":%d,"crash":%d,"recovery":%d,"heat":%d,"native_state":%d}',frame,phases[part][1],steps,r('FrameCounter'),r('SavedJoypadBits'),r('SavedJoypad1Bits'),r('A_B_Buttons'),private(0xc803),private(0xc801),private(0xc802),private(0xc03f),private(0xc0b0),private(0xc098),private(0xc09c),private(0xc3e0),r('Player_State'))
 end
end,emu.callbackType.exec,EX_MOVE)
emu.addMemoryCallback(function()if rawA==3 and rawC==2 and r('SelectedCharacter')==37 then launches=launches+1 end end,emu.callbackType.exec,EX_LAUNCH)
emu.addMemoryCallback(function()if rawA==3 and rawC==2 and r('SelectedCharacter')==37 then colorCalls=colorCalls+1 end end,emu.callbackType.exec,EX_COLORS)
emu.addMemoryCallback(function(_,page)
 if phase~='play'or r('SelectedCharacter')~=37 then return end
 dmas=dmas+1
 if dmas~=1 and dmas%120~=0 then return end
 local pal={};local records={}
 for i=0,31 do pal[#pal+1]=string.format('%02x',emu.read(0x3f00+i,emu.memType.nesPpuDebug))end
 for at=0,252,4 do
  local y=private(page*256+at)
  if y<240 then records[#records+1]=string.format('[%d,%d,%d,%d]',y,private(page*256+at+1),private(page*256+at+2),private(page*256+at+3))end
 end
 hardware[#hardware+1]=string.format('{"frame":%d,"phase":"%s","CHR4_7":[%d,%d,%d,%d],"palette":"%s","visible_OAM":[%s]}',frame,phases[part][1],chr[4]or-1,chr[5]or-1,chr[6]or-1,chr[7]or-1,table.concat(pal,''),table.concat(records,','))
end,emu.callbackType.write,0x4014)
'''
    addition=addition.replace('EX_MOVE',str(lab['ExHostMovement'])).replace('EX_LAUNCH',str(lab['ExAirLaunch'])).replace('EX_COLORS',str(lab['ExHostColors']))
    assert text.count(marker)==1;text=text.replace(marker,marker+'\n'+addition)
    marker=" f:close();emu.stop(passed and 0 or 1)"
    extra=r'''
 local z=assert(io.open(OUTPUT..'diagnosis.json','w'))
 z:write(string.format('{"source_movement_calls":%d,"source_launch_calls":%d,"source_color_calls":%d,"normal_DMAs":%d,"input_trace":[%s],"hardware":[%s]}\n',sourceCalls,launches,colorCalls,dmas,table.concat(inputs,','),table.concat(hardware,',')));z:close()
'''
    assert text.count(marker)==1;text=text.replace(marker,' f:close()\n'+extra+' emu.stop(passed and 0 or 1)')
    prepare(O/'native2',O/'current.nes',text,[Path(__file__),old/'controller.lua',old/'capture/result.json',O/'cold-CPU.json',O/'host.lbl'],
            expected=sha(O/'current.nes'),timeout=150,allow_interactive=True,
            scope='Same exact negative ROM. A held8Mainepochs to diagnose native sampling, passive actual source entry/launch/input/CHR-latch/palette/OAM observers. Original jump assertion retained;3PNG, compact aggregate; no writes or install.')

if __name__=='__main__':main()
