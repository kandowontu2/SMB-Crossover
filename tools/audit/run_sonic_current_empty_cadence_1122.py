"""Installed59e empty-scene clock; reuse the existing stdout observer/queue.

Default compiles both controllers without writes. Root-only --run changes
only the existing shared controller.lua, restores it finally, and launches
the installed Downloads ROM. No candidate, capture or receipt files.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
from unittest.mock import patch

import compose_sonic_original_motion_1122 as Motion
from run_sonic_original_motion_smoke_1122 import value

R, ROM = Motion.R, Motion.ROM
PIN = '59e1a591d5ea31d62dafa9332990598b74b5b0852194ef7cc7ad22788196b723'
BASE = R / 'tools/playthroughs/ff_empty_cadence_stdout_1110.lua'
SHARED = R / 'build/smb2-flag-native-1113'
FORMS = {'sonic': 3, 'super': 4}


def H(raw):
    return sha256(raw).hexdigest()


def controller(raw, form):
    assert H(raw) == PIN and form in FORMS
    text = BASE.read_text(encoding='utf-8')

    def once(old, new):
        nonlocal text
        assert text.count(old) == 1, old
        text = text.replace(old, new, 1)

    once("local pin=assert(os.getenv('SMB_STDOUT_ROM_SHA'))", "local pin=assert(os.getenv('SMB_STDOUT_ROM_SHA'));assert(pin==C.sha,'Exact installed59e')")
    once('local completions,phases={},{}', 'local completions,phases={},{}\nlocal portReads,pollFrames,motor,motorBase,motorLive= {},{},0,0,nil\nlocal motorHooked={}\nlocal costs={idle={calls=0,cycles=0,maximum=0},right={calls=0,cycles=0,maximum=0}}')
    once("local function state()", "local function work(bank,a)return emu.read(bank*8192+(a&8191),emu.memType.nesWorkRam)end\nlocal function state()")
    once('raw=r(0x6002),variant=r(0x5fef)', 'raw=r(0x6002),variant=r(0x5ffe)')
    once('local duration,zero,maximum,total=0,0,0,0', 'local duration,zero,maximum,total=0,0,0,0\n local missed,reads,physicalPolls,hist,readHist=0,0,0,{},{}')
    once('local n=completions[f]or 0;total=total+n;maximum=math.max(maximum,n)', "local n=completions[f]or 0;total=total+n;maximum=math.max(maximum,n)\n   local p=portReads[f]or 0;reads=reads+p;physicalPolls=physicalPolls+(pollFrames[f]or 0)\n   if p==0 then missed=missed+1 end\n   hist[tostring(n)]=(hist[tostring(n)]or 0)+1;readHist[tostring(p)]=(readHist[tostring(p)]or 0)+1")
    once('phases=phases,terminal=state(),', 'phases=phases,terminal=state(),form=C.form,actual_motor_returns=motor-motorBase,\n  literal_controller_reads=reads,no_controller_read_frames=missed,physical_input_polls=physicalPolls,\n  Main_return_histogram=hist,literal_read_histogram=readHist,inclusive_Main_costs=costs,\n  baseline_marker={bank=126,entry=0x82d9,returns={0x82be,0x82d0},actual_PC_SP_mapping_acknowledged=true},')
    once("scope='80 actual Main completions in inclusive physical frame interval, four warm settled updates, six empty enemy slots before/after every Main.32idle then48Right. Native NmiSkipped modulo256. Not forced60fps or exhaustive route/art/audio proof.'", "scope='64 actual Main completions in an inclusive physical-frame interval, four settled updates, naturally zero enemies, idle48 then Right16. Actual accepted motor returns, literal4016/4017 reads and inclusive Main cycles (interrupts/DMA included). Boundary frames can be partial. No cadence acceptance assumed.'")
    once("assert(r(0x6002)==22 and r(0x5fef)==0 and r(0x75f)==2 and r(0x5fc5)==0,'Identity/life/power')", "assert(r(0x6002)==43 and r(0x5ffe)==C.select and r(0x75f)==2 and r(0x5fc5)==0,'Identity/life/power')\n assert(work(2,0xc119)==1 and work(2,0xc041)==24 and work(2,0xc042)==32 and work(2,0xc030)&128~=0 and r(0xbd)==176,'Actual grounded Sonic opening')\n for bank=2,3 do for i,v in ipairs(C.cookie)do assert(work(bank,0xdfe0+i-1)==v,'Complete source header')end end")
    once('local observe=menuDone and active()', 'local observe=menuDone and active()and work(2,0xc119)==1 and ticks<64')
    once('live={ret=ret,sp=(sp+2)&255,observe=observe}', "if observe and settled>=4 and not started then\n  started=true;beginFrame=frame;beginSkipped=r(0x13a);motorBase=motor;phases[1]={name='idle48',before=state()}\n end\n live={ret=ret,sp=(sp+2)&255,observe=observe,cycle=s['cpu.cycleCount'],motor=motor}")
    once('local observe=live.observe;live=nil', "local observed=live;local observe=live.observe;live=nil")
    once("assert(active(),'Profile left ordinary gameplay');empty()", "assert(active(),'Profile left ordinary gameplay');empty()\n  assert(not motorLive and motor-observed.motor==1,'One accepted returned motor per complete Main')")
    once("if not started then started=true;beginFrame=frame;beginSkipped=r(0x13a);phases[1]={name='idle32',before=state()}end", "assert(started,'Clock starts at actual measured Main entry')\n  local cost=costs[ticks<48 and'idle'or'right'];local elapsed=cpu['cpu.cycleCount']-observed.cycle\n  assert(elapsed>=0,'Monotonic native CPU clock');cost.calls=cost.calls+1;cost.cycles=cost.cycles+elapsed;cost.maximum=math.max(cost.maximum,elapsed)")
    once("if ticks==32 then phases[1].after=state();phases[2]={name='Right48',before=state()};pad=1 end", "if ticks==48 then phases[1].after=state();phases[2]={name='Right16',before=state()};pad=1 end")
    once('if ticks==80 then phases[2].after=state();pad=0 end', 'if ticks==64 then phases[2].after=state();pad=0 end')
    once("for _,b in ipairs({4,4,1,1,1,1,1})do press(b)end\n assert(r(0x7309)==21 and r(0x6002)==22 and r(0x5fef)==0,'Fighter slot')", "for _,b in ipairs({4,4,4,1})do press(b)end\n assert(r(0x7309)==25,'MrGimmick slot');for _=1,C.select do press(32)end\n assert(r(0x6002)==43 and r(0x5ffe)==C.select,'Actual Sonic form')")
    once('polls=polls+1', 'polls=polls+1;pollFrames[frame]=(pollFrames[frame]or 0)+1')
    once("emu.setInput({right=pad&1~=0,down=pad&4~=0,start=pad&16~=0},0)", "emu.setInput({right=pad&1~=0,down=pad&4~=0,start=pad&16~=0,select=pad&32~=0},0)")
    once("if ticks>=80 then assert(ticks==80 and x()>40 and x()<160,'Exact empty profile endpoint');finish(true,'Natural empty80-Main profile');return end", "if ticks>=64 then assert(ticks==64 and x()>40 and x()<160 and motor-motorBase==64,'Exact empty profile endpoint');finish(true,'Natural Sonic empty64-Main profile');return end")
    extra = r'''
for _,port in ipairs({0x4016,0x4017})do emu.addMemoryCallback(guarded(function()
 portReads[frame]=(portReads[frame]or 0)+1
end),emu.callbackType.read,port)end
local function workMapped(pc,offset)
 local q=emu.convertAddress(pc);return q and q.memType==emu.memType.nesWorkRam and q.address==offset
end
emu.addMemoryCallback(guarded(function()
 if not live or not live.observe or not workMapped(0xbbb0,3*8192+0x1bb0)then return end
 assert(not motorLive,'Synchronous original motor')
 for i,v in ipairs(C.motor)do assert(r(0xbbb0+i-1)==v,'Actual installed motor entry')end
 local s=emu.getState();local sp=s['cpu.sp']
 local ret=(r(0x100+((sp+1)&255))+256*r(0x100+((sp+2)&255))+1)&65535
 local q=emu.convertAddress(ret);assert(q,'Actual motor return mapping')
 motorLive={ret=ret,sp=(sp+2)&255,kind=q.memType,address=q.address}
 if not motorHooked[ret]then
  motorHooked[ret]=true;emu.addMemoryCallback(guarded(function()
   local p=motorLive;if not p or p.ret~=ret then return end
   local c=emu.getState();if c['cpu.sp']~=p.sp then return end
   local a=emu.convertAddress(ret);assert(a and a.memType==p.kind and a.address==p.address,'Actual motor mapped return')
   assert(c['cpu.ps']&1~=0 and work(2,0xc116)==0,'Accepted actual motor return')
   motor=motor+1;motorLive=nil
  end),emu.callbackType.exec,ret)
 end
end),emu.callbackType.exec,0xbbb0)
'''
    once('local function frames(n)', extra+'\nlocal function frames(n)')
    q = dict(sha=PIN, form=form, select=FORMS[form], cookie=list(raw[Motion.COOKIE_AT:Motion.COOKIE_AT+16]),
             motor=list(Motion.kernel(raw)[0x1bb0:0x1bb0+16]))
    result = 'local C='+value(q)+'\n'+text
    executable = '\n'.join(line.split('--', 1)[0] for line in result.splitlines())
    assert not re.search(r'\bio\s*[.:]|\bemu\s*[.:]\s*(?:write|save|load)|os\s*\.\s*(?:execute|remove|rename)', executable)
    from check_ff_stdout_controller_source_1110 import LuaRuntime
    LuaRuntime().compile(result)
    return result


def validate(raw):
    return dict(passed=True, source_only=True, ROM_SHA256=PIN,
                controllers={form:H(controller(raw,form).encode()) for form in FORMS},
                source_SHA256=H(Path(__file__).read_bytes()), reused_observer_SHA256=H(BASE.read_bytes()),
                no_cadence_acceptance_assumed=True, files=0, native=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--shared-slot', action='store_true')
    parser.add_argument('--form', choices=(*FORMS,'both'), default='both')
    args=parser.parse_args()
    raw=ROM.read_bytes();assert H(raw)==PIN
    if not args.run:
        def deny(*a,**k):raise AssertionError('Source validation attempted file/process output')
        with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):q=validate(raw)
        print('SONIC CADENCE SOURCE '+json.dumps(q,separators=(',',':')),flush=True);return
    assert args.shared_slot,'Root native run requires the existing shared slot'
    from nightly_patch_guard_v1 import check
    from run_stdout_mesen_1110 import run
    import build_storage_guard_v1 as Storage
    Storage.preflight(private_root=SHARED,reserved_files=0,fresh=True)
    assert {p.name for p in SHARED.iterdir()}=={'candidate.nes','controller.lua'}
    target,script=SHARED/'candidate.nes',SHARED/'controller.lua'
    assert target.read_bytes()==raw
    original=script.read_bytes();guard=check(ROM)
    assert guard['ROM_sha256']==PIN
    try:
        for form in FORMS if args.form=='both' else (args.form,):
            script.write_text(controller(raw,form),encoding='utf-8',newline='\n')
            result=run(script,ROM,SHARED/'capture',PIN,120,extra_env={'SMB_STDOUT_IMAGES':'0'})
            print('SONIC CURRENT CADENCE '+json.dumps(dict(form=form,script_SHA256=result['script_SHA256'],receipt_SHA256=result['receipt_SHA256'],receipt=result['receipt']),separators=(',',':')),flush=True)
            assert result['passed'] and result['outputs_written']==0 and not result['images']
    finally:
        script.write_bytes(original)
        assert script.read_bytes()==original and target.read_bytes()==ROM.read_bytes()==raw and check(ROM)==guard
        assert {p.name for p in SHARED.iterdir()}=={'candidate.nes','controller.lua'}
        print('SONIC CADENCE SHARED RESTORED '+PIN,flush=True)


if __name__=='__main__':main()
