"""Check profiler nested IRQ/NMI cycle arithmetic and fail-closed return guards."""
from pathlib import Path
import argparse,hashlib,json,sys
from check_tmnt_render_oa import load,address
from cv3_dmc_complete_cpu_v1 import LaneArena
from observe_chip_committed_write import lua
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fixture',type=Path,required=True);p.add_argument('--lua-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);prep=json.loads((a.fixture/'preparation.json').read_text());P=json.loads((a.fixture/'configuration.json').read_text());b=load(Path(prep['ROM']));sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
 def make():
  rt=LuaRuntime(unpack_returned_tuples=True);q=LaneArena(b,14);q.put(SelectedCharacter=14,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,NmiDisable=255);callbacks=[];st={'cpu.pc':0,'cpu.sp':253,'cpu.a':7,'cpu.x':3,'cpu.y':1,'cpu.ps':32,'cpu.cycleCount':0,'ppu.frameCount':391,'ppu.scanline':241,'ppu.cycle':0};emu=rt.table_from({'memType':rt.table_from({'nesDebug':1}),'callbackType':rt.table_from({'write':1,'exec':2}),'eventType':rt.table_from({'endFrame':1})});emu['getState']=lambda:rt.table_from(st);emu['read']=lambda at,kind:q.m[int(at)];emu['convertAddress']=lambda at:rt.table_from({'address':q.m.banks[(int(at)-0x8000)//8192]*8192+(int(at)&8191)if int(at)>=0x8000 else int(at)});emu['addMemoryCallback']=lambda f,k,lo,hi=None:callbacks.append((f,k,int(lo),int(hi if hi is not None else lo)));rt.globals().emu=emu;rt.execute("L={};OUTPUT='mock/';events={};outputs={};emu.addEventCallback=function(fn)events[#events+1]=fn end;function frame()for _,fn in ipairs(events)do fn()end end;io.open=function(name,mode)outputs[name]={};return{write=function(self,...)for i=1,select('#',...)do outputs[name][#outputs[name]+1]=tostring(select(i,...))end;return self end,close=function()end}end;function text(n)return table.concat(outputs['mock/'..n]or{})end")
  for n in['SelectedCharacter','OperMode','OperMode_Task','GameEngineSubroutine','CurrentBank','CurrentBankC','NmiDisable','NmiSkipped','ShouldSkipDrawSprites','FramesSinceLastSpriteDraw','RgAudioSong','RgAudioRequest']:rt.globals().L[n]=address(b,n)
  rt.execute('CHIP_IDLE_PROFILE='+lua(P)+'\n'+(ROOT/'tools/audit/chip_idle_profile_capture_v1.lua').read_text());emu['addMemoryCallback']=lambda *args:(_ for _ in()).throw(AssertionError('Runtime registration'));emu['write']=lambda *args:(_ for _ in()).throw(AssertionError('Observer writes'))
  for _ in range(390):rt.globals().frame()
  def fire(pc,sp,cycle):
   st.update({'cpu.pc':pc,'cpu.sp':sp,'cpu.cycleCount':cycle})
   for fn,k,lo,hi in callbacks:
    if k==2 and lo<=pc<=hi:fn(pc)
  return rt,q,st,fire,callbacks
 def ret(target,bank,base):
  return next(pc for pc in P['return_pcs']if base<=pc<base+8192 and b['raw'][16+bank*8192+pc-base-3:16+bank*8192+pc-base]==bytes([0x20,target&255,target>>8]))
 game=address(b,'GameLoop');audio=address(b,'AudioUpdate');expanded=address(b,'ExpandedAudioUpdate');gr=ret(game,126,0x8000);ar=ret(audio,127,0xe000);er=ret(expanded,127,0xe000)
 rt,q,st,fire,cb=make()
 def stack(sp,returnPC):q.m[0x100+(sp+1)%256]=(returnPC-1)&255;q.m[0x100+(sp+2)%256]=(returnPC-1)>>8
 stack(251,gr);fire(game,251,100)
 q.m[0x1f9]=32;q.m[0x1fa]=(game+2)&255;q.m[0x1fb]=(game+2)>>8;fire(P['interrupts']['NMI']['address'],248,200)
 stack(240,ar);fire(audio,240,220);stack(238,er);fire(expanded,238,230)
 q.m[0x1ec]=32;q.m[0x1ed]=(expanded+2)&255;q.m[0x1ee]=(expanded+2)>>8;fire(P['interrupts']['IRQ']['address'],235,240);fire(P['interrupts']['IRQReturn']['address'],235,270)
 fire(er,240,300);fire(ar,242,350);fire(P['interrupts']['NMIReturn']['address'],248,400);fire(gr,253,600)
 for _ in range(390,1300):rt.globals().frame()
 spans=[json.loads(x)for x in rt.globals().text('profile-spans.jsonl').splitlines()];by={x['name']:x for x in spans};assert by['GameLoop']['cpuCycles']==287 and by['GameLoop']['interruptCycles']==213 and by['GameLoop']['exclusiveCpuCycles']==287;assert by['AudioUpdate']['cpuCycles']==87 and by['AudioUpdate']['exclusiveCpuCycles']==60 and by['ExpandedAudioUpdate']['cpuCycles']==27
 badrt,badq,badst,badfire,_=make();badq.m[0x1fc]=255;badq.m[0x1fd]=0x59
 try:badfire(game,251,100)
 except Exception as ex:assert'Unbound actual return'in str(ex)
 else:raise AssertionError('Unknown return accepted')
 (a.output/'spans.json').write_text(json.dumps(spans,indent=2)+'\n');result=dict(passed=True,native_executed=False,ROM_sha256=prep['ROM_sha256'],script_sha256=prep['script_sha256'],synthetic_nested_hardware_entry7_RTI6_costs=dict(NMI=213,IRQ=43),Main_elapsed500_minus_NMI213_equals287=True,nested_IRQ_not_double_subtracted_from_Main=True,Audio_elapsed130_minus_IRQ43_equals87=True,Audio_exclusive_after_child27_equals60=True,unknown_return_rejected=True,fixed_runtime_callbacks=len(cb),tool_sha256=sha(__file__),scope='Synthetic chronological event injection into the exact Lua module, not emulated NMI/PPU timing or native cost evidence. Demonstrates arithmetic/ownership, real pinned entry/return hooks and fail-closed unknown-return handling only.')
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
