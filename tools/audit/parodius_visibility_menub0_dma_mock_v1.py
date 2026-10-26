"""Execute both actual menu post-DMA guard closures under finite synthetic APIs."""
from pathlib import Path
import argparse,hashlib,json,sys
from final_roll_items_prepare import lua
R=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for n in ['preparation','lua-root','output']:p.add_argument('--'+n,type=Path,required=True)
 a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
 z=json.loads((a.preparation/'menu/preparation.json').read_text());script=Path(z['script']);s=script.read_text();c=json.loads(script.with_name('config.json').read_text());g=c['dma_protocol'];assert g['next_pc']==0xe005 and g['complete_pc']==0xe008 and len(g['next_bytes'])==8
 mock='''
callbacks={};slots={};rows={};state={['cpu.pc']=0xe005};image={};hardware={};for i=1,256 do image[i]=(i*31+7)%256;hardware[i]=image[i]end
memory={};emu={memType={nesDebug=1,nesSpriteRam=3},callbackType={write=1},getState=function()return state end,read=function(a)return memory[a]or 0 end,addMemoryCallback=function(fn,k,a)callbacks[#callbacks+1]=fn end}
local C=CONFIG;local D={Sprite_Data=512};local wall=500;local nmiDepth,lifeGeneration,lifeInitDMAs,lifeCarryDMAs=1,0,0,0;local ppuMask=6;local oamAddress=0;local physical=127;local lastPub={id=1,oam=image,generation=0,phase='init'};local lastDMA,dmaPending;local dmaid,completeMismatches=0,0;local completionHooks={}
local function active()return NOT_INIT end;local function lifeOwn()return true end;local function bytes(a,k)return k==3 and hardware or image end
local function equal(a,b)if#a~=#b then return false end;for i=1,#a do if a[i]~=b[i]then return false end end;return true end
local function bank()return physical end;local function stamp()return{frame=500,scanline=250,cycle=77}end;local function detail()return{}end
local function row(_,t)rows[#rows+1]=t end;local bus={};local function queueReturnSlot(pc,fn)slots[pc]=fn end
function SET_MASK(v)ppuMask=v end;function SET_BANK(v)physical=v end
function COUNT(v)dmaPending.data_writes=v end
function PENDING()return dmaPending~=nil end;function RESULT()return lastDMA and lastDMA.complete end
'''
 cases=[]
 for filename in ['parodius_visibility_postdma_static_observer_v1.lua','parodius_visibility_postdma_bridge_v1.lua']:
  whole=(R/'tools/audit'/filename).read_text();assert s.count(whole)==1
  end=whole.index('end,emu.callbackType.write,0x4014)')+len('end,emu.callbackType.write,0x4014)');start=whole.rfind('emu.addMemoryCallback(function(_,v)',0,end);block=whole[start:end];assert block.count('0x4014')==1
  def test(name,count=256,flip=None,badbyte=None,pc=0xe005,startmask=6,endmask=6,wrongbank=False,wanted=None):
   rt=LuaRuntime(unpack_returned_tuples=True);rt.execute('CONFIG='+lua(c)+'\nNOT_INIT='+('false'if'bridge'in filename else'true')+'\n'+mock+'\n'+block)
   for i,v in enumerate(g['next_bytes']):rt.globals().memory[g['next_pc']+i]=v
   rt.globals().state['cpu.pc']=pc
   if badbyte is not None:rt.globals().memory[g['next_pc']+badbyte]^=1
   rt.globals().SET_MASK(startmask);err=None
   try:
    rt.globals().callbacks[1](0x4014,2);assert rt.globals().PENDING();assert rt.globals().slots[0xe005] is None
    rt.globals().COUNT(count);rt.globals().SET_MASK(endmask)
    if flip is not None:rt.globals().hardware[flip+1]^=1
    if wrongbank:rt.globals().SET_BANK(125);rt.globals().slots[0xe008]();assert rt.globals().PENDING();rt.globals().SET_BANK(127)
    rt.globals().slots[0xe008]()
   except Exception as ex:err=str(ex)
   assert(err is None)==(wanted is None),(filename,name,err,wanted)
   if wanted:assert wanted in err,(filename,name,err,wanted)
   else:assert not rt.globals().PENDING()and rt.globals().RESULT()['exact_source']and rt.globals().RESULT()['completed_2004_writes']==256
   cases.append(dict(observer=filename,case=name,expected_rejection=wanted,error=err))
  test('correct256-hardware-pre-enable')
  test('wrong-bank-defers-then-completes',wrongbank=True)
  test('wrong-nextPC',pc=0xe006,wanted='DMA post-STA PC')
  for i in range(8):test('wrong-next-byte-'+str(i),badbyte=i,wanted='postDMA eight-byte sequence')
  test('start-rendering-enabled',startmask=30,wanted='Rendering disabled throughout actual DMA')
  test('finish-rendering-enabled',endmask=30,wanted='Completed hardware observed before rendering enable')
  for n in [0,255,257]:test('bad-count-'+str(n),count=n,wanted='Completed DMA256 writes')
  for n in [0,127,255]:test('bad-physical-byte-'+str(n),flip=n,wanted='Completed DMA hardware exact source image')
 (a.output/'cases.json').write_text(json.dumps(cases,indent=2)+'\n')
 proof=dict(passed=True,native_run=False,ROM_sha256=z['ROM_sha256'],script_sha256=sha(script),cases=len(cases),actual_both_generated_4014_guard_bodies_executed=True,E005_no_completion_and_E008_after_LDA_before_enable=True,full256_count_and_hardware_equality_retained=True,eight_actual_hook_bytes_and_PC_exact=True,rendering_disabled_at_start_and_completed_hardware=True,wrong_bank_deferral_exact=True,intentional_rejections=sum(q['expected_rejection']is not None for q in cases),cases_sha256=sha(a.output/'cases.json'),tool_sha256=sha(__file__),limits='Synthetic observation APIs only, including synthetic source/write-count/hardware values to test rejection. No native ROM/input/PPU modification or timing/graphics verdict; actual native required.')
 (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
