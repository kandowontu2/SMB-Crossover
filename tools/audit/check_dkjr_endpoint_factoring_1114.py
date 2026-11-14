"""Finite carry contract for the exact old/new endpoint context predicates."""
import ast
from hashlib import sha256
import json
from pathlib import Path

import check_dkjr_indirect_funding_1114 as CPU
import measure_dkjr_floor_entry_fit_1114 as Fit

E=Fit.Endpoint;W=Fit.Indirect.G.W


def run():
    proposal,model=Fit.measure(include_model=True);defs,_=E.sources()
    data=Path(E.Original.__file__).read_bytes();assert sha256(data).hexdigest()==E.ORIGINAL_SHA
    tree=ast.parse(data);fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='measure')
    texts={n.targets[0].id:ast.literal_eval(n.value)for n in fn.body
        if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Name)
        and n.targets[0].id in ('entry','floor')}
    original=E.H.T.assemble(defs+texts['entry']+texts['floor'],
        dict(ENTRY=(0x9000,256),FLOOR=(0x9200,256),PREDICATE=(0x9400,256),VISIBLE=(0x9600,256),STATIC=(0x9800,256)))
    old,new=CPU.models(model,proposal)
    for name,pc in (('ENTRY',0x9000),('FLOOR',0x9200),('PREDICATE',0x9400),('VISIBLE',0x9600),('STATIC',0x9800)):
        old[pc:pc+len(original['images'][name])]=original['images'][name]
    b=W.Symbols.bundle()
    fields={W.address(b,n):v for n,v in dict(OperMode=1,OperMode_Task=3,
        GameEngineSubroutine=8,TimerControl=0,DisableCollisionDet=0,JumpspringAnimCtrl=0,
        SwimmingFlag=0,PlayerEntranceCtrl=1,Player_State=2,Player_Y_HighPos=1).items()}
    fields.update({0xc04a:1,0xc068:0})
    cases=[(None,None,p)for p in range(256)]
    cases.extend((at,value,0x61)for at in fields for value in range(256))
    digest=sha256();accepted=0
    for at,value,p in cases:
        outputs=[]
        for index,memory in enumerate((old,new)):
            for address,initial in fields.items():memory[address]=initial
            if at is not None:memory[at]=value
            cpu=CPU.N.NesMPU(memory=memory,pc=(0x9400,model['proposed']['symbols']['MeasuredForcedDrop'])[index])
            cpu.a,cpu.x,cpu.y,cpu.p,cpu.sp=85,37,91,p,224;cpu.stPushWord(0x5aff)
            for _ in range(100):
                if(cpu.pc,cpu.sp)==(0x5b00,224):break
                cpu.step()
            else:raise AssertionError('Predicate CPU bound')
            assert (cpu.x,cpu.y)==(37,91)
            assert all(memory[address]==(value if address==at else initial)for address,initial in fields.items())
            outputs.append(bool(cpu.p&1))
        assert outputs[0]==outputs[1],(at,value,p,outputs)
        digest.update(bytes(outputs));accepted+=outputs[0]
    return dict(passed=True,cases=len(cases),all256_incoming_P=True,
        each12_context_fields_all256_values=True,accepted_cases=accepted,
        carry_equivalence_SHA256=digest.hexdigest(),all_context_fields_unchanged=True,
        predicate_callers_consume_only_C='Entry immediately BCC; draw-admission tail-jumps to predicate and body guard immediately BCS. Floor context immediately BCC.',
        AXYP_claim='Predicate A/N/Z differ for some rejected compound states; callers use only carry. Floor saves/restores AXYP and returns Cset.',
        ROM_composed=False,outputs_written=0,scope='Detached predicate factoring equivalence, not gameplay or resource admission.')


if __name__=='__main__':print('DKJR_ENDPOINT_FACTORING '+json.dumps(run(),separators=(',',':')),flush=True)
