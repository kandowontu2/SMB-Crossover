"""Read-only native counter/health trace of Prince's authored1-2 entry."""
import argparse
from hashlib import sha256
import json

import check_prince_draw_cache_native_1113 as Cases


def controller(raw):
    assert sha256(raw).hexdigest() in (Cases.Fix.PARENT,Cases.Fix.CANDIDATE)
    cookie=raw[Cases.Fix.Packet.COOKIE:Cases.Fix.Packet.COOKIE+16].hex()
    text=Cases.stage_controller(cookie)
    marker='local ending\n'
    # Mesen's write callback reports PC after operand fetch. The `pc` and
    # `instruction` fields below are that reported next-PC, not automatically
    # the writer's start. Qualify opcode bytes separately before naming a
    # writer (live A03E follows INC at A03B; A345 follows STA at A342).
    extra='''
local function entryWrite(name,at)
  emu.addMemoryCallback(guarded(function(_,value)
    if not ending or read(0x761)~=1 then return end
    local target=emu.convertAddress(at)
    if not target or target.memType~=emu.memType.nesWorkRam
      or target.address//8192~=2 then return end
    late.entryTrace=late.entryTrace or {}
    assert(#late.entryTrace<64,'Bounded entry counter/health trace')
    local cpu=emu.getState()
    local pc=cpu['cpu.pc']
    local mapped=emu.convertAddress(pc)
    late.entryTrace[#late.entryTrace+1]={name=name,value=value,
      before=source(at&8191),state=state(),counter=source(0x6c6),health=source(0x6cf),
      original_y=source(0x611)+256*source(0x612),original_mode=source(0x618),
      pc=pc,bank=mapped and mapped.address//8192 or -1,
      memory_type=mapped and tostring(mapped.memType)or '',
      a=cpu['cpu.a'],x=cpu['cpu.x'],y=cpu['cpu.y'],sp=cpu['cpu.sp'],
      instruction={read(pc),read(pc+1),read(pc+2)}}
  end),emu.callbackType.write,at)
end
entryWrite('fall-counter',0xc6c6)
entryWrite('source-health',0xc6cf)
'''
    assert text.count(marker)==1
    text=text.replace(marker,marker+extra)
    assert 'emu.write' not in text and 'emu.setState' not in text
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(text)
    return text


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',action='store_true')
    args=parser.parse_args()
    rom=Cases.OUT/'candidate.nes' if args.candidate else Cases.Fight.P.Base.C.ROM
    raw=rom.read_bytes();pin=sha256(raw).hexdigest()
    script=Cases.OUT/'controller.lua'
    script.write_text(controller(raw),encoding='utf-8',newline='\n')
    result,route=Cases.Stage.replay(script,rom,Cases.OUT/'capture',pin)
    q=result['receipt']
    print(json.dumps(dict(passed=result['passed'],reason=q['reason'],ROM_SHA256=pin,
        script_SHA256=result['script_SHA256'],receipt_SHA256=result['receipt_SHA256'],
        physical_frames=q['physical_frames'],commits=q['commits'],terminal=q['terminal'],
        underground_start=route.get('undergroundStart'),
        trace=q.get('later_route',{}).get('entryTrace'),native_Mesen=True,outputs=0),sort_keys=True),flush=True)
