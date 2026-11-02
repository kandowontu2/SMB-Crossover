"""Observe actual native Hogan input/import/source/export after zero movement."""
from pathlib import Path
import json
from prepare_selected_native_packet_v1 import R, prepare, sha

O = R / 'build/hogan-walk-diagnostic-1102-v1'
P = R / 'build/empty-screen-lag-1102-v1/hulk-hogan'
ROM = R / 'build/excitebike-pose-1101-v3/current4.nes'


def main():
    O.mkdir(exist_ok=True)
    q = json.loads((P / 'capture/result.json').read_text(encoding='utf-8'))
    assert q['passed'] and q['measurements'][1]['first_x'] == q['measurements'][1]['last_x'] == 40
    text = (P / 'controller.lua').read_text(encoding='utf-8')
    marker = "local function finish(reason)"
    observer = r'''
local trace={};local observed={}
local function note(name)
 if phase~='walk' or (observed[name]or 0)>=24 then return end
 observed[name]=(observed[name]or 0)+1
 local s=emu.getState();local bytes={}
 for i=0x20,0x43 do bytes[#bytes+1]=r('WfState',i)end
 trace[#trace+1]=string.format('{"at":%q,"frame":%d,"epoch":%d,"cpu_a":%d,"cpu_x":%d,"cpu_y":%d,"held":%d,"pad1":%d,"previous_source_input":%d,"native_x":%d,"native_y":%d,"native_speed":%d,"native_scroll":%d,"source20_43":[%s]}',name,frame,r('FrameCounter'),s['cpu.a'],s['cpu.x'],s['cpu.y'],r('SavedJoypadBits'),r('SavedJoypad1Bits'),r('WfPreviousInput'),wx(),r('Player_Y_Position'),r('Player_X_Speed'),r('Player_X_Scroll'),table.concat(bytes,','))
end
for _,name in ipairs({'WfRawHostImport','WfRawHostExport'})do
 emu.addMemoryCallback(function()if r('CurrentBank')==(B[name]|128) and r('CurrentBankC')==2 then note(name)end end,emu.callbackType.exec,assert(L[name]))
end
emu.addMemoryCallback(function()if r('CurrentBankC')==2 then note('WfHostFrame')end end,emu.callbackType.exec,assert(L.WfHostFrame))
'''
    assert text.count(marker) == 1
    text = text.replace(marker, observer + '\n' + marker)
    marker = " out:close();emu.stop(passed and 0 or 1)"
    assert text.count(marker) == 1
    text = text.replace(marker, " out:close();local z=assert(io.open(OUTPUT..'input-source-export.json','w'));z:write('['..table.concat(trace,',')..']');z:close();emu.stop(passed and 0 or 1)")
    text = text.replace("phase=='walk' and age>=40", "phase=='walk' and (age>=180 or wx()>=110)")
    prepare(O / 'native', ROM, text, [Path(__file__), P / 'controller.lua', P / 'capture/result.json'],
            expected=sha(ROM), timeout=90, allow_interactive=True,
            scope='Same installed cf, extended180-physical-frame no-attack right hold after empty idle. '
                  'Passive first24 actual source/import/export calls per entry with bank checks; '
                  'one PNG and compact aggregate, no emulated writes or source changes.')


if __name__ == '__main__':
    main()
