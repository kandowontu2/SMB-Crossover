"""Exercise the relocated actual DMA-completion guard, including corruptions."""
from pathlib import Path
import argparse, hashlib, json, sys
from cv3_remaining_sfx_static_dma_v1 import MOCK, CORE
from observe_chip_committed_write import lua

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fixture',type=Path,required=True)
    p.add_argument('--lua-root',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args(); a.output.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(a.lua_root));from lupa.lua54 import LuaRuntime
    source=(a.fixture/'run.lua').read_text(encoding='utf-8')
    config=json.loads((a.fixture/'configuration.json').read_text(encoding='utf-8'))
    guard=config['dma_completion_guard'];assert guard==dict(pc=0xe005,bank=127,bytes=[173,122,7,141,1,32,162,1])
    lo=source.index('local function stamp()')
    hi=source.index("emu.addMemoryCallback(function()\n if not entered or done or not valid('AudioUpdate')",lo)
    block=source[lo:hi]
    mock=MOCK.replace('0xe361','0xe005').replace('0xe362','0xe006').replace('0xe363','0xe005')
    cases=[]
    def test(name,scan=250,mask=6,end=250,count=256,flip=-1,badbyte=None,badpc=False,badbank=False,defer=False,wanted=None):
        rt=LuaRuntime(unpack_returned_tuples=True)
        rt.execute(mock+CORE+'\nC='+lua({'dma_completion_guard':guard})+'\n'+block+'\ninstallStaticReturns()')
        for i,v in enumerate(guard['bytes']):rt.globals().memory[0xe005+i]=v
        expected=guard['bytes'][:]
        if badbyte is not None:
            expected[badbyte]^=1;rt.globals().memory[0xe005+badbyte]=expected[badbyte]
        if badpc:rt.execute('C.dma_completion_guard.pc=0xe006')
        if badbank:rt.execute('activeBank=125')
        rt.execute("emu.addMemoryCallback=function()error('Runtime registration forbidden')end")
        error=None
        try:
            rt.globals().startdma(scan,mask,expected[0],expected[1])
            rt.globals().finishdma(count,end,flip,125 if defer else 127)
            if defer:
                assert rt.eval('strictDmaPending~=nil and strictDMA==0')
                rt.execute('activeBank=127;event(2,0xe005)')
        except Exception as ex:error=str(ex)
        assert (error is None)==(wanted is None),(name,error,wanted)
        if wanted:assert wanted in error,(name,error,wanted)
        else:assert rt.eval('strictDMA')==1 and not rt.eval('strictDmaPending~=nil'),name
        cases.append(dict(name=name,expected_failure=wanted,error=error,strictDMA=rt.eval('strictDMA')))
    for scan,mask in [(241,30),(250,30),(260,30),(-1,0),(-1,6),(0,0),(240,6)]:
        test('valid-'+str(scan)+'-'+str(mask),scan=scan,mask=mask,end=scan)
    for i in range(8):test('wrong-byte-'+str(i),badbyte=i,wanted='Actual postDMA mask pair and LDX1 bytes')
    test('wrong-PC',badpc=True,wanted='Actual DMA bound post-transfer callsite')
    test('wrong-bank',badbank=True,wanted='Actual DMA bound post-transfer callsite')
    for n in [0,255,257]:test('wrong-count-'+str(n),count=n,wanted='Actual completed DMA has256 data writes')
    for n in [0,127,255]:test('wrong-image-'+str(n),flip=n,wanted='Actual completed DMA hardware equals complete source page')
    test('late-start',scan=0,mask=30,wanted='Actual DMA starts inside vblank or disabled rendering')
    test('late-end',mask=30,end=0,wanted='Actual DMA completes inside vblank or disabled rendering')
    test('wrong-return-bank-defers',defer=True)
    (a.output/'cases.json').write_text(json.dumps(cases,indent=2)+'\n',encoding='utf-8')
    result=dict(passed=True,native_run=False,actual_generated_guard_executed=True,cases=len(cases),
                intentional_rejections=sum(z['expected_failure'] is not None for z in cases),
                guard=guard,all_full256_byte_equality_count_and_safe_timing_predicates_retained=True,
                no_runtime_callback_registration=True,wrong_return_bank_defers=True,
                script_sha256=sha(a.fixture/'run.lua'),cases_sha256=sha(a.output/'cases.json'),tool_sha256=sha(__file__),
                limits='Synthetic Lua-only observer checks, no native outcome. Fresh exact8byte postDMA protocol; no ROM or hardware equality mask.')
    (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
