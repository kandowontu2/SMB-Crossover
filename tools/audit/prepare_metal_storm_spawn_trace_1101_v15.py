"""Bounded read-only spawn/cold-loader/actor trace on the failing native replay."""
from pathlib import Path
import json,re
import prepare_metal_storm_menu_1101_v15 as P
from prepare_selected_native_packet_v1 import prepare,sha
def main():
    labels={m[2]:int(m[1],16) for line in (P.R/'build/metal-storm-native-integration-1101-v12/native-component.lbl').read_text().splitlines() if (m:=re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\S+)',line))}
    c=(P.O/'native-smoke/controller.lua').read_text()
    instrument="""
local events,counts={},{}
local function event(id)
 counts[id]=(counts[id] or 0)+1
 if #events>=90 then return end
 local s=emu.getState()
 table.insert(events,string.format('[%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d]',id,frame,s['cpu.pc'],r('CurrentBank'),r('CurrentBankC'),r('Player_X_Position'),r('Player_PageLoc'),r('Player_Y_Position'),r('Player_Y_HighPos'),r('GameEngineSubroutine'),r('OperMode_Task'),s['cpu.a'],s['cpu.sp']))
end
"""
    hooks=[('Ms8Load',116),('Ms12Movement',2),('MsNativeConstruct',3),('MsNativeApplyDelta',3),('MsRenderDraw',2)]
    for i,(name,bank) in enumerate(hooks,1):
        pc=labels[name];mapname='CurrentBankC' if pc>=0xc000 else 'CurrentBank';tag=bank if bank<4 else bank|128
        instrument+=f"emu.addMemoryCallback(function() if r('{mapname}')=={tag} then event({i}) end end,emu.callbackType.exec,{pc})\n"
    instrument+="""emu.addMemoryCallback(function(_,value)
 if (phase=='start' or phase=='walk') and r('SelectedCharacter')==35 then event(6) end
end,emu.callbackType.write,L['Player_X_Position'])
"""
    at=c.index('local function shot');c=c[:at]+instrument+c[at:]
    c=c.replace('done=true;emu.stop',"""local t=assert(io.open(OUTPUT..'spawn-trace.json','w'))
 local cs={};for id,n in pairs(counts)do table.insert(cs,string.format('"%d":%d',id,n))end
 t:write('{"counts":{'..table.concat(cs,',')..'},"events":['..table.concat(events,',')..']}');t:close()
 done=true;emu.stop""")
    prepare(P.O/'native-diagnostic',P.O/'candidate.nes',c,[Path(__file__)],expected=sha(P.O/'candidate.nes'),timeout=90,
            scope='Same failing controller replay with at most90 read-only code/write observations. No emulated writes.')
if __name__=='__main__':main()
