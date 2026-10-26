"""Load complete UNRUN menu fixture and qualify static/finalization observation order."""
from pathlib import Path
import argparse,hashlib,json,sys
from parodius_visibility_hud_cancel_observer_cpu_v1 import runtime
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['preparation','lua-root','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);sys.path.insert(0,str(a.lua_root));from lupa import LuaRuntime
 z=json.loads((a.preparation/'menu/preparation.json').read_text());script=Path(z['script']);text=script.read_text();assert sha(script)==z['script_sha256']
 expose='\nfunction AREA_LEASE_TEST_COUNTS(a,b,c)PLchecks=a;PLcustom=b;PLblank=c end\n'
 # Use the complete actual generated chunk; exposed lexical counters are
 # synthetic source-test controls only, never part of a prepared native file.
 from parodius_visibility_hud_static_startup_v1 import MOCK
 rt=LuaRuntime(unpack_returned_tuples=True)
 rt.execute(MOCK+"\nL={}\nMOCK_LOGS={};io.open=function(path,mode)if mode=='rb'then return nil end;MOCK_LOGS[path]=MOCK_LOGS[path]or'';return{write=function(self,x)MOCK_LOGS[path]=MOCK_LOGS[path]..x;return self end,flush=function()end,close=function()end}end")
 for line in script.with_name('candidate.lbl').read_text().splitlines():
  f=line.split()
  if len(f)>=3 and f[0]=='al':rt.globals().L[f[2].lstrip('.')]=int(f[1],16)
 rt.execute('emu.getScreenBuffer=function()return{}end');rt.execute(text+expose);count=rt.eval('#callbacks')
 assert rt.eval('callbacks[#callbacks].kind==emu.callbackType.exec and callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==0xffff')
 rt.execute("emu.addMemoryCallback=function()error('Runtime registration forbidden')end;emu.removeMemoryCallback=function()error('Runtime removal forbidden')end")
 for frame in range(1,440):
  rt.execute(f"state['ppu.frameCount']={frame};state['ppu.scanline']=-1;runevents(emu.eventType.startFrame);runread(0);state['ppu.scanline']=240;runevents(emu.eventType.endFrame)")
 assert rt.eval('#callbacks')==count
 early='emu.addEventCallback(function()PARODIUS_HUD_LEASE_FINISH()end,emu.eventType.endFrame)'
 native='emu.addEventCallback(function()\n wall=wall+1'
 lines=[text[:text.index(s)].count('\n')+1 for s in [early,native]];indices=[]
 ev=rt.globals().events[rt.globals().emu.eventType.endFrame]
 for line in lines:
  matches=[i for i in range(1,len(ev)+1)if rt.eval("function(fn)return debug.getinfo(fn,'S').linedefined end")(ev[i])==line]
  assert len(matches)==1;indices.append(matches[0])
 assert indices[0]<indices[1]
 rt.execute("state['ppu.frameCount']=1800;state['ppu.scanline']=240")
 try:ev[indices[0]]()
 except Exception as ex:assert 'Meaningful all-life displayed HUD pairs'in str(ex)
 else:raise AssertionError('Missing meaningful pair scope accepted')
 rt.globals().AREA_LEASE_TEST_COUNTS(1574,1564,10);ev[indices[0]]()
 path=json.loads(script.with_name('config.json').read_text())['output']+'hud-lease-native-result.json'
 result=json.loads(rt.globals().MOCK_LOGS[path]);assert result['passed']and result['visible_pair_checks']==1574
 rt.globals().MOCK_LOGS[path]='';rt.execute("state['ppu.frameCount']=1799");ev[indices[0]]();assert rt.globals().MOCK_LOGS[path]==''
 for n in ['parodius_visibility_hud_scroll_native_v2.lua','parodius_visibility_hud_native_v1.lua','parodius_visibility_postdma_static_observer_v1.lua','parodius_visibility_postdma_bridge_v1.lua']:
  assert text.count((ROOT/'tools/audit'/n).read_text())==1
 old=(ROOT/'tools/audit/parodius_visibility_hud_lease_native_v1.lua').read_text();new=(ROOT/'tools/audit/parodius_visibility_hud_lease_native_v2.lua').read_text()
 split='emu.addEventCallback(function()\n if emu.getState()';assert old[:old.index(split)]==new[:new.index('PARODIUS_HUD_LEASE_FINISH=function()')]
 q=dict(passed=True,native_run=False,ROM_sha256=z['ROM_sha256'],script_sha256=sha(script),memory_callbacks=count,
        full_static_dispatcher_last=True,runtime_registration_attempts=0,complete_generated_mock_frames=439,
        additional_finalizer_event_index=indices[0],original_stop_event_index=indices[1],original_five_registration_order_unchanged=True,
        all_original_native_scroll_HUD_bridge_guard_bodies_exact=True,original_all_life_pair_start_guard_exact=True,
        finalizer_controls=['insufficient-pairs-rejected','sufficient-pairs-write-before-stop-slot','nonterminal-no-write'],
        mock_only_counter_setup=True,tool_sha256=sha(Path(__file__)),
        limits='Complete actual generated source/registration startup under inactive untimed read-only API mocks. Synthetic counter controls test finalization order/threshold only, and are absent from native script. No real cold/menu/pipe/area/Buffer2/PPU/IRQ/DMA or timing outcome. Original missing F35 sixth receipt remains absent and aggregateFALSE.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
