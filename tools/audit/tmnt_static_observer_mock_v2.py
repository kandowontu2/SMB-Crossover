"""Lua54 syntax and host-callback registration/order mock; no Mesen."""
from pathlib import Path
import argparse
import json
import sys


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--prepared',type=Path,required=True)
    p.add_argument('--lua-runtime',type=Path,required=True)
    a=p.parse_args();sys.path.insert(0,str(a.lua_runtime))
    from lupa.lua54 import LuaRuntime
    import hashlib
    def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
    lua=LuaRuntime(unpack_returned_tuples=True)
    mock='''
    host={exec=0,other=0,events=0,functions={}}
    emu={callbackType={exec=1,write=2,read=3},eventType={endFrame=1,inputPolled=2},memType={nesDebug=1,nesSpriteRam=2}}
    function emu.addMemoryCallback(fn,kind,first,last)
      if kind==1 then host.exec=host.exec+1;host.functions[#host.functions+1]=fn
      else host.other=host.other+1 end
      return host.exec+host.other
    end
    function emu.addEventCallback(fn,kind)host.events=host.events+1 end
    function emu.stop(code)end
    function emu.read(at,kind)return 0 end
    function emu.getState()return{}end
    function emu.convertAddress(a)return{address=0}end
    '''
    lua.execute(mock)
    lua.execute((a.prepared/'tmnt_static_exec_dispatcher_v1.lua').read_text())
    result=lua.execute('''
      local seen={};local added=false
      emu.addMemoryCallback(function(pc)seen[#seen+1]='first';if not added then added=true;emu.addMemoryCallback(function()seen[#seen+1]='late'end,1,0x1234)end end,1,0x1234)
      emu.addMemoryCallback(function()seen[#seen+1]='second'end,1,0x1234)
      emu.addMemoryCallback(function()seen[#seen+1]='range'end,1,0x1233,0x1234)
      emu.addMemoryCallback(function()end,2,0x2001)
      assert(host.exec==0 and host.other==1)
      TMNT_STATIC_EXEC.install();assert(host.exec==1)
      host.functions[1](0x1234);assert(table.concat(seen,',')=='first,second,range')
      seen={};host.functions[1](0x1234);assert(table.concat(seen,',')=='first,second,range,late')
      seen={};host.functions[1](0x1233);assert(table.concat(seen,',')=='range')
      local ok=pcall(function()emu.addMemoryCallback(function()end,2,0x2001)end);assert(not ok)
      local ok2=pcall(TMNT_STATIC_EXEC.install);assert(not ok2)
      local ok3=pcall(function()emu.addMemoryCallback(function()end,1,0x10000)end);assert(not ok3)
      assert(host.exec==1 and host.other==1)
      return TMNT_STATIC_EXEC.status().lua_exec_registrations
    ''')
    assert result==4
    actual=LuaRuntime(unpack_returned_tuples=True);actual.execute(mock)
    folder=a.prepared/'mock-startup';folder.mkdir(exist_ok=False)
    actual.globals().OUTPUT=folder.as_posix()+'/'
    actual.globals().TEST_DIR=folder.as_posix()+'/'
    actual.execute("L=setmetatable({},{__index=function()return 0 end}); B=setmetatable({},{__index=function()return 0 end})")
    # Parse all actual source first, then execute only startup callback/file
    # registration. No emulated callback, CPU or controller event is run.
    syntax=actual.eval('function(s)local f,e=load(s);assert(f,e);return true end')
    for name in ['tmnt_static_exec_dispatcher_v1.lua','run.lua','performance-observer.lua','chr-commit-observer.lua']:
        assert syntax((a.prepared/name).read_text())
    actual.execute((a.prepared/'run.lua').read_text())
    status=actual.eval('TMNT_STATIC_EXEC.status()')
    assert status['installed'] and status['host_exec_dispatchers']==1
    assert actual.eval('host.exec')==1 and status['lua_exec_registrations']>10
    proof=dict(passed=True,native_run=False,syntax_files=4,mock_order_range_and_runtime_safety_checks=9,
        complete_generated_harness_startup_host_exec_dispatchers=1,
        complete_generated_harness_startup_Lua_exec_registrations=status['lua_exec_registrations'],
        complete_generated_harness_startup_nonexec_host_registrations=status['host_nonexec_registrations'],
        script_sha256=sha(a.prepared/'run.lua'),core_sha256=sha(a.prepared/'tmnt_static_exec_dispatcher_v1.lua'),
        checker_sha256=sha(Path(__file__)),limits='Syntax and mock API startup/order checks only. No real emulated events or native image/CSV/JSON equivalence; this observer is not yet native-qualified.')
    (a.prepared/'mock-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(proof))


if __name__=='__main__':main()
