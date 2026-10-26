"""Original/static actual Lua return/DMA ordering, mirror/SP guards and full transform."""
from pathlib import Path
import argparse,hashlib,json,random,sys
from cv3_remaining_sfx_static_build_v1 import CORE,transform
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
MOCK='''
state={['cpu.sp']=0};memory={};banks={};callbacks={};log={};strictDmaPending=nil;strictDmaHooks={}
emu={memType={nesDebug=1},callbackType={exec=2}}
emu.getState=function()return state end
emu.read=function(a)return memory[a]or 0 end
emu.addMemoryCallback=function(fn,kind,lo,hi)callbacks[#callbacks+1]={fn=fn,lo=lo,hi=hi or lo}end
bank=function(pc)return banks[pc]or 0 end
C={mirror=1,overlays={{4416,5505},{5568,5761},{6903,7050}}}
function setcaller(pc,sp,b)
 state['cpu.sp']=sp;local word=(pc-1)%65536
 memory[256+(sp+1)%256]=word%256;memory[256+(sp+2)%256]=word//256;banks[pc]=b
end
function runexec(pc,sp,b)
 state['cpu.sp']=sp;banks[pc]=b
 local count=#callbacks
 for i=1,count do local q=callbacks[i];if pc>=q.lo and pc<=q.hi then q.fn(pc)end end
end
function armreturn(key,pc,sp,b,label)
 setcaller(pc,sp,b);TEST_ONRETURN(key,function()log[#log+1]=label end)
end
function armdma(pc,b,label)
 strictDmaPending={label=label};local key=b..':'..pc
 if not strictDmaHooks[key]then strictDmaHooks[key]=true;TEST_REGISTER_DMA(pc,function()
  if not strictDmaPending or bank(pc)~=b then return end
  local q=strictDmaPending;strictDmaPending=nil;log[#log+1]=q.label
 end)end
end
function output()return table.concat(log,'|')end
'''
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--original',type=Path,required=True);p.add_argument('--static',type=Path,required=True);p.add_argument('--lua-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
 old=a.original.read_text();new=a.static.read_text();expected,edits,oldcore=transform(old);assert new==expected
 # Reverse every allowed change byte-for-byte: every source/state/DMA/PPU/
 # return/SMC/stack/bank/controller/APU/cadence guard is otherwise identical.
 suffix='\n-- Final startup registration follows every original observer/controller hook.\ninstallStaticReturns()\n';assert new.endswith(suffix);reverse=new[:-len(suffix)]
 reverse=reverse.replace(CORE+'\n','',1).replace('  queueReturnSlot(finish,function()','  emu.addMemoryCallback(function()',1).replace('  end)\n end\nend,emu.callbackType.write,0x4014)','  end,emu.callbackType.exec,finish)\n end\nend,emu.callbackType.write,0x4014)',1)
 marker="emu.addMemoryCallback(function()\n if not entered or done or not valid('AudioUpdate')";reverse=reverse.replace(marker,oldcore+marker,1);assert reverse==old
 begin=old.index('local function alias(');end=old.index('local function valid(',begin);alias=old[begin:end];runtimes=[]
 for core,static in[(oldcore,False),(CORE,True)]:
  rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(MOCK+alias+core+'\nTEST_ONRETURN=onReturn\n'+('TEST_REGISTER_DMA=queueReturnSlot;installStaticReturns()'if static else'TEST_REGISTER_DMA=function(pc,fn)emu.addMemoryCallback(fn,emu.callbackType.exec,pc)end'))
  if static:rt.execute("emu.addMemoryCallback=function()error('Runtime callback registration forbidden')end;emu.removeMemoryCallback=function()error('Runtime removal forbidden')end")
  runtimes.append(rt)
 operations=[]
 def both(fn,*args):
  for rt in runtimes:rt.globals()[fn](*args)
  assert runtimes[0].globals().output()==runtimes[1].globals().output(),(fn,args);operations.append([fn,*args])
 # Replace a pending same-name return, retain independent same-PC slots in
 # registration order, persistent DMA/bank checks, nested stack depths/wrap.
 for pc,sp,b in[(pc,sp,b)for pc in[0,1,0xa777,0xc123,0xe007,0xffff]for sp in[0,1,127,253,254,255]for b in[28,82,125,127]]:
  both('armreturn','same',pc,sp,b,'replaced');both('armreturn','second',pc,sp,b,'second');both('armdma',pc,b,'dma');both('armreturn','same',pc,sp,b,'replacement')
  both('runexec',pc,(sp+1)&255,b);both('runexec',pc,(sp+2)&255,(b+1)&127);both('runexec',pc,(sp+2)&255,b);both('runexec',pc,(sp+2)&255,b)
  both('armdma',pc,b,'dma-rearm');both('runexec',pc,(sp+2)&255,b)
 # Every overlay border and every genuine E125/127 alias is checked. Same
 # physical code is allowed outside DPCM overlays only, exactly as before.
 for pc in[0xdfff,0xe000,0xe007,0xe000+4415,0xe000+4416,0xe000+5504,0xe000+5505,0xe000+5568,0xe000+5761,0xe000+6903,0xe000+7050,0xffff]:
  for before,after in[(125,127),(127,125),(28,127)]:
   both('armreturn','mirror',pc,253,before,'mirror'+str(pc));both('runexec',pc,255,after);both('runexec',pc,255,before)
 rng=random.Random(0x0c45ce16)
 for i in range(5000):
  pc=rng.choice([0xe007,0xc123,0xa777,0xffff,0]);sp=rng.choice([0,124,128,190,240,253,254,255]);b=rng.choice([0,28,82,84,125,127]);key='perf:'+str(i)if i%3==0 else'owner:'+str(i%7)
  both('armreturn',key,pc,sp,b,'r'+str(i))
  if i%11==0:both('armdma',pc,b,'d'+str(i))
  if i%5==0:both('armreturn',key,pc,sp,b,'replace'+str(i))
  both('runexec',pc,(sp+2)&255,b)
  if i%13==0:both('runexec',pc,sp,(b+1)&127)
 assert runtimes[1].eval('#callbacks')==1
 (a.output/'operations.json').write_text(json.dumps(operations,separators=(',',':'))+'\n')
 result=dict(passed=True,native_executed=False,game_ROM_modified=False,Lua_runtime=runtimes[1].eval('_VERSION'),runtime_module='lupa.lua54',comparisons=len(operations),operations_sha256=sha(a.output/'operations.json'),logged_events=runtimes[1].eval('#log'),old_callback_count=runtimes[0].eval('#callbacks'),new_callback_count=1,all_output_streams_equal_after_every_operation=True,raw_return_and_physicalbank_SP_alias_guards_unchanged=True,full_script_reverse_transform_exact=True,original_script_sha256=sha(a.original),static_script_sha256=sha(a.static),core_sha256=sha(Path(__file__).with_name('cv3_remaining_sfx_static_core_v1.lua')),tool_sha256=sha(__file__),scope='Actual Lua execution with deterministic synthetic callback/stack/physical-bank/DMA ordering. Complete-script reverse transformation binds every original guard/output/controller byte. No Mesen, actual DMA/PPU, performance or native observation-equivalence verdict.')
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
