"""Execute original/new Lua return and DMA dispatch semantics without emulation."""
from pathlib import Path
import argparse,hashlib,json,random,sys
from parodius_visibility_hud_static_build_v1 import CORE,transform
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ROOT=Path(__file__).resolve().parents[2]

MOCK='''
state={['cpu.sp']=0};memory={};banks={};callbacks={};log={};dmaPending=nil;completionHooks={}
emu={memType={nesDebug=1},callbackType={exec=2}}
emu.getState=function()return state end
emu.read=function(a)return memory[a]or 0 end
emu.addMemoryCallback=function(fn,kind,lo,hi)callbacks[#callbacks+1]={fn=fn,lo=lo,hi=hi or lo}end
bank=function(pc)return banks[pc]or 0 end
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
 dmaPending={label=label};local key=tostring(b)..':'..pc
 if not completionHooks[key]then completionHooks[key]=true;TEST_REGISTER_DMA(pc,function()
  if not dmaPending or bank(pc)~=b then return end
  local q=dmaPending;dmaPending=nil;log[#log+1]=q.label
 end)end
end
function output()return table.concat(log,'|')end
'''


def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--lua-root',type=Path,required=True);p.add_argument('--parser-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 sys.path.insert(0,str(a.lua_root));from lupa import LuaRuntime
 sys.path.insert(0,str(a.parser_root));from luaparser import ast
 oldpath=ROOT/'tools/audit/parodius_visibility_observer.lua';newpath=ROOT/'tools/audit/parodius_visibility_hud_static_observer_v1.lua';old=oldpath.read_text(encoding='utf-8');new=newpath.read_text(encoding='utf-8');expected,edits=transform(old);assert new==expected;ast.parse(new)
 first=old.index('local pending,installed={},{}');last=old.index('\nfor _,name in ipairs(C.profile_hooks or{})do',first);oldcore=old[first:last]
 runtimes=[]
 for core,static in [(oldcore,False),(CORE,True)]:
  rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(MOCK+core+'\nTEST_ONRETURN=onReturn\n'+('TEST_REGISTER_DMA=queueReturnSlot;PARODIUS_STATIC_INSTALL_RETURNS()'if static else'TEST_REGISTER_DMA=function(pc,fn)emu.addMemoryCallback(fn,emu.callbackType.exec,pc)end'))
  if static:rt.execute("emu.addMemoryCallback=function()error('Runtime native registration forbidden')end")
  runtimes.append(rt)
 rng=random.Random(0x12f820);operations=[];comparisons=0
 def both(fn,*args):
  nonlocal comparisons
  for rt in runtimes:rt.globals()[fn](*args)
  assert runtimes[0].globals().output()==runtimes[1].globals().output(),(fn,args)
  comparisons+=1;operations.append([fn,*args])
 # Explicit pending replacement, shared-PC registration order, stack/bank misses,
 # nested depth, 16-bit return wrap, and persistent DMA interleaving.
 for pc in [0,1,0x4000,0xc000,0xffff]:
  for sp in [0,1,127,253,254,255]:
   both('armreturn','reused',pc,sp,116,'old-replaced')
   both('armreturn','unique',pc,sp,116,'first-unique')
   both('armdma',pc,116,'dma')
   both('armreturn','reused',pc,sp,116,'replacement')
   both('runexec',pc,(sp+1)%256,116)
   both('runexec',pc,(sp+2)%256,77)
   both('runexec',pc,(sp+2)%256,116)
   both('runexec',pc,(sp+2)%256,116)
   both('armdma',pc,116,'dma-rearmed')
   both('runexec',pc,(sp+2)%256,116)
 for i in range(12000):
  pc=rng.choice([0xe007,0xc123,0xa777,0xffff,0]);sp=rng.choice([0,124,128,190,240,253,254,255]);b=rng.choice([0,59,77,116,127]);key='profile-'+str(i)if i%3==0 else'draw-owner-'+str(i%7)
  both('armreturn',key,pc,sp,b,'return-'+str(i))
  if i%11==0:both('armdma',pc,b,'dma-'+str(i))
  if i%5==0:both('armreturn',key,pc,sp,b,'overwrite-'+str(i))
  both('runexec',pc,(sp+2)%256,b)
  if i%13==0:both('runexec',pc,sp,(b+1)%128)
 # Dispatch must follow every fixed callback even if that callback arms a return.
 # The final global dispatcher is registered after the full generated harness.
 assert runtimes[1].eval('#callbacks')==1
 # All unchanged observer bytes/guards are covered by exact reverse transform;
 # only five documented registration transformations are permitted.
 (a.output/'operations.json').write_text(json.dumps(operations,separators=(',',':'))+'\n',encoding='utf-8')
 q=dict(passed=True,native_run=False,ROM_modified=False,Lua_runtime=runtimes[1].eval('_VERSION'),comparisons=comparisons,operations_sha256=sha(a.output/'operations.json'),logged_events=runtimes[1].eval('#log'),new_native_callback_count=runtimes[1].eval('#callbacks'),old_native_callback_count=runtimes[0].eval('#callbacks'),old_observer_sha256=sha(oldpath),new_observer_sha256=sha(newpath),tool_sha256=sha(Path(__file__)),exact_documented_transform=True,source_transforms=len(edits),constraints=['Original pending key and replacement semantics','First registration order retained per PC across return and persistent DMA slots','Stack/bank guards retained','16-bit return address and stack wrap retained','No runtime native addMemoryCallback allowed in new Lua test','Identical output trace after every operation'],limits='Actual Lua unit observation-layer checks, not Mesen/game/native qualification. Raster registration is moved to startup but activation remains the exact original endFrame predicate; native prefix/PPU equivalence still required.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(q))

if __name__=='__main__':main()
