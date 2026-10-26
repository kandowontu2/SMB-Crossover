"""Prepare static acquired-ability fixtures with genuine current731 DMA hooks.

No native execution switch. Old source, mechanics, receipts and guards stay intact.
"""
from pathlib import Path
import argparse,difflib,hashlib,json,shutil,subprocess,sys
from final_item_abilities_run import lua
from final_item_abilities_static_prepare_v2 import CURRENT,D,ROOT
from check_tmnt_render_oa import address,location
from link_pit_rygar_sophia_audit_cpu import scoped_load
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
OLD_DMA="""emu.addMemoryCallback(function(_,v)
 dma=nil;if entered and not done and published then local s=bytes(v*256,emu.memType.nesDebug);if s==published then dma=s end end
end,emu.callbackType.write,0x4014)
"""

def protocol(b):
 start=address(b,'PostDmaMaskEnable');pos=location(b,'PostDmaMaskEnable');raw=b['raw'][pos:pos+8]
 assert start==0xe005 and raw==bytes([0xad,address(b,'Mirror_PPUMASK')&255,address(b,'Mirror_PPUMASK')>>8,0x8d,1,0x20,0xa2,1])
 assert b['raw'][location(b,'OAMandReadJoypad'):location(b,'OAMandReadJoypad')+5]==bytes([0xa9,2,0x8d,0x14,0x40])
 return dict(window_start=start,window_bytes=list(raw),bank=(pos-16)//8192,complete_pc=start+3,obsolete_preDMA_exec_pc=start,scope_ram={n:address(b,n)for n in ['DisableScreenFlag','CrossoverMenuState','OperMode','OperMode_Task','GameEngineSubroutine']},observation='EXEC after real LDA atE008, before STA2001; E005 is NOT complete')

def dma_mocks(LuaRuntime,text,cfg):
 # Run the actual new observer with deterministic hardware/source APIs. The
 # synthetic transfer model is a rejection test, not a native timing claim.
 mock='''
 callbacks={};events={};mem={};hardware={};logs={};state={['cpu.sp']=240,['cpu.pc']=0,['cpu.cycleCount']=0,['ppu.frameCount']=184,['ppu.scanline']=-1,['ppu.cycle']=0,['ppu.spriteRamAddr']=0}
 emu={memType={nesDebug=1,nesSpriteRam=2},callbackType={exec=2,write=1},eventType={startFrame=3}}
 emu.getState=function()return state end
 emu.read=function(a,t)if t==2 then return hardware[a]or 0 else return mem[a]or 0 end end
 emu.addMemoryCallback=function(fn,k,lo,hi)callbacks[#callbacks+1]={fn=fn,k=k,lo=lo,hi=hi or lo}end
 emu.addEventCallback=function(fn,k)events[k]=fn end
 io.open=function()return{write=function(self,s)logs[#logs+1]=s;return self end,flush=function()end}end
 function fire(k,a,v)for _,q in ipairs(callbacks)do if q.k==k and a>=q.lo and a<=q.hi then q.fn(a,v)end end end
 local C=CFG;local OUTPUT='mock/';local entered,done=true,false;local published=nil;local dma=nil
 local function bytes(at,t)local z={};for i=0,255 do z[#z+1]=string.char(emu.read(at+i,t))end;return table.concat(z)end
 local function bank(a)return a>=0xe000 and CFG.dma_protocol.bank or 1 end
 local function json(v)return'RAW-BEFORE-ASSERT' end
 for i,v in ipairs(C.dma_protocol.window_bytes)do mem[C.dma_protocol.window_start+i-1]=v end
 for i=0,255 do mem[512+i]=(i*17+3)%256;hardware[i]=mem[512+i]end
 '''
 cases=[]
 def execute(name,body,passes):
  rt=LuaRuntime(unpack_returned_tuples=True);rt.execute('CFG='+lua(cfg)+'\n'+mock+text)
  rt.execute('initialCallbackCount=#callbacks;emu.addMemoryCallback=function()error("runtime registration")end')
  ok,error=rt.eval('function()local ok,e=pcall(function()'+body+' end);return ok,tostring(e)end')()
  assert bool(ok)==passes,(name,error)
  assert rt.eval('#callbacks==initialCallbackCount')
  if not passes:assert rt.eval('#logs')>0,(name,'raw diagnostics must precede rejection')
  cases.append(dict(name=name,passed=True,expected_native_guard_outcome='accept'if passes else'reject',rejection=None if passes else error))
 common="state['cpu.pc']=CFG.dma_protocol.window_start;fire(1,0x2001,0);fire(1,0x4014,2);"
 transfer="for i=0,255 do state['ppu.spriteRamAddr']=i;fire(1,0x2004,mem[512+i])end;state['ppu.spriteRamAddr']=0;"
 finish='fire(2,CFG.dma_protocol.complete_pc,0);'
 execute('complete256_exact',common+transfer+finish+'events[3]()',True)
 execute('E005_rejected_as_completion',common+'fire(2,CFG.dma_protocol.obsolete_preDMA_exec_pc,0);'+finish,False)
 execute('only255_writes',common+"for i=0,254 do state['ppu.spriteRamAddr']=i;fire(1,0x2004,mem[512+i])end;state['ppu.spriteRamAddr']=0;"+finish,False)
 execute('corrupted_physical_byte',common+transfer+'hardware[7]=255;'+finish,False)
 execute('wrong_destination_ordinal',common+transfer.replace("state['ppu.spriteRamAddr']=i;","state['ppu.spriteRamAddr']=(i==242 and 244 or i);" )+finish,False)
 execute('render_enabled_during_DMA','state["cpu.pc"]=CFG.dma_protocol.window_start;fire(1,0x2001,30);fire(1,0x4014,2);'+transfer+finish,False)
 execute('wrong_start_address',"state['ppu.spriteRamAddr']=8;"+common+transfer+finish,False)
 execute('wrong_source_write',common+transfer.replace('mem[512+i])','(i==7 and 255 or mem[512+i]))')+finish,False)
 execute('later_start_hardware_changed',common+transfer+finish+'hardware[7]=255;events[3]()',False)
 execute('pending_start_classified_not_complete',common+'events[3]();'+transfer+finish,True)
 scoped="mem[CFG.dma_protocol.scope_ram.DisableScreenFlag]=0;mem[CFG.dma_protocol.scope_ram.CrossoverMenuState]=2;mem[CFG.dma_protocol.scope_ram.OperMode]=0;state['ppu.scanline']=-1;"
 execute('safe_render_enable_dot274',scoped+"state['ppu.cycle']=274;fire(1,0x2001,30)",True)
 execute('late_render_enable_dot275',scoped+"state['ppu.cycle']=275;fire(1,0x2001,30)",False)
 execute('transient_render_during_one_data_write',common+transfer.replace("state['ppu.spriteRamAddr']=i;fire(1,0x2004,mem[512+i])","state['ppu.spriteRamAddr']=i;if i==128 then fire(1,0x2001,30)end;fire(1,0x2004,mem[512+i]);if i==128 then fire(1,0x2001,0)end ")+finish,False)
 return cases

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--lua-root',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 base=a.output/'static-return-control';r=subprocess.run([sys.executable,'-B',str(ROOT/'tools/audit/final_item_abilities_static_prepare_v2.py'),'--output',str(base),'--lua-root',str(a.lua_root)],capture_output=True,text=True);assert r.returncode==0,(r.stdout,r.stderr)
 rom=D/'mm-proto-clean-menu-candidates-v1/clean-menu-irq/candidate.nes';assert sha(rom)==CURRENT;b=scoped_load(rom);h=protocol(b)
 module=ROOT/'tools/audit/final_item_abilities_dma731_v1.lua';text=module.read_text()+'\n';sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
 cases=dma_mocks(LuaRuntime,text,dict(dma_protocol=h));profiles=[];bindings={}
 def bind(p):
  p=Path(p);bindings[str(p.resolve())]=dict(path=str(p.resolve()),sha256=sha(p),bytes=p.stat().st_size)
 for family in ['pit','rygar','scrooge']:
  for mode in ['easy','hard']:
   old=base/(family+'-'+mode);out=a.output/(family+'-'+mode);shutil.copytree(old,out)
   before=(old/'run.lua').read_text();assert before.count(OLD_DMA)==1;cfg=json.loads((out/'config.json').read_text());oldcfg=cfg.copy();cfg['dma_protocol']=h
   prefix='FINAL_ITEM_PROGRESSIVE='+lua(oldcfg)+'\n';newprefix='FINAL_ITEM_PROGRESSIVE='+lua(cfg)+'\n';assert before.startswith(prefix)
   after=before.replace(OLD_DMA,text);after=newprefix+after[len(prefix):]
   assert (prefix+after[len(newprefix):]).replace(text,OLD_DMA)==before
   (out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n');(out/'run.lua').write_text(after,encoding='utf-8')
   (out/'current-observer-only.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='source-qualified-static-return',tofile='current731-DMA-observer')),encoding='utf-8')
   from parodius_visibility_hud_static_startup_v1 import MOCK
   rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(MOCK+'\nL={};OUTPUT="mock/";emu.write=function()error("Unexpected fixture startup mutation")end');rt.execute(after)
   n=rt.eval('#callbacks');assert rt.eval('callbacks[#callbacks].kind==2 and callbacks[#callbacks].lo==0 and callbacks[#callbacks].hi==65535')
   z=json.loads((out/'static-preparation.json').read_text());z.update(status='current731_static_DMA_source_mock_prepared_not_native',script_sha256=sha(out/'run.lua'),dma_observer_sha256=sha(module),dma_protocol=h,reverse_normalization_to_static_return_exact=True,static_memory_callbacks=n)
   (out/'current-preparation.json').write_text(json.dumps(z,indent=2)+'\n')
   profiles.append(dict(family=family,mode=mode,numeric_mode=cfg['mode_value'],path=str(out),script_sha256=sha(out/'run.lua'),preparation_sha256=sha(out/'current-preparation.json'),static_callback_count=n,planned_abilities=len(cfg['abilities'])))
   for f in out.iterdir():
    if f.is_file():bind(f)
 for f in base.rglob('*'):
  if f.is_file():bind(f)
 for f in [Path(__file__),module,ROOT/'tools/audit/final_item_abilities_static_prepare_v2.py',ROOT/'tools/audit/final_item_abilities_static_return_v1.lua',ROOT/'tools/audit/final_item_abilities_run.py',ROOT/'tools/audit/final_item_matrix_progressive.lua',ROOT/'tools/audit/check_tmnt_render_oa.py',ROOT/'tools/audit/link_pit_rygar_sophia_audit_cpu.py',ROOT/'tools/audit/parodius_visibility_hud_static_startup_v1.py',ROOT/'tools/audit/presentation_timing_preflight_v1.lua',D/'root-presentation450-731-v1/native-receipt.json',D/'root-presentation450-731-v1/config.json',ROOT/'tools/run_mesen.py',ROOT/'tools/audit/run_mesen_isolated.py',Path(sys.modules['lupa'].__file__),Path(sys.modules[LuaRuntime.__module__].__file__)]:bind(f)
 controls=dict(passed=True,native_launches=0,ROM_sha256=CURRENT,Lua_runtime=rt.eval('_VERSION'),protocol=h,return_static_controls_sha256=sha(base/'controls.json'),DMA_model_cases=cases,profiles=profiles,original_mechanics_and_guards_reverse_normalized_exact=True,
  scope='Source/mock preparation only: actual source8-byte E005window, E008 afterLDA/beforeSTA completion, fullraw256 before strict checks, data write count/destination/source/render mask/start hardware, original endFrame publication check retained. All static callbacks installed before final dispatcher.',
  limits=['No actual current acquired ability, visibility, native timing, waveform or native acquisition claim. No native worker/grant.','Full generated Lua uses run_mesen wrapper L/OUTPUT/debug bindings; no source result is called a real PPU observation.','Pending startFrame is explicitly logged, not relabeled completed; completed transfer is checked at actual E008 and next uncontested startFrame. Real native callbacks/PPU timings still require reviewed execution.'])
 (a.output/'controls.json').write_text(json.dumps(controls,indent=2)+'\n');bind(a.output/'controls.json');(a.output/'manifest.json').write_text(json.dumps(dict(bindings=list(bindings.values())),indent=2)+'\n')
 proof=dict(passed=True,native_launches=0,ROM_sha256=CURRENT,controls_sha256=sha(a.output/'controls.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(bindings),profiles=6,planned_abilities=62,source_mock_only=True)
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))

if __name__=='__main__':main()
