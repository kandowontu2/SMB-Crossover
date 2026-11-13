"""Four bounded native spot images and color-queue observations of the entrance."""
import argparse
from hashlib import sha256
import json

import check_prince_entrance_current_native_1113 as Native
from run_stdout_mesen_1110 import run


def controller(candidate):
    assert sha256(candidate).hexdigest() == Native.Fix.PIN
    cookie = candidate[Native.Fix.Entry.Cache.Packet.COOKIE:
        Native.Fix.Entry.Cache.Packet.COOKIE+16].hex()
    text = Native.Prior.stage_controller(cookie)
    assert sha256(text.encode()).hexdigest() == Native.Prior.PINS['stage']
    needle = 'controller_only=true,output_files=0,'
    assert text.count(needle) == 1
    text = 'local entryShots,entryColorEvents={},{}\n'+text.replace(needle,
        needle+'entry_shots=entryShots,entry_color_events=entryColorEvents,')
    text += r'''
local shotFlags={}
local alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
local function png64(bytes)
 local out={};for i=1,#bytes,3 do local a,b,c=bytes:byte(i),bytes:byte(i+1),bytes:byte(i+2);local n=(a<<16)|((b or 0)<<8)|(c or 0)
 out[#out+1]=alphabet:sub((n>>18)+1,(n>>18)+1);local j=(n>>12)&63;out[#out+1]=alphabet:sub(j+1,j+1);j=(n>>6)&63;out[#out+1]=b and alphabet:sub(j+1,j+1)or'=';j=n&63;out[#out+1]=c and alphabet:sub(j+1,j+1)or'='end;return table.concat(out)
end
emu.addEventCallback(guarded(function()
 if stopped then return end
 local s=state();if s.world~=0 or s.level~=1 or s.area~=0 or s.y_high~=1 then return end
 local tag
 if s.engine==7 and s.y>=96 and not shotFlags.middle then tag='middle'
 elseif s.engine==7 and s.y>=160 and not shotFlags.lower then tag='lower'
 elseif s.engine==8 and s.y==176 and s.phase>=4 and not shotFlags.landed then tag='landed'
 elseif s.engine==8 and s.y==176 and s.phase>=30 and not shotFlags.later then tag='later'end
 if not tag then return end
 assert(#entryShots<4,'Four spot images maximum');shotFlags[tag]=true
 local png=emu.takeScreenshot();assert(type(png)=='string'and png:byte(1)==137 and png:sub(2,4)=='PNG'and png:byte(5)==13 and png:byte(6)==10 and png:byte(7)==26 and png:byte(8)==10,'Actual PNG');assert(#png<=4*1024*1024,'PNG4MB bound')
 local sprites={};for i=0,63 do local at=0x200+i*4;local y=read(at);if y<240 then sprites[#sprites+1]={slot=i,y=y,tile=read(at+1),attributes=read(at+2),x=read(at+3)}end end
 local palette,pattern={},{};for at=0x3f00,0x3f1f do palette[#palette+1]=emu.read(at,emu.memType.nesPpuDebug)end;for at=0,159 do pattern[#pattern+1]=emu.read(at,emu.memType.nesPpuDebug)end
 entryShots[#entryShots+1]={tag=tag,state=s,bytes=#png,sprites=sprites,palette=palette,pattern_debug=pattern}
 print('SMB_NATIVE_IMAGE '..png64(png))
end),emu.eventType.endFrame)
for _,address in ipairs({0xdf9e,0xdfa1,0xdfa6,0xdfb6})do
 local pc=address
 emu.addMemoryCallback(guarded(function()
  if stopped or read(0x6002)~=38 or read(0x761)~=1 then return end
  local m=emu.convertAddress(pc);if not m or m.memType~=emu.memType.nesWorkRam or m.address~=2*8192+(pc&8191)then return end
  assert(#entryColorEvents<32,'Bounded color queue observations')
  local cpu=emu.getState()
  entryColorEvents[#entryColorEvents+1]={pc=pc,state=state(),offset=read(0x4ae),control=read(0x774),a=cpu['cpu.a'],x=cpu['cpu.x'],p=cpu['cpu.p']}
 end),emu.callbackType.exec,pc)
end
'''
    assert 'emu.write' not in text and 'io.open' not in text
    return text


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--metadata', action='store_true')
    args = p.parse_args()
    rom = Native.OUT/'candidate.nes'
    raw = rom.read_bytes(); text = controller(raw)
    if args.metadata:
        print(json.dumps(dict(ROM_SHA256=Native.Fix.PIN,
            script_SHA256=sha256(text.encode()).hexdigest(), native_run=False, output_files=0)))
    else:
        script = Native.OUT/'controller.lua'
        script.write_text(text, encoding='utf-8', newline='\n')
        result, _ = Native.Prior.Stage.replay(script, rom, Native.OUT/'capture', Native.Fix.PIN)
        for img in result.pop('images'):
            print(json.dumps(dict(native_image=img)), flush=True)
        q = result['receipt']
        print(json.dumps(dict(passed=result['passed'], ROM_SHA256=Native.Fix.PIN,
            script_SHA256=result['script_SHA256'], receipt_SHA256=result['receipt_SHA256'],
            entry_shots=q.get('entry_shots'), entry_color_events=q.get('entry_color_events'), terminal=q.get('terminal'),
            outputs_written=result['outputs_written']), separators=(',', ':')), flush=True)
        assert result['passed'] and len(q['entry_shots']) == 4
