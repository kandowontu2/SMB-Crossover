"""Load complete prepared Lua with actual runner labels under inactive-game mocks."""
from pathlib import Path
import argparse,hashlib,json,sys
from parodius_visibility_hud_static_startup_v1 import MOCK
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);p.add_argument('--lua-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);z=json.loads((a.packet/'preparation.json').read_text());script=Path(z['script']);assert sha(script)==z['script_sha256']
 sys.path.insert(0,str(a.lua_root));from lupa import LuaRuntime
 rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(MOCK+'\nL={}');labels={}
 for line in script.with_name('candidate.lbl').read_text().splitlines():
  fields=line.split()
  if len(fields)>=3 and fields[0]=='al':labels[fields[2].lstrip('.')]=int(fields[1],16)
 for n,v in labels.items():rt.globals().L[n]=v
 rt.execute(script.read_text(encoding='utf-8'));count=rt.eval('#callbacks');assert rt.eval('callbacks[#callbacks].kind==emu.callbackType.exec and callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==0xffff')
 rt.execute("emu.addMemoryCallback=function()error('Runtime callback registration forbidden')end;emu.removeMemoryCallback=function()error('Runtime callback removal forbidden')end")
 for frame in range(1,440):rt.execute(f"state['ppu.frameCount']={frame};state['ppu.scanline']=-1;runevents(emu.eventType.startFrame);runread(0);state['ppu.scanline']=240;runevents(emu.eventType.endFrame)")
 rt.execute('runread(0);callbacks[#callbacks].fn(0xe007)');assert rt.eval('#callbacks')==count
 q=dict(passed=True,native_run=False,ROM_modified=False,Lua_runtime=rt.eval('_VERSION'),all_memory_callbacks_registered_before_runtime=True,total_static_memory_callbacks=count,final_callback=dict(kind='exec',start=0,end=65535),actual_linked_labels=len(labels),executed_mock_frames=439,raster_gate_original_endFrame=439,runtime_registration_attempts=0,script_sha256=sha(script),preparation_sha256=sha(a.packet/'preparation.json'),tool_sha256=sha(Path(__file__)),mock_source_sha256=sha(Path(__file__).with_name('parodius_visibility_hud_static_startup_v1.py')),labels_sha256=sha(script.with_name('candidate.lbl')),limits='Complete generated Lua and actual controller policy/guard load under synthetic inactive-game APIs. Actual runner exposes L labels before loading; v1 mock omitted L and failed before runtime. No emulation, outcome, PPU or gameplay verdict. Return/DMA semantics checked separately. Native same-input prefix proof remains required.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(q))

if __name__=='__main__':main()
