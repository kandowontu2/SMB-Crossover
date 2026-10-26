"""Execute unchanged complete256-byte DMA guards under old/static Lua dispatch."""
from pathlib import Path
import argparse,hashlib,json,sys
from cv3_remaining_sfx_static_build_v1 import CORE,transform
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
MOCK=r'''
callbacks={};state={['cpu.pc']=0xe361,['cpu.sp']=253,['cpu.cycleCount']=100,['ppu.frameCount']=2,['ppu.scanline']=241,['ppu.cycle']=12};memory={};hardware={};files={};wall=1;entered=true;done=false;strictDMA=0;strictDmaPending=nil;strictDmaHooks={};ppuMask=30
emu={memType={nesDebug=1,nesSpriteRam=2},callbackType={write=1,exec=2}}
emu.getState=function()return state end
emu.read=function(a,kind)if kind==2 then return hardware[a]or 0 end;return memory[a]or 0 end
emu.addMemoryCallback=function(fn,kind,lo,hi)callbacks[#callbacks+1]={fn=fn,kind=kind,lo=lo,hi=hi or lo}end
bank=function(a)return activeBank end;activeBank=127
bytes=function(a,kind)local q={};for i=0,255 do q[#q+1]=string.char(emu.read(a+i,kind))end;return table.concat(q)end
json=function(q)
 if type(q)=='table'then local out={};for k,v in pairs(q)do out[#out+1]=string.format('%q',tostring(k))..':'..json(v)end;return'{'..table.concat(out,',')..'}'
 elseif type(q)=='string'then return string.format('%q',q)else return tostring(q)end
end
dmaBus={write=function(self,v)files[#files+1]=v;return self end,flush=function()end}
for i=0,255 do memory[0x200+i]=(i*37+19)%256;hardware[i]=0 end
memory[0xe361]=0xa2;memory[0xe362]=1
function event(kind,a,v)
 local count=#callbacks
 for i=1,count do local c=callbacks[i];if c.kind==kind and a>=c.lo and a<=c.hi then c.fn(a,v)end end
end
function startdma(scanline,mask,opcode,operand)
 state['cpu.pc']=0xe361;state['ppu.scanline']=scanline;ppuMask=mask;memory[0xe361]=opcode;memory[0xe362]=operand;event(1,0x4014,2)
end
function finishdma(count,scanline,flip,physical)
 for i=0,count-1 do event(1,0x2004,(i*37+19)%256)end
 for i=0,255 do hardware[i]=memory[0x200+i]end
 if flip>=0 then hardware[flip]=(hardware[flip]+1)%256 end
 activeBank=physical;state['cpu.pc']=0xe363;state['ppu.scanline']=scanline;event(2,0xe363)
end
'''
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--original',type=Path,required=True);p.add_argument('--static',type=Path,required=True);p.add_argument('--lua-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
 old=a.original.read_text();new=a.static.read_text();assert transform(old)[0]==new
 def block(s):
  lo=s.index('local function stamp()');hi=s.index('local pendingReturns,installedReturns=',lo)if s==old else s.index("emu.addMemoryCallback(function()\n if not entered or done or not valid('AudioUpdate')",lo);return s[lo:hi]
 cases=[]
 configs=[dict(name='valid-'+str(i),start=scan,mask=mask,op=0xa2,arg=1,count=256,end=scan,flip=-1,bank=127,wanted=None)for i,(scan,mask)in enumerate([(241,30),(250,30),(260,30),(-1,0),(0,0),(240,0)])]
 configs +=[dict(name='bad-start-'+str(scan),start=scan,mask=30,op=0xa2,arg=1,count=256,end=241,flip=-1,bank=127,wanted='Actual DMA starts inside vblank or disabled rendering')for scan in[0,239,240,261]]
 configs +=[dict(name='bad-end-'+str(scan),start=241,mask=30,op=0xa2,arg=1,count=256,end=scan,flip=-1,bank=127,wanted='Actual DMA completes inside vblank or disabled rendering')for scan in[0,240,261]]
 configs +=[dict(name='bad-op-'+str(op),start=241,mask=30,op=op,arg=1,count=256,end=241,flip=-1,bank=127,wanted='Actual DMA next instruction LDX1')for op in[0,0xea]]
 configs +=[dict(name='bad-operand',start=241,mask=30,op=0xa2,arg=2,count=256,end=241,flip=-1,bank=127,wanted='Actual DMA next instruction LDX1')]
 configs +=[dict(name='bad-count-'+str(n),start=241,mask=30,op=0xa2,arg=1,count=n,end=241,flip=-1,bank=127,wanted='Actual completed DMA has256 data writes')for n in[0,255,257]]
 configs +=[dict(name='bad-image-'+str(n),start=241,mask=30,op=0xa2,arg=1,count=256,end=241,flip=n,bank=127,wanted='Actual completed DMA hardware equals complete source page')for n in[0,127,255]]
 for cfg in configs:
  results=[]
  for s,static in[(old,False),(new,True)]:
   rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(MOCK+(CORE if static else'')+block(s)+('\ninstallStaticReturns()'if static else''))
   if static:rt.execute("emu.addMemoryCallback=function()error('Runtime registration forbidden')end;emu.removeMemoryCallback=function()error('Runtime removal forbidden')end")
   error=None
   try:rt.globals().startdma(cfg['start'],cfg['mask'],cfg['op'],cfg['arg']);rt.globals().finishdma(cfg['count'],cfg['end'],cfg['flip'],cfg['bank'])
   except Exception as e:error=str(e)
   assert(error is None)==(cfg['wanted']is None),(cfg,error)
   if error:assert cfg['wanted']in error,(cfg,error)
   rows=[json.loads(rt.globals().files[i])for i in range(1,rt.eval('#files')+1)];results.append(dict(error=error,guard=cfg['wanted'],strictDMA=rt.eval('strictDMA'),rows=rows,pending=rt.eval('strictDmaPending~=nil')))
  assert {k:v for k,v in results[0].items()if k!='error'}=={k:v for k,v in results[1].items()if k!='error'},cfg
  cases.append(dict(config=cfg,old=results[0],static=results[1]))
 # A mismatched physical bank must defer completion without consuming pending;
 # returning in the bound physical bank later executes exactly once.
 bankrows=[]
 for s,static in[(old,False),(new,True)]:
  rt=LuaRuntime(unpack_returned_tuples=True);rt.execute(MOCK+(CORE if static else'')+block(s)+('\ninstallStaticReturns()'if static else''))
  if static:rt.execute("emu.addMemoryCallback=function()error('Runtime registration forbidden')end")
  rt.globals().startdma(241,30,0xa2,1);rt.globals().finishdma(256,241,-1,125);assert rt.eval('strictDmaPending~=nil and strictDMA==0');rt.execute('activeBank=127;event(2,0xe363)');assert rt.eval('strictDmaPending==nil and strictDMA==1');bankrows.append([json.loads(rt.globals().files[i])for i in range(1,rt.eval('#files')+1)])
 assert bankrows[0]==bankrows[1]
 (a.output/'cases.json').write_text(json.dumps(cases,indent=2)+'\n');result=dict(passed=True,native_executed=False,Lua_runtime='Lua5.4',complete_actual_DMA_guard_cases=len(cases),expected_guard_failures=sum(c['wanted']is not None for c in configs),wrong_physical_bank_defer_control=True,all_complete256_source_and_hardware_bytes_and_timing_guards_retained=True,all_semantic_output_rows_and_failure_reasons_exact=True,cases_sha256=sha(a.output/'cases.json'),original_script_sha256=sha(a.original),static_script_sha256=sha(a.static),tool_sha256=sha(__file__),scope='Actual unchanged generated strictDMA Lua callbacks executed with complete source/hardware images and deterministic synthetic bus events. Both old and new must reject all identical corrupt/late/incomplete controls. No native bus or real PPU claim.')
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
