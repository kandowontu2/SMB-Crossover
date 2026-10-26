"""Load the complete prepared Lua under read-only mocks; check registration phase."""
from pathlib import Path
import argparse,hashlib,json,sys
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
MOCK='''
callbacks={};events={};state={['cpu.sp']=253,['cpu.pc']=0,['cpu.cycleCount']=0,['ppu.frameCount']=0,['ppu.scanline']=240,['ppu.cycle']=0}
for i=0,11 do state['mapper.chrBanks'..i]=0 end
emu={memType={nesDebug=1,nesPpuDebug=2,nesSpriteRam=3,nesPpuMemory=4},cpuType={nes=0},callbackType={read=0,write=1,exec=2},eventType={startFrame=0,endFrame=1,inputPolled=2}}
emu.read=function()return 0 end
emu.getState=function()return state end
emu.convertAddress=function(a)return{address=a}end
emu.addMemoryCallback=function(fn,kind,lo,hi,cpu,mem)callbacks[#callbacks+1]={fn=fn,kind=kind,lo=lo,hi=hi or lo,cpu=cpu,mem=mem}end
emu.addEventCallback=function(fn,kind)if not events[kind]then events[kind]={}end;events[kind][#events[kind]+1]=fn end
emu.stop=function()error('Unexpected mock stop')end
emu.setInput=function()error('Input not called in source-only startup test')end
emu.takeScreenshot=function()return''end
local actualOpen=io.open
io.open=function(path,mode)
 if mode=='rb'then return nil end
 return{write=function(self,...)return self end,flush=function()end,close=function()end}
end
function runevents(kind)for _,fn in ipairs(events[kind]or{})do fn()end end
function runread(address)for _,q in ipairs(callbacks)do if q.kind==0 and q.mem==4 and address>=q.lo and address<=q.hi then q.fn(address)end end end
'''

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--lua-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);z=json.loads((a.packet/'preparation.json').read_text());script=Path(z['script']);assert sha(script)==z['script_sha256']
 sys.path.insert(0,str(a.lua_root));from lupa import LuaRuntime
 rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(MOCK);rt.execute(script.read_text(encoding='utf-8'));count=rt.eval('#callbacks');assert rt.eval('callbacks[#callbacks].kind==emu.callbackType.exec and callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==0xffff')
 rt.execute("emu.addMemoryCallback=function()error('Runtime callback registration forbidden')end;emu.removeMemoryCallback=function()error('Runtime callback removal forbidden')end")
 # Real callback bodies execute under inactive-game mocks through the exact
 # original raster activation boundary, without native emulator execution.
 for frame in range(1,440):
  rt.execute(f"state['ppu.frameCount']={frame};state['ppu.scanline']=-1;runevents(emu.eventType.startFrame);runread(0);state['ppu.scanline']=240;runevents(emu.eventType.endFrame)")
 rt.execute('runread(0);callbacks[#callbacks].fn(0xe007)');assert rt.eval('#callbacks')==count
 q=dict(passed=True,native_run=False,ROM_modified=False,Lua_runtime=rt.eval('_VERSION'),all_memory_callbacks_registered_before_runtime=True,total_static_memory_callbacks=count,final_callback=dict(kind='exec',start=0,end=65535),executed_mock_frames=439,raster_gate_original_endFrame=439,runtime_registration_attempts=0,script_sha256=sha(script),preparation_sha256=sha(a.packet/'preparation.json'),tool_sha256=sha(Path(__file__)),limits='Complete actual generated Lua and actual controller policy/guard load under synthetic inactive-game APIs; no emulation, outcome, PPU or gameplay verdict. Return/DMA semantics checked separately. Native same-input prefix proof remains required.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(q))

if __name__=='__main__':main()
