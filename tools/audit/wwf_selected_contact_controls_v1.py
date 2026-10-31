"""Genuine selected contact/depth/RNG versus original native instructions."""
from pathlib import Path
import itertools,json,sys,traceback
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import wwf_c2_relocation_model_v2 as M
T=M.T;L=R/'build/wwf-selected-contact-v1';O=R/'build/wwf-selected-contact-controls-v1'

def main():
    assert not O.exists();O.mkdir();q=dict(passed=False,isolated_CPU_lab=True,native_host=False,no_host_allocation=True,checks={})
    p=json.loads((L/'build-proof.json').read_text());prior=json.loads((T.L/'build-proof.json').read_text());prg=T.W.W.raw()
    for path,h in p['bindings'].items():assert T.sha(path)==h,path
    count=0;audio=0
    try:
        def run(name,original,fields,actor,flags):
            nonlocal count,audio
            a=M.OracleBus(prg,bytes(2048),prior,None);a.labels={**a.labels,name:original}
            b=M.C2Bus(prg,bytes(2048),prior,'relocated');b.mem[0xc000:0xe000]=(L/'c2.bin').read_bytes();b.labels={**b.labels,**p['labels']}
            # The actual constructor replaces any initialized snapshot fixture.
            for i,v in [(0x2b,5),(0x2a,0),(0x82,55),(0x100,1),(0x12b,255)]:a.ram[i]=v
            M.old_call(a,'WfInitDescriptors');T.W.call(a,0x8044,limit=100000);M.call(b,'WfHostCold',a=5,x=0,y=55)
            for i,v in fields.items():a.ram[i]=v;b.ram[i]=v
            start=[len(a.state_events),len(b.state_events)];apu=[len(a.apu),len(b.apu)]
            ca=M.old_call(a,name,a=0x5a,x=actor,y=0x7d,flags=flags);cb=M.call(b,name,a=0x5a,x=actor,y=0x7d,flags=flags)
            assert T.cpu_state(ca)==T.cpu_state(cb),('Selected callback AXYP/SP',name,fields,actor,flags,T.cpu_state(ca),T.cpu_state(cb))
            assert all(a.ram[i]==b.shadow[i]for i in range(2048)if not 0x100<=i<0x200),('Selected callback source state',name,fields,actor,flags)
            expected=[e for e in a.state_events[start[0]:]if e is not None];actual=[e for e in b.state_events[start[1]:]if e is not None]
            assert expected==actual,('Selected callback ordered writes',name,fields,actor,flags,expected,actual)
            assert a.apu[apu[0]:]==b.apu[apu[1]:]and a.io==b.io and a.bank==b.bank,('Genuine audio side effects',name,fields,actor,flags)
            assert b.mem[:0x100]==b.host_seed[:0x100]and b.mem[0x200:0x800]==b.host_seed[0x200:]
            audio+=bool(b.apu[apu[1]:]);count+=1
        for bits in range(64):
            flags=0x30|(bits&15)|((bits&48)<<2)
            for seed in [0,1,127,128,255]:run('WfCbRandom',0xce17,{0x82:seed,0x83:seed^0x55,0x84:seed^0xaa},0,flags)
        q['checks']['RNG']=dict(passed=True,cases=count,all64flags=True)
        before=count
        for bits,actor,dy in itertools.product(range(64),[0,1],[-4,-3,0,3,4]):
            flags=0x30|(bits&15)|((bits&48)<<2);run('WfCbActorDepthProbe',0xcd02,{0x2e:180,0x2f:180+dy},actor,flags)
        q['checks']['depth']=dict(passed=True,cases=count-before,all64flags=True)
        before=count
        for bits,actor,force,collision_kind,reverse,x1,y1 in itertools.product(range(64),[0,1],[0,1,4],[0,1],[0,1],[120,133,180],[180,200]):
            flags=0x30|(bits&15)|((bits&48)<<2)
            fields={0x2c:128,0x2d:x1,0x2e:180,0x2f:y1,0x89:force,0x8a:collision_kind,0x3a:0,0x3b:reverse,0x79:180,0x7a:180,0x8e:0,0x8f:0}
            run('WfCbActorContact',0xcd25,fields,actor,flags)
        q['checks']['contact']=dict(passed=True,cases=count-before,all64flags=True,actual_audio_cases=audio)
        q.update(passed=True,total_cases=count,remaining_semantics=['No SMB enemy proxy/terrain API is installed; this is genuine selected original wrestler contact.','Native sound callback remains an oracle but actual nested sound entry executes and ordered APU/mapper effects are compared.','Nested callback trace SP metadata from the previous fixed-offset observer is outside this receipt; complete actual publicAXYP/SP, scratch, ordered source writes and audio results are exact.'])
    except Exception as e:q.update(error=repr(e),traceback=traceback.format_exc());raise
    finally:
        q['bindings']={str(path.resolve()):T.sha(path)for path in [Path(__file__),Path(M.__file__),L/'build-proof.json',L/'contact.s',L/'aliases.s',L/'vm.bin',L/'c2.bin',T.W.W.ROM]};T.save(O/'controls.json',q);print(json.dumps({k:q.get(k)for k in ['passed','total_cases','checks','error']}))
if __name__=='__main__':main()
