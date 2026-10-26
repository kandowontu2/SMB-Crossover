"""v2 load exact0c45 BASIC effect/mode fixture; execute inactive controller/guards with static API."""
from pathlib import Path
import argparse,hashlib,json,sys
from parodius_visibility_hud_static_startup_v1 import MOCK
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fixture',type=Path,required=True);p.add_argument('--lua-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);z=json.loads((a.fixture/'preparation.json').read_text());script=Path(z['script']);assert sha(script)==z['script_sha256'];sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
 rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(MOCK.replace("emu.setInput=function()error('Input not called in source-only startup test')end","emu.setInput=function()inputCalls=inputCalls+1 end")+'\nL={};OUTPUT="synthetic/";inputCalls=0');labels={}
 for line in(a.fixture/'candidate.lbl').read_text().splitlines():
  t=line.split()
  if len(t)>=3 and t[0]=='al':labels[t[2].lstrip('.')]=int(t[1],16)
 for n,v in labels.items():rt.globals().L[n]=v
 rt.execute(script.read_text());count=rt.eval('#callbacks');assert rt.eval('callbacks[#callbacks].kind==emu.callbackType.exec and callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535')
 rt.execute("emu.addMemoryCallback=function()error('Runtime memory registration forbidden')end;emu.removeMemoryCallback=function()error('Runtime memory removal forbidden')end;emu.write=function()error('Inactive fixture must not write gameRAM')end")
 for frame in range(1,440):rt.execute(f"state['ppu.frameCount']={frame};state['ppu.scanline']=-1;runevents(emu.eventType.startFrame);runevents(emu.eventType.inputPolled);state['ppu.scanline']=240;runevents(emu.eventType.endFrame)")
 rt.execute("for _,q in ipairs(callbacks)do if q.kind==emu.callbackType.exec then state['cpu.pc']=q.lo;q.fn(q.lo)end end");assert rt.eval('#callbacks')==count
 result=dict(passed=True,native_executed=False,ROM_sha256=z['ROM_sha256'],script_sha256=z['script_sha256'],actual_linked_labels=len(labels),actual_numeric_mode_configuration=json.loads((a.fixture/'configuration.json').read_text())['mode'],fixed_startup_callbacks=count,last_dispatcher=dict(start=0,end=65535),inactive_mock_frames=439,actual_controller_calls=rt.eval('inputCalls'),runtime_registration_removal_game_writes=0,Lua_runtime=rt.eval('_VERSION'),tool_sha256=sha(__file__),scope='Complete generated0c45 fixture loading and inactive actual controller/fixed hook execution inLua5.4. Active actual cast/NMI/queue/image logic separately tested by assembled CPU replay. No native run or140-update gameplay verdict.')
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
