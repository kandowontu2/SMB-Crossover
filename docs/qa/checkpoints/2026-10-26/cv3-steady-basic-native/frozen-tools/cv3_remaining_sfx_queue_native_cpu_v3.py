"""v3 source-only real BASIC owners for seven effects and two modes; v1/v2 unchanged."""
from pathlib import Path
import argparse,csv,hashlib,io,json,sys
from check_tmnt_render_oa import load,address,location,Memory
from cv3_remaining_sfx_queue256_support_v1 import init
from cv3_primary_sfx_source_v1 import Original,CV3
from verify_native_relocation import NesMPU
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--fixture',type=Path,required=True);p.add_argument('--lua-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);cfg=json.loads((a.fixture/'configuration.json').read_text());prep=json.loads((a.fixture/'preparation.json').read_text());assert sha(prep['script'])==prep['script_sha256'];b=load(Path(prep['ROM']));sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
 script=Path(prep['script']).read_text();lo=script.index('local function json(');hi=script.index('local function native()',lo);functions=script[lo:hi];core=(ROOT/'tools/audit/cv3_remaining_sfx_static_core_v1.lua').read_text();module=(ROOT/'tools/audit/cv3_remaining_sfx_queue_native_v2.lua').read_text();results=[]
 for interference,dummy in[('none',False),('slot',True),('head',True)]:
  q=init(b,cfg['variant']);q.put(CrossoverBehaviorVersion=cfg['mode'],PlayerFacingDir=1,Cv3AttackAge=14,Cv3AttackKind=2,Cv3Fresh=0,SavedJoypadBits=0,NmiDisable=255,NmiSkipped=0,DisableScreenFlag=0,Sprite0HitDetectFlag=1,Mirror_PPUMASK=30,Mirror_PPUCTRL=128);q.set('Cv3Subweapon',cfg['cases'][0]['sub'],cfg['variant']-1);q.set('Cv3Hearts',64,cfg['variant']-1)
  if cfg['expected_cue']==6:q.put(Cv3AttackAge=8,Cv3AttackKind=1)
  if cfg['expected_cue']==7:q.put(Cv3AttackAge=0,Cv3AttackKind=0,Cv3Fresh=128,SavedJoypadBits=4)
  rt=LuaRuntime(unpack_returned_tuples=True);callbacks=[];hardware=[];live={'c':None,'enabled':False}
  def dispatch(kind,at,v=None):
   for f,k,low,high in list(callbacks):
    if k==kind and low<=at<=high:f(at,v)if v is not None else f(at)
  class Watched(Memory):
   def __setitem__(self,at,v):
    if live['enabled']and isinstance(at,int):
     if 0x4000<=at<=0x4017:hardware.append(dict(audioEpoch=int(rt.globals().TEST_EPOCH()),register=at,value=v))
     if dummy and at==address(b,'Cv3FxQueueHead'):dispatch(1,at,list.__getitem__(self,at))
     dispatch(1,at,v)
    super().__setitem__(at,v)
  mem=Watched(b);list.__setitem__(mem,slice(None),list(q.m));mem.banks=list(q.m.banks);q.m=mem
  def state():
   c=live['c'];return rt.table_from({'cpu.pc':c.pc if c else 0,'cpu.sp':c.sp if c else 253,'cpu.a':c.a if c else 0,'cpu.x':c.x if c else 0,'cpu.y':c.y if c else 0,'cpu.cycleCount':c.processorCycles if c else 0})
  emu=rt.table_from({'memType':rt.table_from({'nesDebug':1}),'callbackType':rt.table_from({'write':1,'exec':2})});emu['getState']=state;emu['read']=lambda at,kind:q.m[int(at)];emu['convertAddress']=lambda at:rt.table_from({'address':q.m.banks[(int(at)-0x8000)//8192]*8192+(int(at)&8191)if int(at)>=0x8000 else int(at)})
  emu['addMemoryCallback']=lambda f,k,low,high=None:callbacks.append((f,k,int(low),int(high if high is not None else low)));rt.globals().emu=emu
  prefix=script.split('\n',1)[0]+'''\nlocal C=CV3_REMAINING_NATIVE_CONFIG;L=C.ram;OUTPUT='';local wall,age,audioEpoch=1,0,0;local entered,done=true,false;local savedNmi=nil
local current={q=C.cases[1],spawnCalls=0,spawnTypes={},batEntries=0,requests=0,requestTrace={},cueSerial=0};local r=function(n,i)return emu.read(assert(L[n])+(i or 0),emu.memType.nesDebug)end
outputs={};io.open=function(name,mode)outputs[name]={};return{write=function(self,...)for i=1,select('#',...)do outputs[name][#outputs[name]+1]=tostring(select(i,...))end;return self end,flush=function()end,close=function()end}end
local requests=assert(io.open('requests.csv','w'));local function voice(n)return r(n)end
'''
  suffix='''\ninstallStaticReturns();TEST_START=queueStartCase;TEST_FINISH=queueFinishCase
TEST_BEFORE=function(pc)if pc==C.hooks.NonMaskableInterrupt.address then savedNmi={}end;if pc==C.hooks.AudioUpdate.address then audioEpoch=audioEpoch+1 end end
TEST_EPOCH=function()return audioEpoch end;TEST_NMI_END=function()savedNmi=nil end;TEST_CURRENT=function()return current end;TEST_TEXT=function(n)return table.concat(outputs[n]or{})end
'''
  rt.execute(prefix+functions+core+module+'''
local h=C.hooks.Cv3BatUpdate;emu.addMemoryCallback(function()if not valid('Cv3BatUpdate')then return end;local before=r('Cv3Bat');onReturn('old-bat-entry',function()if before==0 and r('Cv3Bat')==1 then current.batEntries=(current.batEntries or 0)+1 end end)end,emu.callbackType.exec,h.address)
'''+suffix);rt.globals().emu['addMemoryCallback']=lambda *args:(_ for _ in()).throw(AssertionError('Runtime callback registration forbidden'));rt.globals().TEST_START();live['enabled']=True
  def step(c):
   live['c']=c;rt.globals().TEST_BEFORE(c.pc);dispatch(2,c.pc);c.step()
  def nmi(c):
   live['c']=c;resume,sp=c.pc,c.sp;c.nmi()
   for _ in range(60000):
    if c.pc==resume and c.sp==sp:rt.globals().TEST_NMI_END();return
    step(c)
   raise AssertionError('actual NMI timeout')
  proc='Cv3BatUpdate'if cfg['expected_cue']==7 else'Cv3WeaponsGate';bank=(location(b,proc)-16)//8192;q.m.page(1,bank);q.put(CurrentBank=bank|128);c=NesMPU(memory=q.m,pc=address(b,proc));c.sp=253;c.stPushWord(0x5aff);interrupted=False
  for _ in range(15000):
   if c.pc==0x5b00:break
   at=len(q.m.writes);step(c)
   if not interrupted and interference!='none':
    wanted=address(b,'Cv3FxQueue')if interference=='slot'else address(b,'Cv3FxQueueHead')
    if any(x==wanted for x,v in q.m.writes[at:]):nmi(c);interrupted=True
  else:raise AssertionError('actual cast timeout')
  live['c']=c;rt.globals().TEST_BEFORE(c.pc);dispatch(2,c.pc)
  for _ in range(100):nmi(c)
  rt.globals().TEST_FINISH();out=a.output/interference;out.mkdir()
  logs={}
  for name in['queue-owners.jsonl','source-register-image.csv','requests.csv']:
   text=rt.globals().TEST_TEXT(name);(out/name).write_text(text);logs[name]=sha(out/name)
  with(out/'assembled-apu.csv').open('w',newline='')as h:
   w=csv.DictWriter(h,fieldnames=['audioEpoch','register','value']);w.writeheader();w.writerows(hardware)
  logs['assembled-apu.csv']=sha(out/'assembled-apu.csv')
  events=[json.loads(t)for t in(out/'queue-owners.jsonl').read_text().splitlines()];images=list(csv.DictReader((out/'source-register-image.csv').open()));source=Original(CV3.read_bytes());source.call(0xe227);first=min(r['audioEpoch']for r in events if r['kind']=='drain-return'and cfg['expected_cue']in r['cues']);last=max(int(r['audioEpoch'])for r in images);raw_frames=0
  for epoch in range(first,last+2):
   for e in events:
    if e['kind']=='drain-return'and e['audioEpoch']==epoch:
     for cue in e['cues']:
      if cue==cfg['expected_cue']:source.call(0xe25f,a=cfg['cases'][0]['event'])
   wanted=(source.m[0x10a],source.m[0x10d]);source.m.trace=[];source.call(0xe24e);expected=[(r['address'],r['value'])for r in source.m.trace if(wanted[0]and r['address']in[0x4000,0x4001,0x4002,0x4003])or(wanted[1]and r['address']in[0x400c,0x400e,0x400f])];actual=[(int(r['address']),int(r['value']))for r in images if int(r['audioEpoch'])==epoch];assert actual==expected,(interference,epoch,actual,expected);raw_frames+=1
  current=rt.globals().TEST_CURRENT();results.append(dict(interference=interference,synthetic_RMW_dummy_writes=dummy,actual_native_casts=current['spawnCalls'],actual_bat_entries=current['batEntries'],actual_bat_gates=current['batGateCalls'],actual_published=current['queuePublished'],actual_consumed=current['queueConsumed'],actual_full_lag_NMIs=100+int(interrupted),ordered_original_source_frames=raw_frames,source_image_writes=current['sourceImageWrites'],callbacks=len(callbacks),logs=logs))
 result=dict(passed=True,native_executed=False,ROM_sha256=prep['ROM_sha256'],actual_numeric_mode=cfg['mode'],event=cfg['cases'][0]['event'],script_sha256=prep['script_sha256'],cases=results,actual_assembled_ability_entry=proc,actual_full_NMI_ISR=True,actual_genuine_caller_stack_writer_opcodes_banks_and_raw_source_image_hooks=True,all_raw_source_register_stores_including400F_order_equal_original=True,no_game_source_modifications=True,Lua_runtime='Lua5.4',tool_sha256=sha(__file__),scope='Actual6502 main cast and complete lagNMI replay into the read-only new Lua module, with source writes compared to original executable on actual consumer epochs. Synthetic PPU/bus-free CPU layer and an optional simulated INC dummy event; no Mesen, controller140-update fixture execution, OAM/CHR/DMC bus or native deadline verdict.')
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
