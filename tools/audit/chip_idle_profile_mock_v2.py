"""Source-only full fixture startup and actual6502 Audio profiler validation."""
from pathlib import Path
import argparse,hashlib,json,sys
from parodius_visibility_hud_static_startup_v1 import MOCK
from check_tmnt_render_oa import load,address,Memory
from cv3_dmc_complete_cpu_v1 import LaneArena
from verify_native_relocation import NesMPU
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fixture',type=Path,required=True);p.add_argument('--lua-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);z=json.loads((a.fixture/'preparation.json').read_text());script=Path(z['script']);assert sha(script)==z['script_sha256'];cfg=json.loads((a.fixture/'configuration.json').read_text());sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
 # Complete original1300 script: inactive fixture must STILL reject its missing
 # gameplay coverage, after the newly registered profile finalization callback.
 rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(MOCK.replace("emu.setInput=function()error('Input not called in source-only startup test')end","emu.setInput=function()end")+"\nOUTPUT='synthetic/';L={};outputs={};io.open=function(name,mode)if mode=='rb'then error('Inactive fixture must not request source gold')end;outputs[name]={};return{write=function(self,...)for i=1,select('#',...)do outputs[name][#outputs[name]+1]=tostring(select(i,...))end;return self end,flush=function()end,close=function()end}end")
 for line in Path(z['ROM']).with_suffix('.lbl').read_text().splitlines():
  t=line.split()
  if len(t)>=3 and t[0]=='al':rt.globals().L[t[2].lstrip('.')]=int(t[1],16)
 rt.execute(script.read_text(encoding='utf-8'));count=rt.eval('#callbacks');rt.execute("emu.addMemoryCallback=function()error('Runtime registration forbidden')end;emu.removeMemoryCallback=function()error('Runtime removal forbidden')end;emu.write=function()error('Observer emulated writes forbidden')end")
 failure=None
 for frame in range(1,1301):
  try:rt.execute(f"state['ppu.frameCount']={frame};runevents(emu.eventType.inputPolled);runevents(emu.eventType.endFrame)")
  except Exception as ex:failure=str(ex);break
 assert frame==1300 and failure and 'Sustained actual active-game observations'in failure;assert rt.eval('#callbacks')==count;assert rt.eval("outputs['synthetic/profile-summary.json']~=nil")
 # Actual6502 whole AudioUpdate calls feed the new observer's real startup
 # callbacks. No original-controller/native/PPU verdict is implied.
 b=load(Path(z['ROM']));q=LaneArena(b,14);q.put(SelectedCharacter=0,OperMode=0,OperMode_Task=3,GameEngineSubroutine=8,CdVariant=0,CrossoverBehaviorVersion=0,CurrentBank=215,CurrentBankC=166);live={'c':None};callbacks=[]
 rt2=LuaRuntime(unpack_returned_tuples=True)
 def dispatch(kind,at,value=None):
  for f,k,lo,hi in callbacks:
   if k==kind and lo<=at<=hi:f(at,value)if value is not None else f(at)
 class Watched(Memory):
  def __setitem__(self,at,v):
   if isinstance(at,int):dispatch(1,at,v)
   super().__setitem__(at,v)
 m=Watched(b);list.__setitem__(m,slice(None),list(q.m));m.banks=q.m.banks[:];q.m=m
 def state():
  c=live['c'];return rt2.table_from({'cpu.pc':c.pc if c else 0,'cpu.sp':c.sp if c else 253,'cpu.a':c.a if c else 0,'cpu.x':c.x if c else 0,'cpu.y':c.y if c else 0,'cpu.ps':c.p if c else 0x20,'cpu.cycleCount':c.processorCycles if c else 0,'ppu.frameCount':390,'ppu.scanline':241,'ppu.cycle':0})
 emu=rt2.table_from({'memType':rt2.table_from({'nesDebug':1}),'callbackType':rt2.table_from({'write':1,'exec':2}),'eventType':rt2.table_from({'endFrame':1})});emu['getState']=state;emu['read']=lambda at,kind:q.m[int(at)];emu['convertAddress']=lambda at:rt2.table_from({'address':q.m.banks[(int(at)-0x8000)//8192]*8192+(int(at)&8191)if int(at)>=0x8000 else int(at)});emu['addMemoryCallback']=lambda f,k,lo,hi=None:callbacks.append((f,k,int(lo),int(hi if hi is not None else lo)));rt2.globals().emu=emu
 rt2.execute("L={};OUTPUT='cpu/';events={};outputs={};emu.addEventCallback=function(fn,kind)events[#events+1]=fn end;function stepFrame()for _,fn in ipairs(events)do fn()end end;io.open=function(name,mode)outputs[name]={};return{write=function(self,...)for i=1,select('#',...)do outputs[name][#outputs[name]+1]=tostring(select(i,...))end;return self end,close=function()end}end;function text(name)return table.concat(outputs[name]or{})end")
 from observe_chip_committed_write import lua
 for name in ['SelectedCharacter','OperMode','OperMode_Task','GameEngineSubroutine','CurrentBank','CurrentBankC','NmiDisable','NmiSkipped','ShouldSkipDrawSprites','FramesSinceLastSpriteDraw','RgAudioSong','RgAudioRequest']:rt2.globals().L[name]=address(b,name)
 rt2.execute('CHIP_IDLE_PROFILE='+lua(cfg)+'\n'+(ROOT/'tools/audit/chip_idle_profile_capture_v1.lua').read_text(encoding='utf-8'));static=len(callbacks);emu['addMemoryCallback']=lambda *args:(_ for _ in()).throw(AssertionError('Runtime registration forbidden'));emu['removeMemoryCallback']=lambda *args:(_ for _ in()).throw(AssertionError('Runtime removal forbidden'));emu['write']=lambda *args:(_ for _ in()).throw(AssertionError('Emulated observer writes forbidden'))
 for _ in range(390):rt2.globals().stepFrame()
 q.put(SelectedCharacter=14,OperMode=1,OperMode_Task=3,GameEngineSubroutine=8,CdVariant=0,CrossoverBehaviorVersion=0,AreaMusicQueue=1)
 target=address(b,'AudioUpdate');ret=next(pc for pc in cfg['return_pcs']if 0xe000<=pc and b['raw'][16+127*8192+pc-0xe000-3:16+127*8192+pc-0xe000]==bytes([0x20,target&255,target>>8]));cycles=[]
 for call in range(4):
  c=NesMPU(memory=q.m,pc=target);c.a,c.x,c.y,c.p,c.sp=0x55,7,3,0x24,0xfd;c.stPushWord((ret-1)&65535);live['c']=c
  for _ in range(100000):
   dispatch(2,c.pc)
   if c.pc==ret and c.sp==253:break
   c.step()
  else:raise AssertionError('Actual AudioUpdate timeout')
  cycles.append(c.processorCycles);q.put(AreaMusicQueue=0)
 for _ in range(390,1300):rt2.globals().stepFrame()
 assert len(callbacks)==static
 texts={n:rt2.globals().text('cpu/'+n)for n in['profile-summary.json','profile-spans.jsonl','profile-snapshots.jsonl','profile-boundaries.jsonl']}
 # Binary snapshot data can include arbitrary bytes; LuaRuntime uses UTF8
 # strings by default, so obtain it through Lua byte-array conversion only.
 summary=json.loads(texts['profile-summary.json']);spans=[json.loads(x)for x in texts['profile-spans.jsonl'].splitlines()];audio=[x for x in spans if x['name']=='AudioUpdate'];assert len(audio)==4 and[x['cpuCycles']for x in audio]==cycles and all(x['interruptCycles']==0 for x in audio);assert summary['source_returns']==4
 for name in['profile-summary.json','profile-spans.jsonl','profile-snapshots.jsonl','profile-boundaries.jsonl']:(a.output/name).write_text(texts[name])
 result=dict(passed=True,native_executed=False,ROM_sha256=z['ROM_sha256'],script_sha256=z['script_sha256'],complete_generated_startup_callbacks=count,complete_original1300_missing_gameplay_guard_retained=True,new_finalization_runs_before_original1300_stop=True,actual6502_whole_AudioUpdate_calls=4,actual_Audio_cycles=cycles,profile_Audio_cycles_exact=True,actual_source_returns=summary['source_returns'],actual_module_startup_callbacks=static,actual_function_spans=summary['spans'],runtime_registration_removal_and_emulated_observer_writes=0,tool_sha256=sha(__file__),scope='Full generated inactive mock chronology plus four actual6502 whole Audio calls into the read-only static profiler. No native Main/NMI deadline, PPU, DMA, controller workload, real timing attribution or optimization acceptance; actual interrupt accounting is separately mocked/tested before readiness.')
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
