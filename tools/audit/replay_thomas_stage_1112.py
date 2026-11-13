"""Run the retained Thomas stage controller with a bounded stdout receipt."""

import argparse
from hashlib import sha256
import json
from pathlib import Path

from run_stdout_mesen_1110 import R, run


SOURCE = R/'build/helper-camera-thomas-gap-v5-1110/controller.lua'
SOURCE_PIN = 'e4f0e2a9476dea8b3fd129d043f45d6d76a3085e511325399dfdef88863730b2'
OUTPUT = R/'build/metal-flower-native-1112'
PIN = '15a683321cde608cfe15447e90ef58d5295a16a1a6b607434f98df37162ac533'


def replace_once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new, 1)


def replace_span(text, first, after, replacement):
    start = text.index(first)
    end = text.index(after, start)
    return text[:start] + replacement + text[end:]


def controller():
    assert sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_PIN
    text = SOURCE.read_text()
    text = text.replace('5444f3e3bcb07c8314ba6f17b067f2e678eb4ec668786456e4f26d56ba8d75a2', PIN)
    text = replace_once(text, "local plan={'right','right','down','select','select'}",
                        "local plan={'down','right','right','select','select'}")
    text = replace_once(text, "  elseif visible('selected')then assert(r('CrossoverMenuIndex')==10 and selected(),'Actual Thomas Select alternate');shot('selected');phase='launch';age=0 end",
                        "  else assert(r('CrossoverMenuIndex')==10 and selected(),'Actual Thomas Select alternate');phase='launch';age=0 end")
    text = replace_once(text, "   assert(ui.lives_shot,'Visible lives sprite');phase='game';age=0;initialLives=r('NumberofLives')",
                        "   assert(selected(),'Thomas retained at stage entry');phase='game';age=0;initialLives=r('NumberofLives')")
    text = replace_once(text, "  if not ui.lives_shot and livesFirst and frame-livesFirst>=24 and visible('lives')then shot('lives');ui.lives_shot=true end\n", '')
    text = replace_once(text, " if target==1 and routeState=='ride'and slot~=nil and contact==slot and not ui.platform_shot and visible('game')then shot('platform');ui.platform_shot=true end\n", '')
    text = replace_span(text, 'local function sample(', 'for _,entry in ipairs(', '')
    text = replace_once(text, ' local rows={}', ' local rows,flower={},{}')
    text = replace_span(text, "emu.addMemoryCallback(function()if active()and raw(L.GameLoop)",
                        'emu.addEventCallback(function()', '''emu.addMemoryCallback(function()
 if not active()or raw(L.GameLoop)~=254 then return end
 assert(not lastMain,'No recursive Main')
 local cpu=emu.getState();local sp=cpu['cpu.sp']
 local pc=(peek(0x100+((sp+1)&255))+256*peek(0x100+((sp+2)&255))+1)&65535
 assert(pc==0x82be or pc==0x82d0,'Actual Main caller')
 lastMain={sp=(sp+2)&255,pc=pc}
end,emu.callbackType.exec,L.GameLoop)
for _,pc in ipairs({0x82be,0x82d0})do
 emu.addMemoryCallback(function()
  if lastMain and lastMain.pc==pc and raw(pc)==254 and emu.getState()['cpu.sp']==lastMain.sp then
   updates=updates+1;lastMain=nil;route()
  end
 end,emu.callbackType.exec,pc)
end
''')
    text = replace_once(text, '  local i=#rows+1', '''  if left==1200 then
   assert(not flower.left and y==192 and relative>=256 and relative<=287,'Flower lift birth')
   flower={left=left,center=left+16,y=y,camera=camera,slot=slot}
   return
  end
  local i=#rows+1''')
    text = replace_span(text, "  local out=assert(io.open(OUTPUT..'helper-camera.json'", ' end\nend',
                        '  if ok then assert(flower.left,"Flower lift constructor")end\n'
                        '  return ok,reason,rows,flower\n')
    text = replace_span(text, 'local csv=', 'local function r(', '')
    text = replace_span(text, 'local function shot(n)', 'local function finish(ok,reason)',
                        'local function shot(_) end\n')
    text = replace_once(text, ' ok,reason=helperCameraFinish(ok,reason)',
                        ' local placements,flower\n ok,reason,placements,flower=helperCameraFinish(ok,reason)')
    text = replace_span(text, " done=true;shot('endpoint');csv:close()", '\nend\nemu.addMemoryCallback', ''' done=true
 print('SMB_NATIVE_RECEIPT '..json({passed=ok,reason=reason,ROM_SHA256=P.sha256,frames=frame,Main=updates,
  counters=counters,minimum_ISR_SP=minSP,pipe_clears=clears,maximum_X=maxX,maximum_camera=maxCamera,
  first_floor_gap={readback=gapProbe.readback,landing=gapProbe.landing},
  placements=placements,flower_lift=flower,lives=r('NumberofLives'),initial_lives=initialLives,
  level=r('LevelNumber'),world=r('WorldNumber'),controller_only=true,output_files=0}))
 emu.stop(ok and 0 or 1)''')
    text = replace_span(text, ' local s=emu.getState();local bytes={}', ' assert(false,reason)', '')
    text = replace_span(text, 'local softwareFrames,softwarePosts,softwareEvents=',
                        'local stepProbes,lastStepProbe=', '')
    text = replace_once(text, " if ok then assert(counters.software_rti>0 and counters.software_target>0,'Positive actual qualified software RTI path');assert(counters.nmi>0 and counters.irq>0 and counters.vectors>0,'Positive genuine hardware NMI/IRQ parity')end\n", '')
    text = replace_once(text, 'pad.up=not gapProbe.trigger and x>=1371 and leftSupport and not support',
                        'pad.up=not gapProbe.trigger and x>=1372 and grounded and not support')
    text = replace_once(text, " elseif phase=='game'then b=pad end", ''' elseif phase=='game'then
  b=pad
  local x=r('Player_X_Position')+256*r('Player_PageLoc')
  if x>=1368 and x<1378 and r('Player_Y_Position')==176 then
   b={right=true,up=x>=1372 and r('Player_State')==0}
  end
 end''')
    text = replace_once(text, "    local f=assert(io.open(OUTPUT..'terrain-probes.json','w'));f:write(json(stepProbes));f:close()\n", '')
    text = replace_span(text, "    local f=assert(io.open(OUTPUT..'elevated-support.json'", '\n   end', '')
    text = '\n'.join(line for line in text.splitlines() if 'csv:write(' not in line) + '\n'
    assert 'io.open' not in text and 'takeScreenshot' not in text
    # Errors in retained observers must produce a bounded failure receipt.
    guard = '''local memoryCallback,eventCallback=emu.addMemoryCallback,emu.addEventCallback
local observerFailed=false
local function checked(fn)
 return function(...)
  if observerFailed then return end
  local ok,why=pcall(fn,...)
  if not ok then
   observerFailed=true
   print('THOMAS_OBSERVER_ERROR '..tostring(why))
   local detail=tostring(why):gsub('[^%w :./_-]','?')
   print('SMB_NATIVE_RECEIPT {"passed":false,"reason":"'..detail..'","output_files":0,"ROM_SHA256":"'..os.getenv('SMB_STDOUT_ROM_SHA')..'"}')
   emu.stop(1)
  end
 end
end
emu.addMemoryCallback=function(fn,...)return memoryCallback(checked(fn),...)end
emu.addEventCallback=function(fn,...)return eventCallback(checked(fn),...)end
'''
    return guard+text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom', type=Path, default=OUTPUT/'candidate.nes')
    args = parser.parse_args()
    script = OUTPUT/'controller.lua'
    script.write_text(controller(), encoding='utf-8', newline='\n')
    result = run(script, args.rom, OUTPUT/'capture', PIN, 240)
    print(json.dumps({key: result[key] for key in
                     ('passed', 'receipt_SHA256', 'script_SHA256', 'receipt', 'stderr')}), flush=True)
    assert result['passed']


if __name__ == '__main__':
    main()
