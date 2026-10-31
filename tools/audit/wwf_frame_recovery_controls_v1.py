"""Native CF14 threshold/grapple outputs, true selected source, NES flags."""
from pathlib import Path
import collections,copy,itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from verify_native_relocation import NesMPU
import wwf_c2_relocation_model_v2 as M
M.MPU=M.T.MPU=M.T.W.MPU=NesMPU
T=M.T;L=R/'build/wwf-frame-recovery-v2';O=R/'build/wwf-frame-recovery-controls-v1'

def clone(b):
    d=copy.copy(b);d.mem=bytearray(b.mem);d.shadow=bytearray(b.shadow);d.ram=M.StateProjection(d)
    d.io=dict(b.io);d.apu=[];d.writes=[];d.canonical_writes=[];d.callbacks=[];d.state_events=[];d.pointer_pending={};d.cpu=None;d.hook=None
    d.executed=set();d.pc_by_context=collections.defaultdict(set);d.reads_by_context=collections.defaultdict(set);d.writes_by_context=collections.defaultdict(set);d.handler_hits=collections.Counter();d.helper_reads=collections.Counter();d.zpx_witness=collections.defaultdict(set)
    return d

def main():
    assert not O.exists();O.mkdir();q=dict(passed=False,isolated_CPU_lab=True,CPU='NesMPU binary arithmetic with D retained',native_host=False,no_host_allocation=True,groups={});p=json.loads((L/'build-proof.json').read_text());prior=json.loads((T.L/'build-proof.json').read_text());prg=T.W.W.raw();templates={};count=0
    for path,h in p['bindings'].items():assert T.sha(path)==h,path
    try:
        for ch in range(6):
            a=M.OracleBus(prg,bytes(2048),prior,None);a.labels={**a.labels,'WfFrameRecovery':0xcf14,'WfIntroFill':0xb14d}
            for at,v in [(0x2b,ch),(0x2a,(ch+1)%6),(0x82,55),(0x100,1),(0x12b,255)]:a.ram[at]=v
            n=NesMPU(memory=a,pc=0x8039);n.step();n.step();n.pc=0xa0c3;n.step();n.step()
            M.old_call(a,'WfInitDescriptors');T.W.call(a,0x8044,limit=100000)
            b=M.C2Bus(prg,bytes(2048),prior,'relocated');b.mem[0xc000:0xe000]=(L/'c2.bin').read_bytes();b.labels={**b.labels,**p['labels']};M.call(b,'WfHostCold',a=ch,x=(ch+1)%6,y=55)
            # Actual original intro producer establishes health, no byte preload.
            for _ in range(63):
                M.old_call(a,'WfIntroFill');M.call(b,'WfIntroFillCore')
            assert a.ram[0x79]==b.shadow[0x79]==200 and a.ram[0x7a]==b.shadow[0x7a]==200 and a.ram[0x78]==b.shadow[0x78]==63
            templates[ch]=(bytes(a.ram),clone(b))
        def pair(ch,fields,flags):
            nonlocal count
            ram,base=templates[ch];a=M.OracleBus(prg,ram,prior,None);a.labels={**a.labels,'WfFrameRecovery':0xcf14};b=clone(base)
            for at,v in fields.items():a.ram[at]=v;b.ram[at]=v
            ca=M.old_call(a,'WfFrameRecovery',a=0x53,x=1,y=0x7b,flags=flags);cb=M.call(b,'WfFrameRecovery',a=0x53,x=1,y=0x7b,flags=flags)
            assert T.cpu_state(ca)==T.cpu_state(cb),('CF14 actual return',ch,fields,flags,T.cpu_state(ca),T.cpu_state(cb))
            assert all(a.ram[i]==b.shadow[i]for i in range(2048)if not 0x100<=i<0x200),('CF14 projected state',ch,fields,flags)
            assert[e for e in a.state_events if e is not None]==[e for e in b.state_events if e is not None],('CF14 ordered writes',ch,fields,flags)
            assert a.io==b.io and a.apu==b.apu and a.bank==b.bank,('CF14 actual audio/map',ch,fields,flags)
            assert b.mem[:0x100]==b.host_seed[:0x100]and b.mem[0x200:0x800]==b.host_seed[0x200:]
            count+=1
        start=count
        for bits,hp,video,decay in itertools.product(range(64),[0,1,199,200,229,230,255],[0,15,16,31,32],[0,1,35]):
            pair(5,{0x79:hp,0x7a:200,0x8d:video,0x8e:decay,0x8f:decay},0x30|(bits&15)|((bits&48)<<2))
        q['groups']['recovery_thresholds']=dict(passed=True,cases=count-start)
        start=count
        for ch,bits,walk,face in itertools.product(range(6),range(64),[3,4],[0,1]):
            pair(ch,{0x3c:walk,0x3d:0,0x32:0,0x33:0,0x85:255,0xc9:12,0xca:12,0xc0:0,0xc1:0,0x3a:face,0x3b:face^1,0x2c:128,0x2d:140,0x2e:180,0x2f:180},0x30|(bits&15)|((bits&48)<<2))
        q['groups']['grapple_source_stats']=dict(passed=True,cases=count-start,characters=6)
        start=count
        for bits,actor,hp,already in itertools.product(range(64),[0,1],[230,255],[0,1]):
            pair(5,{0x79+actor:hp,0xa2+(actor^1):already,0x71:actor},0x30|(bits&15)|((bits&48)<<2))
        q['groups']['knockdown_and_repeat']=dict(passed=True,cases=count-start)
        q.update(passed=True,total_pairs=count,actual_intro_source_updates=6*63,limits=['Declared direct source-state threshold contexts; no natural SMB enemy or shared native lifecycle claim.','Complete returnedAXYP/SP, exact original ordered selected-state changes, native audio/map outcomes and scoped scratch are compared.','Native contact/ring/audio remaining boundaries still use the declared original donor environment.'])
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc());raise
    finally:
        paths=[Path(__file__),Path(M.__file__),R/'tools/audit/verify_native_relocation.py',L/'build-proof.json',L/'recovery.s',L/'host.s',L/'vm.bin',L/'c2.bin',T.W.W.ROM]
        q['bindings']={str(path.resolve()):T.sha(path)for path in paths};T.save(O/'controls.json',q);print(json.dumps({k:q.get(k)for k in ['passed','total_pairs','groups','error']}))
if __name__=='__main__':main()
