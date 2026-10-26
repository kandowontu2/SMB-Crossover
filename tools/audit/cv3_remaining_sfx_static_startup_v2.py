"""Load each complete prepared static fixture under linked-label read-only Lua54 APIs."""
from pathlib import Path
import argparse,hashlib,json,sys
from parodius_visibility_hud_static_startup_v1 import MOCK as BASE_MOCK
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--lua-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);z=json.loads((a.packet/'preparation.json').read_text());sys.path.insert(0,str(a.lua_root));import lupa.lua54 as runtime
 rows=[]
 mock=BASE_MOCK+'\nL={};inputCalls=0;lastInput={};inputTrace={};fileTrace={}\n'+'''
emu.setInput=function(b,port)inputCalls=inputCalls+1;lastInput=b;local keys={};for k,v in pairs(b)do if v then keys[#keys+1]=k end end;table.sort(keys);inputTrace[#inputTrace+1]=tostring(port)..':'..table.concat(keys,',')end
io.open=function(path,mode)
 if mode=='rb'then return nil end
 if not fileTrace[path]then fileTrace[path]={}end
 return{write=function(self,...)for i=1,select('#',...)do fileTrace[path][#fileTrace[path]+1]=tostring(select(i,...))end;return self end,flush=function()end,close=function()end}
end
function observerOutput()local names={};for name in pairs(fileTrace)do names[#names+1]=name end;table.sort(names);local t={};for _,name in ipairs(names)do t[#t+1]=name..'\\n'..table.concat(fileTrace[name])end;return table.concat(t,'\\n===\\n')end
function controllerOutput()return table.concat(inputTrace,'|')end
'''
 for entry in z['cases']:
  script=Path(entry['static_script']);assert sha(script)==entry['static_script_sha256'];labels={}
  for line in script.with_name('candidate.lbl').read_text().splitlines():
   t=line.split()
   if len(t)>=3 and t[0]=='al':labels[t[2].lstrip('.')]=int(t[1],16)
  runs=[];counts=[]
  for is_static,path in[(False,script.with_name('original-run.lua')),(True,script)]:
   rt=runtime.LuaRuntime(unpack_returned_tuples=True);rt.execute(mock)
   for n,v in labels.items():rt.globals().L[n]=v
   rt.globals().OUTPUT='synthetic-output/';rt.execute(path.read_text());count=rt.eval('#callbacks');counts.append(count)
   if is_static:assert rt.eval('callbacks[#callbacks].kind==emu.callbackType.exec and callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535')
   rt.execute("emu.addMemoryCallback=function()error('Runtime memory registration forbidden')end;emu.removeMemoryCallback=function()error('Runtime memory removal forbidden')end;emu.write=function()error('Inactive startup must not write gameRAM')end")
   runs.append(rt)
  for frame in range(1,440):
   for rt in runs:rt.execute(f"state['ppu.frameCount']={frame};state['ppu.scanline']=-1;runevents(emu.eventType.startFrame);runevents(emu.eventType.inputPolled);state['ppu.scanline']=240;runevents(emu.eventType.endFrame)")
   assert runs[0].globals().observerOutput()==runs[1].globals().observerOutput()and runs[0].globals().controllerOutput()==runs[1].globals().controllerOutput(),(entry['name'],frame)
  for i,rt in enumerate(runs):rt.execute("for _,q in ipairs(callbacks)do if q.kind==emu.callbackType.exec then state['cpu.pc']=q.lo;q.fn(q.lo)end end");assert rt.eval('#callbacks')==counts[i]
  assert runs[0].globals().observerOutput()==runs[1].globals().observerOutput()and runs[0].globals().controllerOutput()==runs[1].globals().controllerOutput()
  (a.output/(entry['name']+'-startup-output.txt')).write_text(runs[1].globals().observerOutput());(a.output/(entry['name']+'-controller-output.txt')).write_text(runs[1].globals().controllerOutput());rt=runs[1]
  rows.append(dict(name=entry['name'],script_sha256=sha(script),configuration_sha256=entry['configuration_sha256'],actual_linked_labels=len(labels),startup_memory_callbacks=counts[1],old_startup_memory_callbacks=counts[0],all_original_outputs_and_controller_streams_identical_each_frame=True,output_sha256=sha(a.output/(entry['name']+'-startup-output.txt')),controller_sha256=sha(a.output/(entry['name']+'-controller-output.txt')),last_callback=dict(kind='exec',start=0,end=65535),mock_frames=439,actual_original_controller_policy_calls=rt.eval('inputCalls'),runtime_memory_registrations=0,runtime_memory_removals=0,game_RAM_writes=0,Lua_version=rt.eval('_VERSION')))
 result=dict(passed=True,native_executed=False,rows=rows,packet_sha256=sha(a.packet/'preparation.json'),Lua54_module=dict(path=runtime.__file__,sha256=sha(runtime.__file__)),mock_source_sha256=sha(Path(__file__).with_name('parodius_visibility_hud_static_startup_v1.py')),tool_sha256=sha(__file__),scope='Both complete real generated historical fixtures load with original mode/controller/guard code, actual linked labels and startup-last dispatcher. Inactive-game callbacks/controller execute439 synthetic frames under forbidden runtime registration/removal/game writes. Active return/DMA semantics and failure controls separately qualified. This is not native runtime observation equivalence.')
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
