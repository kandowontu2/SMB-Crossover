"""Freeze the repaired ROM and a bounded controller-only hardware diagnosis."""
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_selected_native_packet_v1 import prepare,sha
from prepare_excitebike_dispatch_1101_v1 import labels
O=R/'build/excitebike-pose-1101-v3'


def main():
    for name in ['native','native2']:
        q=json.loads((O/name/'capture/result.json').read_text())
        assert not q['passed'] and q['selected']==37
    composition=json.loads((O/'current2-composition.json').read_text())
    digest='23086fbfa3daa0f4b5b850166c51362eb6a7e8908230bd01cb1a679eadb15616'
    assert composition['passed'] and composition['ROM_SHA256']==sha(O/'current2.nes')==digest
    for name in ['current2-CPU.json','cold2-CPU.json']:
        q=json.loads((O/name).read_text())
        assert q['passed'] and q['memory_candidate_SHA256']==digest
    text=(O/'native2/controller.lua').read_text()
    def replace(old,new):
        nonlocal text
        assert text.count(old)==1,old
        text=text.replace(old,new)
    # Run to the original motor cap, then establish lean before the fresh A.
    # This is a controller change; the original air arithmetic is unchanged.
    replace("{'prepare',90,1},{'jump',36,9}","{'prepare',180,1},{'prelean',4,9},{'jump',36,9}")
    replace('#results==8','#results==9')
    replace('results[7].minY<results[7].firstY-30','results[8].minY<results[8].firstY-30')
    replace('pad.a=part==7 and steps<8','pad.a=part==8 and steps<8')
    replace("if part==7 then shot('source-lean-jump')end","if part==8 then shot('source-lean-jump')end")
    replace("if phase=='play'and part>=6 and #inputs<100 then","if phase=='play'and (part==6 and steps>=150 or part>=7) and #inputs<180 then")
    replace('"air":%d,"crash":%d','"angle":%d,"speed":%d,"x":%d,"y":%d,"air":%d,"crash":%d')
    replace("private(0xc03f),private(0xc0b0)","private(0xc03f),private(0xc0ac),private(0xc090)+256*private(0xc094),wx(),r('Player_Y_Position'),private(0xc0b0)")
    replace('local inputs={};local hardware={};local dmas=0','local inputs={};local hardware={};local dmas=0\nlocal hardwareChecks,hardwareFailures,firstHardwareFailure=0,0,nil')
    replace("local passed=reason=='completed'", "local passed=hardwareChecks>0 and hardwareFailures==0 and sourceCalls>0 and launches>0 and colorCalls>0 and reason=='completed'")
    replace('"normal_DMAs":%d,"input_trace"','"normal_DMAs":%d,"hardware_checks":%d,"hardware_failures":%d,"first_hardware_failure":%s,"input_trace"')
    replace("colorCalls,dmas,table.concat(inputs,',')", "colorCalls,dmas,hardwareChecks,hardwareFailures,firstHardwareFailure or 'null',table.concat(inputs,',')")
    marker="  local cfg=phases[part];local q=results[part]"
    check=r'''
  if dmas>1 and r('SelectedCharacter')==37 and r('GameEngineSubroutine')==8 then
   hardwareChecks=hardwareChecks+1
   local obj=L['ObjectMetasprite'];local ptr=L['SmPosePtr']
   local aligned=r('CurrentOAMOffset')%4==0 and private(obj)==0 and private(ptr)+256*private(ptr+1)==obj
   local banks=chr[4]==736 and chr[5]==737 and chr[6]==738 and chr[7]==739
   local palette=emu.read(0x3f11,emu.memType.nesPpuDebug)==32 and emu.read(0x3f12,emu.memType.nesPpuDebug)==22 and emu.read(0x3f13,emu.memType.nesPpuDebug)==15
   local title={14,33,11,18,20,14,36};local hud=true
   for i,v in ipairs(title)do if emu.read(0x2042+i,emu.memType.nesPpuDebug)~=v then hud=false end end
   if not(aligned and banks and palette and hud)then
    hardwareFailures=hardwareFailures+1
    if not firstHardwareFailure then firstHardwareFailure=string.format('{"frame":%d,"phase":"%s","aligned":%s,"banks":%s,"palette":%s,"HUD":%s}',frame,phases[part][1],tostring(aligned),tostring(banks),tostring(palette),tostring(hud))end
   end
  end
'''
    replace(marker,check+marker)
    lab=labels(O/'host.lbl')
    # The first packet had a stale hard-linked label file. Bind entry hooks
    # from the actual frozen controller, then publish current source labels.
    import re
    for name in ['ExHostMovement','ExAirLaunch','ExHostColors']:
        pattern=r'(end,emu.callbackType.exec,)\d+(\))'
        entries=list(re.finditer(pattern,text))
        index=['ExHostMovement','ExAirLaunch','ExHostColors'].index(name)
        m=entries[index]
        text=text[:m.start()]+m[1]+str(lab[name])+m[2]+text[m.end():]
    refs=[Path(__file__),O/'native2/controller.lua',O/'native/capture/result.json',O/'native2/capture/result.json',
          O/'current2-composition.json',O/'current2-CPU.json',O/'cold2-CPU.json',O/'terrain-CPU.json',O/'host.lbl']
    prepare(O/'native3',O/'current2.nes',text,refs,expected=digest,timeout=150,allow_interactive=True,
            scope='Controller-only repaired raw37 cold menu, idle/throttle/coast/reverse, original motor cap then4 prelean updates and8-epoch A; actual source angle/speed/input trace and completed-frame CHR736..739/palette/HUD/stable aligned OAM checks. Three PNGs; no writes, full1-1, helper or installation claim.')


if __name__=='__main__':main()
