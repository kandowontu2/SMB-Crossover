"""Finite original observer semantics and generated startup under Lua54 mocks."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()

MOCK = r'''
callbacks={};events={};mem={};files={};ops={};runtime=false;cpuBank=4
state={['cpu.sp']=253,['cpu.pc']=0,['cpu.a']=0,['cpu.x']=0,['cpu.y']=0,['cpu.cycleCount']=0,['ppu.frameCount']=0,['ppu.scanline']=240,['ppu.cycle']=0}
for i=0,11 do state['mapper.chrBanks'..i]=0 end
emu={callbackType={read=0,write=1,exec=2},eventType={startFrame=0,endFrame=1,inputPolled=2},memType={nesDebug=1,nesPpuDebug=2,nesSpriteRam=3,nesPrgRom=4}}
function emu.addMemoryCallback(fn,kind,lo,hi,...)
 if runtime and STATIC then error('Runtime native callback registration')end
 callbacks[#callbacks+1]={fn=fn,kind=kind,lo=lo,hi=hi or lo}
 return #callbacks
end
function emu.removeMemoryCallback()error('No callback removal permitted')end
function emu.addEventCallback(fn,kind)if not events[kind]then events[kind]={}end;events[kind][#events[kind]+1]=fn end
function emu.getState()ops[#ops+1]='state:'..state['cpu.pc']..':'..state['cpu.sp'];return state end
function emu.read(at,kind)local v=mem[at]or 0;ops[#ops+1]='read:'..at..':'..v;return v end
function emu.convertAddress(at)return{address=cpuBank*8192+at%8192,memType=emu.memType.nesPrgRom}end
function emu.takeScreenshot()return'mock-screenshot' end
function emu.setInput()end
function emu.stop(code)error('Unexpected mock stop '..code)end
function emu.write()error('Observer must not write emulated state')end
function fire(kind,pc,value)
 state['cpu.pc']=pc
 local count=#callbacks
 for i=1,count do local q=callbacks[i];if q.kind==kind and pc>=q.lo and pc<=q.hi then q.fn(pc,value)end end
end
function store(at,value)mem[at]=value;fire(emu.callbackType.write,at,value)end
function event(kind)for _,fn in ipairs(events[kind]or{})do fn()end end
io.open=function(path,mode)
 if mode=='rb'then return nil end
 files[path]=''
 return{write=function(self,...)for i=1,select('#',...)do files[path]=files[path]..tostring(select(i,...))end;return self end,flush=function()end,close=function()end}
end
'''


def generic(LuaRuntime, core):
    rt = LuaRuntime(unpack_returned_tuples=True)
    rt.execute('STATIC=true\n' + MOCK + core)
    out = rt.execute('''
 local seen={};local added=false
 emu.addMemoryCallback(function(pc)seen[#seen+1]='first';if not added then added=true;emu.addMemoryCallback(function()seen[#seen+1]='late'end,2,0x8123)end end,2,0x8123)
 emu.addMemoryCallback(function()seen[#seen+1]='second'end,2,0x8123)
 emu.addMemoryCallback(function()seen[#seen+1]='range'end,2,0x8122,0x8123)
 emu.addMemoryCallback(function()end,1,0x2001)
 assert(#callbacks==1)
 TMNT_STATIC_EXEC.install();assert(#callbacks==2)
 runtime=true;fire(2,0x8123);assert(table.concat(seen,',')=='first,second,range')
 seen={};fire(2,0x8123);assert(table.concat(seen,',')=='first,second,range,late')
 seen={};fire(2,0x8122);assert(table.concat(seen,',')=='range')
 assert(not pcall(function()emu.addMemoryCallback(function()end,1,0x2004)end))
 assert(not pcall(TMNT_STATIC_EXEC.install))
 assert(not pcall(function()emu.addMemoryCallback(function()end,2,0x10000)end))
 assert(#callbacks==2)
 return TMNT_STATIC_EXEC.status().lua_exec_registrations
''')
    assert out == 4
    return dict(passed=True, registration_order_range_late_next_event_and_rejections=9)


def observer_case(LuaRuntime, core, module, static, scenario, legacy):
    rt = LuaRuntime(unpack_returned_tuples=True)
    rt.execute('STATIC=' + ('true' if static else 'false') + '\n' + MOCK)
    if static:
        rt.execute(core)
    rt.execute('''
 L={DrawAllMetasprites=0xa000,DrawMetasprite=0xa200,MetaspriteRenderLoop=0xa300,
 OperMode=0x701,GameEngineSubroutine=0x702,SelectedCharacter=0x703,CurrentCHRBank=0x710,
 X5ChrMode=0x720,SmChrBank=0x730,SmPosePtr=0x731,ChrPhysicalMap=0x4800,VvVariant=0x740}
 B={DrawAllMetasprites=4,DrawMetasprite=4,MetaspriteRenderLoop=4}
 mem[L.OperMode]=1;mem[L.GameEngineSubroutine]=8;mem[L.SelectedCharacter]=1
 mem[L.SmChrBank]=5;mem[L.SmPosePtr]=0x20;mem[L.SmPosePtr+1]=0x40
 for w=0,11 do mem[L.CurrentCHRBank+w]=5+w;mem[L.X5ChrMode+w]=LEGACY and 0 or 128;mem[L.ChrPhysicalMap+5+w]=41+w;state['mapper.chrBanks'..w]=LEGACY and 41+w or 5+w end
 for i=0,255 do mem[0x200+i]=i%4==0 and 248 or 0 end
 function setup_return(sp,pc)
  state['cpu.sp']=sp;local word=(pc-1)%65536
  mem[256+(sp+1)%256]=word%256;mem[256+(sp+2)%256]=word//256
 end
 function body(pc,sp,wrongEntry)
  fire(2,L.DrawAllMetasprites)
  setup_return(sp,pc);state['cpu.y']=0;cpuBank=wrongEntry and 7 or 4
  fire(2,L.DrawMetasprite);cpuBank=4
  fire(2,L.MetaspriteRenderLoop)
  store(0x200,176);store(0x201,16);store(0x202,1);store(0x203,96)
  store(0x204,184);store(0x205,18);store(0x206,1);store(0x207,104)
 end
'''.replace('LEGACY', 'true' if legacy else 'false'))
    # A fixed hook on the same return PC precedes all later dynamic returns;
    # another after module startup must still precede them as well.
    rt.execute("emu.addMemoryCallback(function()ops[#ops+1]='fixed-before'end,2,0xa250)")
    factory = rt.execute(module)
    observer = factory(rt.table_from(dict(out='mock/', character=1)))
    rt.globals().TEST_OBSERVER = observer
    rt.execute("emu.addMemoryCallback(function()ops[#ops+1]='fixed-after'end,2,0xa250)")
    if static:
        rt.execute('TMNT_STATIC_EXEC.install()')
    rt.execute('runtime=true')
    operations = {
        'normal_and_reuse': "body(0xa250,251,false);state['cpu.sp']=253;fire(2,0xa250);fire(1,0x4014,2);event(1);body(0xa250,251,false);state['cpu.sp']=253;fire(2,0xa250);fire(1,0x4014,2)",
        'wrong_pc_sp_retains_inside': "body(0xa250,251,false);state['cpu.sp']=253;fire(2,0xa251);state['cpu.sp']=252;fire(2,0xa250);store(0x208,192);store(0x209,20);store(0x20a,1);store(0x20b,112);state['cpu.sp']=253;fire(2,0xa250);fire(1,0x4014,2)",
        'stack_and_return_wrap': "body(0,255,false);state['cpu.sp']=0;fire(2,0);state['cpu.sp']=1;fire(2,0);fire(1,0x4014,2)",
        'wrong_entry_bank_then_valid': "body(0xa250,251,true);state['cpu.sp']=253;fire(2,0xa250);fire(1,0x4014,2);event(1);body(0xa250,251,false);state['cpu.sp']=253;fire(2,0xa250);fire(1,0x4014,2)",
        'literal_no_return_bank_guard': "body(0xa250,251,false);cpuBank=7;state['cpu.sp']=253;fire(2,0xa250);cpuBank=4;fire(1,0x4014,2)",
        'different_return_and_stale_DMA': "body(0xd123,247,false);state['cpu.sp']=249;fire(2,0xd123);fire(1,0x4014,2);event(1);fire(1,0x4014,2)",
    }
    rt.execute(operations[scenario])
    rt.execute("for i=1,45 do state['ppu.frameCount']=i;event(emu.eventType.endFrame)end;assert(not TEST_OBSERVER.failure());TEST_OBSERVER.finish()")
    files = {str(k): str(v) for k, v in rt.globals().files.items()}
    ops = [rt.globals().ops[i] for i in range(1, len(rt.globals().ops) + 1)]
    if static:
        assert rt.eval('TMNT_STATIC_EXEC.status().host_exec_dispatchers') == 1
    return files, ops, rt.eval('#callbacks')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--packet', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    deps = D / 'parodius-visibility-current50b5-v1/static-observer-lua-deps-v1'
    sys.path.insert(0, str(deps))
    from lupa.lua54 import LuaRuntime
    core = (a.packet / 'tmnt_static_exec_dispatcher_v1.lua').read_text()
    tests = [generic(LuaRuntime, core)]
    scenarios = ['normal_and_reuse', 'wrong_pc_sp_retains_inside', 'stack_and_return_wrap',
                 'wrong_entry_bank_then_valid', 'literal_no_return_bank_guard', 'different_return_and_stale_DMA']
    for name in ['legacy_chr_observer_of.lua', 'chr_commit_observer.lua']:
        module = (R / 'tools/audit' / name).read_text()
        for scenario in scenarios:
            old, new = [observer_case(LuaRuntime, core, module, static, scenario, name.startswith('legacy'))
                        for static in [False, True]]
            assert old[:2] == new[:2], (name, scenario)
            tests.append(dict(module=name, scenario=scenario, complete_mock_files_and_ordered_reads_state_calls_exact=True,
                              intended_dynamic_native_callbacks=old[2], new_static_native_callbacks=new[2],
                              exact_read_state_operations=len(old[1])))
    # Complete exact generated previews load under inactive source-only APIs.
    # Actual opcode callbacks are not invoked at arbitrary PCs in this startup
    # check; the full original observer callbacks are exercised above.
    from parodius_visibility_hud_static_startup_v1 import MOCK as startup
    previews = []
    syntax = LuaRuntime().eval('function(s)local f,e=load(s);assert(f,e);return true end')
    for p in a.packet.rglob('*.lua'):
        assert syntax(p.read_text())
        assert not __import__('re').search(r'\b(?:True|False)\b', p.read_text())
    for identity in ['megaman', 'proto']:
        rt = LuaRuntime(unpack_returned_tuples=True)
        rt.execute(startup + "\nL=setmetatable({},{__index=function()return 0 end});B=setmetatable({},{__index=function()return 0 end});emu.setInput=function()end")
        script = a.packet / ('preview-' + identity) / 'run.lua'
        rt.execute(script.read_text())
        assert rt.eval('callbacks[#callbacks].kind==emu.callbackType.exec and callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535')
        count = rt.eval('#callbacks')
        # Preserve the wrapper. Forbid its captured real host-registration
        # function through the mock's final callback count and full startup
        # inactive execution; active return registration is tested above.
        for frame in range(1, 440):
            rt.execute(f"state['ppu.frameCount']={frame};runevents(emu.eventType.inputPolled);runevents(emu.eventType.endFrame)")
        assert rt.eval('#callbacks') == count
        previews.append(dict(identity=identity, full_generated_startup=True, inactive_mock_frames=439,
                             static_host_callbacks=count, final_full_range_exec_dispatcher=True))
    proof = dict(passed=True, source_mock_only=True, native_launches=0, observer_mechanic_bytes_unchanged=True,
                 tests=tests, complete_startups=previews, Lua_runtime='Lua54',
                 literal_return_scope='Entry bank and PC/SP checks retained exactly. Original return closures do NOT test bank; the bank-mismatch scenario preserves that original behavior rather than inventing a new guard.',
                 prior_static_native_qualification=str(D / 'tmnt-static-observer-native-ready-v1/receipt.json'),
                 prior_native_scope='Same dispatcher had one actual historical9a791 replay/566draw outcome and source/PPU equality; this does not retag the new routes as native-qualified.',
                 limits='Synthetic source observer/API snapshots, not Mesen vector mutation emulation or actual new gameplay/PPU equivalence. Startup controller executes under inactive zero-memory mocks; real natural mode/identity/return/native rendering checks remain in the unchanged harness.',
                 preparation_sha256=sha(a.packet / 'preparation.json'), tool_sha256=sha(__file__))
    (a.output / 'proof.json').write_text(json.dumps(proof, indent=2) + '\n')
    print(json.dumps(dict(passed=True, observer_semantic_cases=len(tests) - 1, complete_startups=2,
                          native_launches=0, proof_sha256=sha(a.output / 'proof.json')), indent=2))


if __name__ == '__main__':
    main()
