"""Exercise the exact additive59 timing module under finite synthetic APIs."""
from pathlib import Path
import argparse,hashlib,json,sys
from final_roll_items_prepare import lua
R=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['preparation','lua-root','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
 prep=json.loads((a.preparation/'menu/preparation.json').read_text());script=Path(prep['script']);c=json.loads(script.with_name('config.json').read_text())
 module=(R/'tools/audit/parodius_visibility_menu59_timing_v2.lua').read_text();assert script.read_text().count(module)==1
 preflight=(R/'tools/audit/presentation_timing_preflight_v1.lua').read_text();assert 'return line>=241 and line<=260 or line==-1 and dot<=274' in preflight and 'return line>=241 and line<=260 or line==-1 and dot<=274' in module
 mock='''
memory={};hardware={};callbacks={};events={};logs={};physical=127
state={['cpu.pc']=0xe005,['cpu.sp']=253,['cpu.cycleCount']=100,['ppu.frameCount']=500,['ppu.scanline']=250,['ppu.cycle']=0,['ppu.mask.backgroundEnabled']=true,['ppu.tmpVideoRamAddr']=0,['ppu.videoRamAddr']=0,['ppu.xScroll']=0,['ppu.writeToggle']=false}
for i=0,11 do state['mapper.chrBanks'..i]=i end
emu={memType={nesDebug=1,nesPpuDebug=2,nesSpriteRam=3},callbackType={write=1,exec=2},eventType={startFrame=0,endFrame=1}}
emu.read=function(a,k)if k==3 then return hardware[a]or 0 end;return memory[a]or 0 end
emu.getState=function()return state end;emu.convertAddress=function(a)return{address=physical*8192+(a%8192)}end
emu.addMemoryCallback=function(fn,k,lo)callbacks[#callbacks+1]={fn=fn,kind=k,address=lo}end
emu.addEventCallback=function(fn,k)events[k]=fn end
io.open=function(path,mode)logs[path]=logs[path]or'';return{write=function(self,x)logs[path]=logs[path]..x;return self end,flush=function()end,close=function()end}end
function WRITE(at,v)for _,q in ipairs(callbacks)do if q.kind==1 and q.address==at then q.fn(at,v)end end end
function EXEC(pc)state['cpu.pc']=pc;for _,q in ipairs(callbacks)do if q.kind==2 and q.address==pc then q.fn()end end end
'''
 # Expose only lexical counters for separate finalizer-threshold mocks. This
 # addition is NOT written into the prepared native fixture.
 body=module.rsplit('end',1)[0]+"function OBS_TEST_COUNTS(d,c,e,m,l,b)dmas=d;completed=c;enables=e;menuFrames=m;late=l;hardwareBad=b end\nend\n"
 def runtime():
  rt=LuaRuntime(unpack_returned_tuples=True);rt.execute('PARODIUS_VISIBILITY='+lua(c)+'\n'+mock+'\n'+body)
  for h in c['early_timing']['hooks'].values():
   for i,v in enumerate(h['bytes']):rt.globals().memory[h['pc']+i]=v
  for i in range(256):rt.globals().memory[512+i]=(i*31+7)%256;rt.globals().hardware[i]=(i*31+7)%256
  for n,v in dict(DisableScreenFlag=0,CrossoverMenuState=2,OperMode=0,OperMode_Task=3,GameEngineSubroutine=0).items():rt.globals().memory[c['early_timing']['ram'][n]]=v
  rt.execute("emu.addMemoryCallback=function()error('runtime registration forbidden')end;emu.removeMemoryCallback=function()error('runtime removal forbidden')end")
  return rt
 cases=[]
 def test(name,fn,wanted=None):
  rt=runtime();error=None
  try:fn(rt)
  except Exception as ex:error=str(ex)
  assert(error is None)==(wanted is None),(name,error,wanted)
  if wanted:assert wanted in error,(name,error,wanted)
  cases.append(dict(case=name,expected_rejection=wanted,error=error))
 def start(rt):rt.globals().WRITE(0x2001,6);rt.globals().WRITE(0x4014,2)
 def finish(rt,n=256,flip=None,endmask=6):
  for i in range(n):rt.globals().WRITE(0x2004,i%256)
  if flip is not None:rt.globals().hardware[flip]^=1
  rt.globals().WRITE(0x2001,endmask);rt.globals().EXEC(0xe008)
 test('correct actual256/E008 source hardware',lambda rt:(start(rt),finish(rt)))
 test('wrong postSTA PC',lambda rt:(rt.globals().state.__setitem__('cpu.pc',0xe006),start(rt)),'Early real page2 DMA instruction')
 test('wrong bank',lambda rt:(rt.globals().__setitem__('physical',125),start(rt)),'Early real DMA physical bank')
 for i in range(8):
  test('wrong protocol byte'+str(i),lambda rt,i=i:(rt.globals().memory.__setitem__(0xe005+i,rt.globals().memory[0xe005+i]^1),start(rt)),'Early actual post-DMA sequence')
 for n in [0,255,257]:test('count'+str(n),lambda rt,n=n:(start(rt),finish(rt,n)),'Early actual 256 writes completed before enable')
 for i in [0,127,255]:test('hardware byte'+str(i),lambda rt,i=i:(start(rt),finish(rt,flip=i)),'Early complete physical256 exact immutable source')
 test('no associated DMA',lambda rt:rt.globals().WRITE(0x2004,3),'Early every OAM write belongs')
 test('duplicate pending DMA',lambda rt:(start(rt),rt.globals().WRITE(0x4014,2)),'Early no pending actual DMA')
 test('rendering before DMA',lambda rt:(rt.globals().WRITE(0x2001,30),rt.globals().WRITE(0x4014,2)),'Early rendering disabled before every DMA')
 test('rendering during data',lambda rt:(start(rt),rt.globals().WRITE(0x2001,30),rt.globals().WRITE(0x2004,3)),'Early disabled rendering at every actual DMA data write')
 def enable(rt,line,dot,disabled=0,menu=2,oper=0,engine=0):
  rt.globals().state['ppu.scanline']=line;rt.globals().state['ppu.cycle']=dot
  for n,v in dict(DisableScreenFlag=disabled,CrossoverMenuState=menu,OperMode=oper,GameEngineSubroutine=engine).items():rt.globals().memory[c['early_timing']['ram'][n]]=v
  rt.globals().WRITE(0x2001,6);rt.globals().WRITE(0x2001,30)
 for line,dot,ok in [(241,0,True),(260,340,True),(-1,274,True),(-1,275,False),(0,0,False),(261,0,False)]:test('deadline'+str((line,dot)),lambda rt,l=line,d=dot:enable(rt,l,d),None if ok else'Scoped render enable before pre-render vertical reload')
 test('disabled owner is unscoped',lambda rt:enable(rt,0,0,disabled=1))
 test('gameplay engine8 is scoped',lambda rt:enable(rt,0,0,menu=0,oper=1,engine=8),'Scoped render enable before pre-render vertical reload')
 test('gameplay initialization is unscoped',lambda rt:enable(rt,0,0,menu=0,oper=1,engine=7))
 def snapshot(rt):
  rt.globals().events[0]();log=rt.globals().logs[c['output']+'menu-early-timing.jsonl'];q=json.loads(log)
  assert q['kind']=='early-menu-start-owner'and len(q['nametables'])==4096 and len(q['hardware_OAM'])==256 and len(q['palette'])==32 and len(q['actual_chr'])==12 and q['fineX']==0 and q['w']is False
 test('full actual-owner snapshot shape',snapshot)
 def finalize(rt,counts=(501,501,101,101,0,0),frame=1800):
  rt.globals().state['ppu.frameCount']=frame;rt.globals().OBS_TEST_COUNTS(*counts);rt.globals().events[1]()
 test('sufficient mocked counters finalize',lambda rt:finalize(rt))
 test('insufficient counters reject',lambda rt:finalize(rt,(0,0,0,0,0,0)),'Meaningful all-identity early timing scope')
 test('late counter rejects',lambda rt:finalize(rt,(501,501,101,101,1,0)),'Meaningful all-identity early timing scope')
 test('nonterminal finalizer no output',lambda rt:finalize(rt,frame=1799))
 (a.output/'cases.json').write_text(json.dumps(cases,indent=2)+'\n',encoding='utf-8')
 q=dict(passed=True,native_run=False,ROM_sha256=c['ROM_sha256'],script_sha256=sha(script),cases=len(cases),intentional_rejections=sum(z['expected_rejection']is not None for z in cases),actual_additive_module_body_executed=True,ROOT_preflight_deadline_predicate_exact=True,full256_E008_bank_PC_bytes_count_hardware_rejections=True,menu_NT_CHR_palette_OAM_and_scroll_snapshot_shapes_checked=True,runtime_registration_attempts=0,cases_sha256=sha(a.output/'cases.json'),tool_sha256=sha(__file__),limits='Synthetic source/API and separately exposed lexical-counter finalizer tests only. Counter setup absent from native. No actual hardware, pixels, timing or native verdict; wholeBG review remains post-run and separate.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8');print(json.dumps(q,indent=2))
if __name__=='__main__':main()
